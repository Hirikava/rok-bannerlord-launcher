import datetime


class PackageVersion:
    package_name: str
    package_version: str
    package_publish_time: datetime.datetime

    def __init__(
            self,
            package_name: str,
            package_version: str,
            package_publish_time: datetime.datetime):
        self.package_name = package_name
        self.package_version = package_version
        self.package_publish_time = package_publish_time
