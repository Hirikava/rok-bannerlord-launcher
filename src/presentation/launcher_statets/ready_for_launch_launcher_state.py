import os
import subprocess
from pathlib import Path

import imgui

from src.domain.launcher_context import LauncherContext
from src.presentation.launcher_statets.launcher_state_base import LauncherStateBase
from src.utils.system_utils import SystemUtils


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
            # TODO TO INTERNAL COMMAND
            adb_path = Path.cwd() / "adb-platform-tools"

            rokb_exe_path = Path.cwd() / "rok-bannerlord-client" / "rok_bannerlord_client.exe"
            rokb_server_address = self.__get_rokb_server_addr()

            os.environ["PATH"] += os.pathsep + adb_path.__str__()
            os.environ["ROKB_WORKDIR"] = Path.cwd().__str__()
            os.environ["ROKB_ASSETSDIR"] = (Path.cwd() / "rok-bannerlord-agent" / "assets").__str__()
            os.environ["ROKB_APP_VERSION"] = "1.0.0"
            os.environ["ROKB_CLIENT_PORT"] = str(SystemUtils.get_free_port())
            os.environ["ROKB_CLIENT_HOST"] = "127.0.0.1"
            os.environ["ROKB_EXE_PATH"] = str(rokb_exe_path)
            os.environ["ROKB_LOCAL_DATA_DIR"] = str(self.__get_path_to_local_app_data())
            os.environ["ROKB_RUN_MODE"] = "BINARY"
            os.environ["ROKB_SERVER_API_KEY"] = self.launcher_context.user_api_key
            os.environ["ROKB_SERVER_CONNECTION_PORT"] = "7272"
            os.environ["ROKB_SERVER_CONNECTION_ADDR"] = rokb_server_address

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

    def __get_path_to_local_app_data(self) -> Path:
        local_dir = Path(os.getenv('LOCALAPPDATA')) / "RokBannerlord"
        local_dir.mkdir(parents=True, exist_ok=True)

        return local_dir

    def __get_rokb_server_addr(self):
        is_stage = os.getenv('ROKB_STAGE_ENV', default=None)
        if is_stage is None:
            return "rokbannerlord.ru"
        return "127.0.0.1"
