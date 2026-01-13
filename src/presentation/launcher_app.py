import asyncio
import enum
import os
import subprocess
import sys
from pathlib import Path

import OpenGL.GL as gl
import glfw
import imgui
import punq
from imgui.integrations.glfw import GlfwRenderer
from mediatr import Mediator

from src.application.update_package.contracts.update_package_request import UpdatePackageRequestInternal
from src.application.update_package.contracts.update_package_response import UpdatePackageResponseInternal
from src.domain.launcher_context import LauncherContext
from src.domain.launcher_state import LauncherState
from src.domain.package_version import PackageVersion
from src.utils.format_utils import FormatUtils


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


class RokBannerlordLauncherApp:
    checking_for_update_task = None
    updating_task = None

    launcher_context: LauncherContext

    packages_names: list[str]

    mediator: Mediator
    container: punq.Container

    def __init__(
            self,
            host: str,
            port: int,
            packages_names: list[str]):

        imgui.create_context()
        self.window = impl_glfw_init()
        self.impl = GlfwRenderer(self.window)

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

            internal_request = UpdatePackageRequestInternal(
                package_version=package_version,
                max_parallel_downloads=4)

            internal_response: UpdatePackageResponseInternal = await self.mediator.send_async(internal_request)

            async for update_process_info in internal_response.update_package_stream:
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
