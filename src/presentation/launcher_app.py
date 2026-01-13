import asyncio
import sys

import OpenGL.GL as gl
import glfw
import imgui
import mediatr
import punq
from imgui.integrations.glfw import GlfwRenderer
from mediatr import Mediator

from src.application.application_registrar import ApplicationRegistrar
from src.domain.launcher_context import LauncherContext
from src.domain.launcher_state import LauncherState
from src.external_services.externa_services_registrar import ExternalServicesRegistrar
from src.infrastructure.infrastructure_registrar import InfrastructureRegistrar
from src.presentation.launcher_statets.ask_for_update_launcher_state import AskForUpdateLauncherState
from src.presentation.launcher_statets.check_packages_versions_launcher_state import CheckPackagesVersionsLauncherState
from src.presentation.launcher_statets.enter_api_key_launcher_state import EnterApiKeyLauncherState
from src.presentation.launcher_statets.ready_for_launch_launcher_state import ReadyForLaunchLauncherState
from src.presentation.launcher_statets.update_packages_launcher_state import UpdatePackagesLauncherState
from src.presentation.presentation_registrar import PresentationRegistrar


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


def crete_custom_handler_class_manager(container: punq.Container):
    def custom_handler_class_manager(
            handler_class,
            is_behavior=False):
        if is_behavior:
            # custom logic
            pass
        return container.resolve(handler_class)

    return custom_handler_class_manager


class RokBannerlordLauncherApp:
    mediator: Mediator
    container: punq.Container

    def __init__(
            self,
            packages_names: list[str]):
        imgui.create_context()
        self.window = impl_glfw_init()
        self.impl = GlfwRenderer(self.window)

        self.packages_names = packages_names
        self.container = punq.Container()
        self.mediator = Mediator(
            handler_class_manager=crete_custom_handler_class_manager(self.container))

    def register_dependencies(self):
        self.container.register(mediatr.Mediator, instance=self.mediator)

        PresentationRegistrar.configure(self.container)
        ApplicationRegistrar.configure(self.container)
        ExternalServicesRegistrar.configure(self.container)
        InfrastructureRegistrar.configure(self.container)

    async def run_window(self):
        launcher_context: LauncherContext = self.container.resolve(LauncherContext)
        launcher_context.set_all_packages_names(self.packages_names)

        enter_api_key_state: EnterApiKeyLauncherState = self.container.resolve(EnterApiKeyLauncherState)
        check_for_updates_state: CheckPackagesVersionsLauncherState = self.container.resolve(
            CheckPackagesVersionsLauncherState)
        ask_for_update_packages_state: AskForUpdateLauncherState = self.container.resolve(AskForUpdateLauncherState)
        update_packages_state: UpdatePackagesLauncherState = self.container.resolve(UpdatePackagesLauncherState)
        ready_for_launch_state: ReadyForLaunchLauncherState = self.container.resolve(ReadyForLaunchLauncherState)

        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.impl.process_inputs()

            imgui.new_frame()

            imgui.set_next_window_position(0, 0)
            imgui.set_next_window_size(imgui.get_io().display_size[0], imgui.get_io().display_size[1])
            imgui.set_next_window_collapsed(False)

            imgui.begin("Update", closable=False)

            if launcher_context.state == LauncherState.CHECKING_FOR_UPDATES:
                await check_for_updates_state.run()
            elif launcher_context.state == LauncherState.ASK_FOR_UPDATE:
                await ask_for_update_packages_state.run()
            elif launcher_context.state == LauncherState.UPDATING:
                await update_packages_state.run()
            elif launcher_context.state == LauncherState.READY_TO_RUN:
                await ready_for_launch_state.run()
            elif launcher_context.state == LauncherState.ENTER_API_KEY:
                await enter_api_key_state.run()
            elif launcher_context.state == LauncherState.EXIT:
                break

            imgui.end()
            gl.glClearColor(1.0, 1.0, 1.0, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            imgui.render()
            self.impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)
            await asyncio.sleep(0.05)

    async def run(self):
        self.register_dependencies()
        await self.run_window()
