from typing import AsyncIterator

from src.application.update_package.contracts.update_package_info import UpdatePackageProcessInfoInternal


class UpdatePackageResponseInternal:
    update_package_stream: AsyncIterator[UpdatePackageProcessInfoInternal]

    def __init__(
            self,
            update_package_stream: AsyncIterator[UpdatePackageProcessInfoInternal]):
        self.update_package_stream = update_package_stream
