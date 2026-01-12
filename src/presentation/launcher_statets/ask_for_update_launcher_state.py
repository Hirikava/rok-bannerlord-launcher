import imgui

from src.domain.launcher_context import LauncherContext
from src.presentation.launcher_statets.launcher_state_base import LauncherStateBase


class AskForUpdateLauncherState(LauncherStateBase):
    launcher_context: LauncherContext

    def __init__(
            self,
            launcher_context: LauncherContext):
        self.launcher_context = launcher_context

    async def on_init(self):
        pass

    async def run_internal(self):
        imgui.text("You need to update following packages:")
        for package_version in self.launcher_context.packages_to_update:
            imgui.text(f"{package_version.package_name} - {package_version.package_version}")

        if imgui.button("Update"):
            self.launcher_context.allow_update()

        if imgui.button("Exit"):
            self.launcher_context.exit()
