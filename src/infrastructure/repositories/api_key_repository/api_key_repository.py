import typing
import winreg


@typing.final
class ApiKeyRepository:
    SUB_KEY = "SOFTWARE\ROKBANNERLORD"
    VALUE_NAME = "api-key"

    def save_api_key(
            self,
            api_key: str) -> None:
        key = winreg.CreateKeyEx(
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

    def get_api_key(self) -> str | None:
        key = winreg.CreateKeyEx(
            winreg.HKEY_CURRENT_USER,
            self.SUB_KEY,
            0,
            winreg.KEY_READ)

        try:
            value, value_type = winreg.QueryValueEx(
                key,
                self.VALUE_NAME)

            return value
        except Exception as e:
            return None
