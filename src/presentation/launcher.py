import asyncio
import os

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from rok_bannerlord_package_tools.files_utils import FilesUtils
from rok_bannerlord_package_tools.manifest_utils import ManifestUtils
from rok_bannerlord_package_tools.models.file_info import FileInfo

from src.domain.package_version import PackageVersion
from src.external_services.rok_packages_service.rok_packages_service import RokPackagesService
from src.infrastructure.repositories.local_version_repository.local_version_repository import LocalVersionRepository

ROK_BANNERLORD_PACKAGE_NAME = "rok-bannerlord"
TESSERACT_OCR_PACKAGE_NAME = "tesseract-ocr"
ADB_TOOLS_PACKAGE_NAME = "adb-platform-tools"
ABOBA_PACKAGE_NAME = "aboba"

PACKAGES_TO_UPDATE = [
    ABOBA_PACKAGE_NAME]


class FileDownloadingInfo:
    file_total_bytes: int
    file_downloaded_bytes: int
    file_name: str

    def __init__(
            self,
            file_total_bytes: int,
            file_downloaded_bytes: int,
            file_name: str):
        self.file_total_bytes = file_total_bytes
        self.file_downloaded_bytes = file_downloaded_bytes
        self.file_name = file_name


class UpdatePackageProcessInfo:
    files_left: int
    total_bytes_read: int
    total_bytes: int
    file_downloading_infos: list[FileDownloadingInfo]

    def __init__(
            self,
            files_left: int,
            total_bytes_read: int,
            total_bytes: int,
            max_downloading_processes: int):
        self.files_left = files_left
        self.total_bytes_read = total_bytes_read
        self.total_bytes = total_bytes
        self.file_downloading_infos = list()
        for i in range(max_downloading_processes):
            self.file_downloading_infos.append(None)


class RokBannerlordLauncher:
    rok_packages_service: RokPackagesService
    local_version_repository: LocalVersionRepository

    def __init__(
            self,
            pm_server_host: str,
            pm_server_port: int,
            user_api_key: str):

        self.rok_packages_service = RokPackagesService(
            host=pm_server_host,
            port=pm_server_port,
            user_api_key=user_api_key)

        self.local_version_storage = LocalVersionRepository()

    async def check_packages_versions(self) -> list[PackageVersion]:
        packages_to_update = list()
        for package_name in PACKAGES_TO_UPDATE:
            server_version: PackageVersion = await self.rok_packages_service.get_latest_package_version(
                package_name=package_name)
            local_version: PackageVersion = await self.local_version_storage.get_package_current_version(
                package_name=package_name)

            if local_version is None:
                packages_to_update.append(server_version)
                continue

            if (local_version.package_version != server_version.package_version and local_version.package_publish_time
                    < server_version.package_publish_time):
                packages_to_update.append(server_version)

        return packages_to_update

    async def update_package(
            self,
            package_version: PackageVersion,
            max_parallel_downloads: int = 4) -> AsyncGenerator[UpdatePackageProcessInfo, Any]:

        local_manifest = await FilesUtils.create_manifest_from_directory_async(
            directory_path=package_version.package_name)

        server_manifest = await self.rok_packages_service.get_package_manifest(
            package_name=package_version.package_name,
            package_version=package_version.package_version)

        manifest_diff = ManifestUtils.create_manifest_diff(
            target_manifest=server_manifest,
            existing_manifest=local_manifest)

        files_to_download = set(manifest_diff.new_files).union(set(manifest_diff.updated_files))
        files_to_download = list(files_to_download)
        files_to_delete = manifest_diff.removed_files

        total_files_count = len(files_to_download)
        total_bytes = sum([x.file_size for x in files_to_download])
        current_total_bytes_read = 0

        update_info = UpdatePackageProcessInfo(
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

        await self.local_version_storage.save_package_current_version(package_version)

    async def __start_download_worker(
            self,
            package_version: PackageVersion,
            package_file_infos: list[FileInfo],
            update_info: UpdatePackageProcessInfo,
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

            update_info.file_downloading_infos[index] = FileDownloadingInfo(
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
