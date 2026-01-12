import typing


@typing.final
class FormatUtils:
    @staticmethod
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

    @staticmethod
    def get_progress(
            current: int,
            total: int) -> float:
        if total == 0:
            return 1.0
        return current / total