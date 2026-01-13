import os
import subprocess
from pathlib import Path

import imgui

from src.domain.launcher_context import LauncherContext
from src.presentation.launcher_statets.launcher_state_base import LauncherStateBase


class ReadyForLaunchLauncherState(LauncherStateBase):
    launcher_context: LauncherContext

    def __init__(
            self,
            launcher_context: LauncherContext):
        self.launcher_context = launcher_context

    async def on_init(self):
        pass

    async def run_internal(self):
        imgui.text("Everything is up to date.")
        if imgui.button("Run RokBannerlord"):
            tesseract_path = Path.cwd() / "tesseract-ocr"
            adb_path = Path.cwd() / "adb-platform-tools"

            rokb_exe_path = Path.cwd() / "rok-bannerlord" / "rok_bannerlord_client.exe"
            os.environ["PATH"] += os.pathsep + tesseract_path.__str__()
            os.environ["PATH"] += os.pathsep + adb_path.__str__()

            os.environ["ROKB_WORKDIR"] = Path.cwd().__str__()
            os.environ["ROKB_ASSETSDIR"] = (Path.cwd() / "rok-bannerlord" / "assets").__str__()

            process = subprocess.Popen(
                [rokb_exe_path.__str__()],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                close_fds=True,
                creationflags=subprocess.DETACHED_PROCESS)

            self.launcher_context.exit()

        imgui.same_line()

        if imgui.button("Exit"):
            self.launcher_context.exit()
