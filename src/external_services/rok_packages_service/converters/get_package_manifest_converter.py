from rok_bannerlord_package_tools.models.file_info import FileInfo
from rok_bannerlord_package_tools.models.manifest import Manifest
from rok_bannerlord_proto.proto_vendor.rok_bannerlord_packages import GetPackageManifestQueryResponse, \
    ManifestFileInfoDto


class GetPackageManifestConverter:
    @staticmethod
    def to_internal(grpc_response: GetPackageManifestQueryResponse) -> Manifest:
        file_infos = [GetPackageManifestConverter.to_internal_file_info(x) for x in
                      grpc_response.package_manifest.file_infos]

        manifest = Manifest(files=file_infos)

        return manifest

    @staticmethod
    def to_internal_file_info(file_info_dto: ManifestFileInfoDto):
        file_info = FileInfo(
            relative_file_path=file_info_dto.file_path,
            file_size=file_info_dto.file_size,
            file_md5_hash=file_info_dto.file_md5_hash)

        return file_info
