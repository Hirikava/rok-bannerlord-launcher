import datetime

import pydantic


class LocalPackageVersionDb(pydantic.BaseModel):
    package_name: str
    package_version: str
    publish_datetime: datetime.datetime

    @staticmethod
    def create_from_data(
            package_name: str,
            package_version: str,
            publish_datetime: datetime.datetime):
        return LocalPackageVersionDb(
            **{
                "package_name": package_name,
                "package_version": package_version,
                "publish_datetime": publish_datetime
            })
