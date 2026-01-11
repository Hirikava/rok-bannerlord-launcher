import asyncio
import enum
import os
import subprocess
import sys
from pathlib import Path

import OpenGL.GL as gl
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer

from src.domain.launcher_state import LauncherState
from src.domain.package_version import PackageVersion
from src.presentation.launcher import UpdatePackageProcessInfo, RokBannerlordLauncher


def impl_glfw_init():
    width, height = 600, 400
    window_name = "Rok Bannerlord Launcher"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        sys.exit(1)

    glfw.swap_interval(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(int(width), int(height), window_name, None, None)
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        sys.exit(1)

    return window


def format_bytes_auto(bytes_value: int | float) -> str:
    if bytes_value < 0:
        return "-"
    if bytes_value == 0:
        return "0 B"

    base = 1024
    units = ["B", "KB", "MB", "GB", "TB", "PB"]

    i = 0
    size = float(bytes_value)

    while size >= base and i < len(units) - 1:
        size /= base
        i += 1
    if i == 0 or size == int(size):
        return f"{int(size)} {units[i]}"
    else:
        return f"{size:.2f} {units[i]}"


def get_progress(
        current: int,
        total: int) -> float:
    if total == 0:
        return 1.0
    return current / total


class RokBannerlordLauncherApp:
    checking_for_update_task = None
    updating_task = None

    current_state: LauncherState = LauncherState.CHECKING_FOR_UPDATES
    packages_names: list[str] = []

    packages_to_update: list[PackageVersion]

    current_update_info: UpdatePackageProcessInfo = None
    packages_updated: int = 0
    current_package_updating: PackageVersion = None

    max_downloads: int = 4

    def __init__(
            self,
            host: str,
            port: int,
            user_api_key: str,
            packages_names: list[str],
            max_downloads: int):

        imgui.create_context()
        self.window = impl_glfw_init()
        self.impl = GlfwRenderer(self.window)
        self.launcher = RokBannerlordLauncher(
            host=host,
            port=port,
            user_api_key=user_api_key)
        self.max_downloads = min(max_downloads, 8)
        self.packages_names = packages_names

    async def checking_for_update(self):
        if self.checking_for_update_task is None:
            loop = asyncio.get_running_loop()
            self.checking_for_update_task = loop.create_task(self.launcher.check_packages_versions(self.packages_names))
        if self.checking_for_update_task.done():
            packages_to_update = self.checking_for_update_task.result()
            if len(packages_to_update) == 0:
                self.current_state = LauncherState.READY_TO_RUN
            else:
                self.packages_to_update = packages_to_update
                self.current_state = LauncherState.ASK_FOR_UPDATE
        else:
            imgui.text("Checking for updates")

    async def ask_for_update(self):
        imgui.text("You need to update following packages:")
        for package in self.packages_to_update:
            imgui.text(f"{package.package_name} - {package.package_version}")

        if imgui.button("Update"):
            self.current_state = LauncherState.UPDATING
        imgui.same_line()
        if imgui.button("Close"):
            self.current_state = LauncherState.EXIT

    async def update(self):
        if self.updating_task is None:
            self.updating_task = asyncio.create_task(self.__create_update_task())

        if self.updating_task.done():
            self.current_state = LauncherState.READY_TO_RUN
        else:
            if self.current_update_info is not None:
                imgui.text(f"Updating {self.current_package_updating.package_name} to version "
                           f" {self.current_package_updating.package_version}")
                imgui.progress_bar(
                    get_progress(
                        self.current_update_info.total_bytes_read,
                        self.current_update_info.total_bytes),
                    size=(200, 20),
                    overlay="")
                imgui.same_line()
                imgui.text(
                    f"{format_bytes_auto(self.current_update_info.total_bytes_read)} / {format_bytes_auto(
                        self.current_update_info.total_bytes)}")
                imgui.text(f"Files left: {self.current_update_info.files_left}")

                for file_update_info in self.current_update_info.file_downloading_infos:
                    if file_update_info is None:
                        continue

                    imgui.progress_bar(
                        get_progress(
                            file_update_info.file_downloaded_bytes,
                            file_update_info.file_total_bytes),
                        size=(200, 20),
                        overlay="")
                    imgui.same_line()
                    imgui.text(f"{file_update_info.file_name}")


            elif self.current_package_updating is not None:
                imgui.text(f"Gathering manifest for {self.current_package_updating.package_name}")

    async def ready_to_launch(self):
        imgui.text("Everything is up to date.")
        if imgui.button("Run RokBannerlord"):
            self.current_state = LauncherState.EXIT
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
            self.current_state = LauncherState.EXIT

        imgui.same_line()
        if imgui.button("Exit"):
            self.current_state = LauncherState.EXIT

    async def __create_update_task(self):
        for package_version in self.packages_to_update:
            self.current_package_updating = package_version
            self.current_update_info = None
            async for update_process_info in self.launcher.update_package(
                    package_version=package_version,
                    max_parallel_downloads=self.max_downloads):
                self.current_update_info = update_process_info
            self.packages_updated += 1

    async def run(self):
        imgui.create_context()
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.impl.process_inputs()

            imgui.new_frame()

            imgui.set_next_window_position(0, 0)
            imgui.set_next_window_size(imgui.get_io().display_size[0], imgui.get_io().display_size[1])

            imgui.begin("Update")
            if self.current_state == LauncherState.CHECKING_FOR_UPDATES:
                await self.checking_for_update()
            elif self.current_state == LauncherState.ASK_FOR_UPDATE:
                await self.ask_for_update()
            elif self.current_state == LauncherState.UPDATING:
                await self.update()
            elif self.current_state == LauncherState.READY_TO_RUN:
                await self.ready_to_launch()
            elif self.current_state == LauncherState.EXIT:
                break
            imgui.end()

            gl.glClearColor(1.0, 1.0, 1.0, 1)

            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            imgui.render()
            self.impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)
            await asyncio.sleep(0.05)
