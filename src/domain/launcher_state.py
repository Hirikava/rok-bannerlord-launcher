import enum


class LauncherState(enum.IntEnum):
    ENTER_API_KEY = 0
    CHECKING_FOR_UPDATES = 1
    ASK_FOR_UPDATE = 2
    READY_TO_RUN = 3
    UPDATING = 4
    EXIT = 5
