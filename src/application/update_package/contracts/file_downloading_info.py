class FileDownloadingInfoInternal:
    file_total_bytes: int
    file_downloaded_bytes: int
    file_name: str

    def __init__(
            self,
            file_total_bytes: int,
            file_downloaded_bytes: int,
            file_name: str):
        self.file_total_bytes = file_total_bytes
        self.file_downloaded_bytes = file_downloaded_bytes
        self.file_name = file_name
