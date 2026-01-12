from src.application.update_package.contracts.file_downloading_info import FileDownloadingInfoInternal


class UpdatePackageProcessInfoInternal:
    files_left: int
    total_bytes_read: int
    total_bytes: int
    file_downloading_infos: list[FileDownloadingInfoInternal]

    def __init__(
            self,
            files_left: int,
            total_bytes_read: int,
            total_bytes: int,
            max_downloading_processes: int):
        self.files_left = files_left
        self.total_bytes_read = total_bytes_read
        self.total_bytes = total_bytes
        self.file_downloading_infos = list()
        for i in range(max_downloading_processes):
            self.file_downloading_infos.append(None)
