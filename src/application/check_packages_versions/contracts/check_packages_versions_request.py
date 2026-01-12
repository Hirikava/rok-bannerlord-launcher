import typing

from mediatr import GenericQuery

from src.application.check_packages_versions.contracts.check_packages_versions_response import \
    CheckPackagesVersionsResponseInternal


@typing.final
class CheckPackagesVersionsRequestInternal(GenericQuery[CheckPackagesVersionsResponseInternal]):
    packages_names: list[str]

    def __init__(
            self,
            packages_names: list[str]):
        self.packages_names = packages_names
