import inspect
import typing

from src.domain.invalid_launcher_state_exception import InvalidLauncherStateException
from src.domain.launcher_state import LauncherState
from src.domain.package_version import PackageVersion


@typing.final
class LauncherContext:
    state: LauncherState
    packages_to_update: list[PackageVersion]
    updated_packages: list[PackageVersion]
    user_api_key: str | None
    all_packages_names: list[str]

    def __init__(self):
        self.updated_packages = []
        self.packages_to_update = []
        self.state = LauncherState.ENTER_API_KEY
        self.user_api_key = None
        self.all_packages_names = []

    def set_all_packages_names(
            self,
            all_packages_names: list[str]):
        self.all_packages_names = all_packages_names

    def set_api_key(
            self,
            user_api_key: str):
        if self.state is not LauncherState.ENTER_API_KEY:
            raise InvalidLauncherStateException(self.state, inspect.currentframe().f_code.co_name)

        self.user_api_key = user_api_key
        self.state = LauncherState.CHECKING_FOR_UPDATES

    def set_packages_to_updated(
            self,
            packages_to_update: list[PackageVersion]):
        if self.state is not LauncherState.CHECKING_FOR_UPDATES:
            raise InvalidLauncherStateException(self.state, inspect.currentframe().f_code.co_name)

        self.packages_to_update = packages_to_update
        self.state = LauncherState.ASK_FOR_UPDATE

    def allow_update(self):
        if self.state is not LauncherState.ASK_FOR_UPDATE:
            raise InvalidLauncherStateException(self.state, inspect.currentframe().f_code.co_name)

        self.state = LauncherState.UPDATING

    def set_package_updated(
            self,
            package_version: PackageVersion):
        if self.state is not LauncherState.UPDATING:
            raise InvalidLauncherStateException(self.state, inspect.currentframe().f_code.co_name)

        self.updated_packages.append(package_version)

        if len(self.updated_packages) == len(self.packages_to_update):
            self.state = LauncherState.READY_TO_RUN

    def check_files(
            self,
            all_packages: list[PackageVersion]):
        if self.state is not LauncherState.READY_TO_RUN:
            raise InvalidLauncherStateException(self.state, inspect.currentframe().f_code.co_name)

        self.packages_to_update = all_packages
        self.updated_packages = []
        self.state = LauncherState.UPDATING

    def exit(self):
        self.state = LauncherState.EXIT

    def reset_context(self):
        self.user_api_key = None
        self.updated_packages = []
        self.packages_to_update = []
        self.state = LauncherState.ENTER_API_KEY
