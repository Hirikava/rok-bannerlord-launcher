import typing

import punq

from src.application.check_packages_versions.check_packages_versions_handler import CheckPackagesVersionsHandlerInternal
from src.application.update_package.update_package_handler import UpdatePackageHandlerInternal


@typing.final
class ApplicationRegistrar:
    @staticmethod
    def configure(container: punq.Container):
        container.register(UpdatePackageHandlerInternal)
        container.register(CheckPackagesVersionsHandlerInternal)
