from collections.abc import AsyncGenerator
from typing import Any

from grpclib.client import Channel
from rok_bannerlord_package_tools.models.manifest import Manifest
from rok_bannerlord_proto.proto_vendor.rok_bannerlord_packages import RokBannerlordPackagesServiceStub, \
    GetLatestPackageVersionQuery, GetPackageManifestQuery, DownloadFileQuery

from src.domain.package_version import PackageVersion
from src.external_services.rok_packages_service.converters.download_file_converter import DownloadFileConverter
from src.external_services.rok_packages_service.converters.get_package_manifest_converter import \
    GetPackageManifestConverter

from rok_bannerlord_proto.well_known_headers import USER_API_KEY_HEADER


class RokPackagesService:
    rok_packages_client: RokBannerlordPackagesServiceStub

    def __init__(
            self,
            host: str,
            port: int,
            user_api_key: str):
        channel = Channel(host=host, port=port)
        self.rok_packages_client = RokBannerlordPackagesServiceStub(
            channel,
            # TODO move api key names into one package
            metadata=[
                (USER_API_KEY_HEADER, user_api_key)
            ])

    async def get_latest_package_version(
            self,
            package_name: str) -> PackageVersion:
        grpc_request = GetLatestPackageVersionQuery(package_name=package_name)

        grpc_response = await self.rok_packages_client.get_latest_package_version(grpc_request)

        package_version = PackageVersion(
            package_name=package_name,
            package_version=grpc_response.package_version,
            package_publish_time=grpc_response.publish_timestamp)

        return package_version

    async def get_package_manifest(
            self,
            package_name: str,
            package_version: str) -> Manifest:
        grpc_request = GetPackageManifestQuery(package_name=package_name, package_version=package_version)

        grpc_response = await self.rok_packages_client.get_package_manifest(grpc_request)

        manifest = GetPackageManifestConverter.to_internal(grpc_response)

        return manifest

    async def download_file(
            self,
            package_name: str,
            package_version: str,
            file_path: str) -> AsyncGenerator[bytes, Any]:
        grpc_request = DownloadFileQuery(
            package_name=package_name,
            package_version=package_version,
            file_relative_path=file_path)

        grpc_response = self.rok_packages_client.download_file(grpc_request)

        response = DownloadFileConverter.to_internal(grpc_response)

        return response
