import typing

import punq

from src.domain.launcher_context import LauncherContext
from src.presentation.launcher_statets.ask_for_update_launcher_state import AskForUpdateLauncherState
from src.presentation.launcher_statets.check_packages_versions_launcher_state import CheckPackagesVersionsLauncherState
from src.presentation.launcher_statets.enter_api_key_launcher_state import EnterApiKeyLauncherState
from src.presentation.launcher_statets.ready_for_launch_launcher_state import ReadyForLaunchLauncherState
from src.presentation.launcher_statets.update_packages_launcher_state import UpdatePackagesLauncherState


@typing.final
class PresentationRegistrar:

    @staticmethod
    def configure(container: punq.Container):
        container.register(LauncherContext, instance=LauncherContext())

        container.register(AskForUpdateLauncherState)
        container.register(CheckPackagesVersionsLauncherState)
        container.register(EnterApiKeyLauncherState)
        container.register(ReadyForLaunchLauncherState)
        container.register(UpdatePackagesLauncherState)
