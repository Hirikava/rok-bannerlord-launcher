import asyncio

import imgui
import mediatr

from src.application.check_packages_versions.contracts.check_packages_versions_request import \
    CheckPackagesVersionsRequestInternal
from src.application.check_packages_versions.contracts.check_packages_versions_response import \
    CheckPackagesVersionsResponseInternal
from src.domain.launcher_context import LauncherContext
from src.presentation.launcher_statets.launcher_state_base import LauncherStateBase


class CheckPackagesVersionsLauncherState(LauncherStateBase):
    launcher_context: LauncherContext
    mediator: mediatr.Mediator

    check_package_update_task: asyncio.Task

    def __init__(
            self,
            launcher_context: LauncherContext,
            mediator: mediatr.Mediator):
        self.launcher_context = launcher_context
        self.mediator = mediator

    async def on_init(self):
        self.check_package_update_task = asyncio.create_task(self.__check_packages_internal())

    async def run_internal(self):
        if self.check_package_update_task.done() is False:
            imgui.text("Checking for updates...")
            return

        self.reset()

        if self.check_package_update_task.exception() is not None:
            raise self.check_package_update_task.exception()

    async def __check_packages_internal(self):
        internal_request = CheckPackagesVersionsRequestInternal(
            packages_names=self.launcher_context.all_packages_names,
            user_api_key=self.launcher_context.user_api_key)

        internal_response: CheckPackagesVersionsResponseInternal = await self.mediator.send_async(internal_request)

        self.launcher_context.set_packages_to_updated(internal_response.packages_to_update)
