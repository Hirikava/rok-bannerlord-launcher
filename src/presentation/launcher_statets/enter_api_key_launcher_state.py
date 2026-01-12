import imgui

from src.domain.launcher_context import LauncherContext
from src.infrastructure.repositories.api_key_repository.api_key_repository import ApiKeyRepository
from src.presentation.launcher_statets.launcher_state_base import LauncherStateBase


class EnterApiKeyLauncherState(LauncherStateBase):
    cashed_api_key: str | None

    launcher_context: LauncherContext
    api_key_repository: ApiKeyRepository

    def __init__(
            self,
            launcher_context: LauncherContext,
            api_key_repository: ApiKeyRepository):
        self.launcher_context = launcher_context
        self.api_key_repository = api_key_repository

    async def on_init(self):
        self.cashed_api_key = self.api_key_repository.get_api_key()

    async def run_internal(self):
        _, self.cashed_api_key = imgui.input_text("Enter api-key", self.cashed_api_key, int_buffer_length=36)

        imgui.same_line()

        if imgui.button("Enter"):
            self.api_key_repository.save_api_key(self.cashed_api_key)

            self.launcher_context.set_api_key(self.cashed_api_key)
            self.reset()