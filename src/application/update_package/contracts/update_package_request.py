from mediatr import GenericQuery

from src.application.update_package.contracts.update_package_response import UpdatePackageResponseInternal
from src.domain.package_version import PackageVersion


class UpdatePackageRequestInternal(GenericQuery[UpdatePackageResponseInternal]):
    package_version: PackageVersion
    max_parallel_downloads: int

    def __init__(
            self,
            package_version: PackageVersion,
            max_parallel_downloads: int):
        self.package_version = package_version
        self.max_parallel_downloads = max_parallel_downloads
