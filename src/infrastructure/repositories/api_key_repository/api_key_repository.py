import typing
import winreg


@typing.final
class ApiKeyRepository:
    SUB_KEY = "SOFTWARE\ROKBANNERLORD"
    VALUE_NAME = "api-key"

    def save_api_key(
            self,
            api_key: str) -> None:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            self.SUB_KEY,
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_CREATE_SUB_KEY)

        winreg.SetValueEx(
            key,
            self.VALUE_NAME,
            0,
            winreg.REG_SZ,
            api_key)

    def get_api_key(self) -> str:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            self.SUB_KEY,
            0,
            winreg.KEY_READ)

        value, value_type = winreg.QueryValueEx(
            key,
            self.VALUE_NAME)

        return value
