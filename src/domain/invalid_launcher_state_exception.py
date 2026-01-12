from src.domain.launcher_state import LauncherState


class InvalidLauncherStateException(Exception):
    state: LauncherState
    operation: str

    def __init__(
            self,
            launcher_state: LauncherState,
            operation: str):
        self.state = launcher_state
        self.operation = operation

