import asyncio
import typing

import imgui
from mediatr import Mediator

from src.application.update_package.contracts.update_package_info import UpdatePackageProcessInfoInternal
from src.application.update_package.contracts.update_package_request import UpdatePackageRequestInternal
from src.application.update_package.contracts.update_package_response import UpdatePackageResponseInternal
from src.domain.launcher_context import LauncherContext
from src.domain.package_version import PackageVersion
from src.presentation.launcher_statets.launcher_state_base import LauncherStateBase
from src.utils.format_utils import FormatUtils


@typing.final
class UpdatePackagesLauncherState(LauncherStateBase):
    launcher_context: LauncherContext
    mediatr: Mediator

    update_packages_task: asyncio.Task | None
    package_update_info: UpdatePackageProcessInfoInternal | None
    current_updating_package: PackageVersion | None

    def __init__(
            self,
            launcher_context: LauncherContext,
            mediatr: Mediator):
        self.launcher_context = launcher_context
        self.mediatr = mediatr

    def run_internal(self):
        if self.update_packages_task.done():
            if self.update_packages_task.exception() is not None:
                raise self.update_packages_task.exception()

        if self.current_updating_package is not None:
            imgui.text(f"Updating {self.current_updating_package.package_name} to version "
                       f" {self.current_updating_package.package_version}")
        else:
            return

        if self.package_update_info is not None:
            imgui.progress_bar(
                FormatUtils.get_progress(
                    self.package_update_info.total_bytes_read,
                    self.package_update_info.total_bytes),
                size=(200, 20),
                overlay="")
            imgui.same_line()
            imgui.text(
                f"{FormatUtils.format_bytes_auto(self.package_update_info.total_bytes_read)} / {FormatUtils.format_bytes_auto(
                    self.package_update_info.total_bytes)}")
            imgui.text(f"Files left: {self.package_update_info.files_left}")

            for file_update_info in self.package_update_info.file_downloading_infos:
                if file_update_info is None:
                    continue

                imgui.progress_bar(
                    FormatUtils.get_progress(
                        file_update_info.file_downloaded_bytes,
                        file_update_info.file_total_bytes),
                    size=(200, 20),
                    overlay="")
                imgui.same_line()
                imgui.text(f"{file_update_info.file_name}")
        else:
            imgui.text(f"Gathering manifest for {self.current_updating_package.package_name}")

    async def on_init(self):
        self.update_packages_task = asyncio.create_task(self.__update_packages_internal())

    async def __update_packages_internal(self):
        self.package_update_info = None
        self.current_updating_package = None

        for package_to_update in self.launcher_context.packages_to_update:
            self.current_updating_package = package_to_update

            internal_request = UpdatePackageRequestInternal(package_version=package_to_update, max_parallel_downloads=4)

            internal_response: UpdatePackageResponseInternal = await self.mediatr.send_async(internal_request)

            async for update_info in internal_response.update_package_stream:
                self.package_update_info = update_info

            self.launcher_context.set_package_updated(package_to_update)

        self.reset()
