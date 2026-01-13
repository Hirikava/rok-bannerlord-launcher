import asyncio
import os
import typing
from pathlib import Path

from mediatr import Mediator
from rok_bannerlord_package_tools.files_utils import FilesUtils
from rok_bannerlord_package_tools.manifest_utils import ManifestUtils
from rok_bannerlord_package_tools.models.file_info import FileInfo
from rok_bannerlord_package_tools.models.manifest_diff import ManifestsDiff

from src.application.update_package.contracts.file_downloading_info import FileDownloadingInfoInternal
from src.application.update_package.contracts.update_package_info import UpdatePackageProcessInfoInternal
from src.application.update_package.contracts.update_package_request import UpdatePackageRequestInternal
from src.application.update_package.contracts.update_package_response import UpdatePackageResponseInternal
from src.domain.package_version import PackageVersion
from src.external_services.rok_packages_service.rok_package_service_factory import RokPackageServiceFactory
from src.external_services.rok_packages_service.rok_packages_service import RokPackagesService
from src.infrastructure.repositories.local_version_repository.local_version_repository import LocalVersionRepository


@typing.final
@Mediator.handler
class UpdatePackageHandlerInternal:
    rok_packages_service_factory: RokPackageServiceFactory
    local_version_repository: LocalVersionRepository

    rok_packages_service: RokPackagesService

    def __init__(
            self,
            rok_packages_service_factory: RokPackageServiceFactory,
            local_version_repository: LocalVersionRepository):
        self.rok_packages_service_factory = rok_packages_service_factory
        self.local_version_repository = local_version_repository

    async def handle(
            self,
            request: UpdatePackageRequestInternal) -> UpdatePackageResponseInternal:
        self.rok_packages_service = self.rok_packages_service_factory.create(request.user_api_key)

        local_manifest = await FilesUtils.create_manifest_from_directory_async(
            directory_path=request.package_version.package_name)

        server_manifest = await self.rok_packages_service.get_package_manifest(
            package_name=request.package_version.package_name,
            package_version=request.package_version.package_version)

        manifest_diff = ManifestUtils.create_manifest_diff(
            target_manifest=server_manifest,
            existing_manifest=local_manifest)

        generator = self.__update_package_internal_async(
            manifest_diff,
            request.package_version,
            request.max_parallel_downloads)

        internal_response = UpdatePackageResponseInternal(generator)

        return internal_response

    async def __update_package_internal_async(
            self,
            manifest_diff: ManifestsDiff,
            package_version: PackageVersion,
            max_parallel_downloads: int) -> typing.AsyncIterator[UpdatePackageProcessInfoInternal]:
        files_to_download = set(manifest_diff.new_files).union(set(manifest_diff.updated_files))
        files_to_download = list(files_to_download)
        files_to_delete = manifest_diff.removed_files

        total_files_count = len(files_to_download)
        total_bytes = sum([x.file_size for x in files_to_download])
        current_total_bytes_read = 0

        update_info = UpdatePackageProcessInfoInternal(
            total_files_count,
            current_total_bytes_read,
            total_bytes,
            max_parallel_downloads)

        update_tasks = [asyncio.create_task(self.__start_download_worker(
            package_version=package_version,
            package_file_infos=files_to_download,
            update_info=update_info,
            index=x)) for x in range(max_parallel_downloads)]

        completed_update_tasks = [x for x in update_tasks if not x.done()]

        while completed_update_tasks.__len__() > 0:
            await asyncio.sleep(2)
            yield update_info
            completed_update_tasks = [x for x in update_tasks if not x.done()]

        failed_tasks = [x for x in update_tasks if x.exception() is not None]
        if failed_tasks.__len__() != 0:
            raise Exception(
                f"Failed to update package {package_version.package_name} to version {package_version.package_version}")

        for file_to_delete in files_to_delete:
            full_path = Path.cwd() / package_version.package_name / file_to_delete.relative_file_path[1:]
            os.remove(full_path)

        await self.local_version_repository.save_package_current_version(package_version)

    async def __start_download_worker(
            self,
            package_version: PackageVersion,
            package_file_infos: list[FileInfo],
            update_info: UpdatePackageProcessInfoInternal,
            index: int):

        while package_file_infos.__len__() > 0:
            file_to_download = package_file_infos.pop()

            file_path = Path.cwd() / package_version.package_name / file_to_download.relative_file_path[1:]

            if file_to_download.file_size == 0:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path.__str__(), 'w'):
                    pass

                update_info.files_left -= 1
                continue

            update_info.file_downloading_infos[index] = FileDownloadingInfoInternal(
                file_total_bytes=file_to_download.file_size,
                file_downloaded_bytes=0,
                file_name=file_to_download.relative_file_path)

            content_stream = await self.rok_packages_service.download_file(
                package_name=package_version.package_name,
                package_version=package_version.package_version,
                file_path=file_to_download.relative_file_path)

            file_path = Path.cwd() / package_version.package_name / file_to_download.relative_file_path[1:]

            download_file_gen = FilesUtils.write_file_async(
                file_path=file_path,
                target_size=file_to_download.file_size,
                target_md5_hash=file_to_download.file_md5_hash,
                content_stream=content_stream)

            async for file_bytes_read in download_file_gen:
                update_info.file_downloading_infos[index].file_downloaded_bytes = file_bytes_read

            update_info.total_bytes_read += file_to_download.file_size
            update_info.files_left -= 1
