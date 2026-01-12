from src.domain.package_version import PackageVersion


class CheckPackagesVersionsResponseInternal:
    packages_to_update: list[PackageVersion]

    def __init__(
            self,
            packages_to_update: list[PackageVersion]):
        self.packages_to_update = packages_to_update

