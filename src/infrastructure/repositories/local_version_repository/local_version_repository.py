import json
import os
from pathlib import Path

import aiofiles

from src.domain.package_version import PackageVersion
from src.infrastructure.repositories.local_version_repository.local_package_version_db import LocalPackageVersionDb


class LocalVersionRepository:
    def __init__(self):
        os.makedirs(".versions", exist_ok=True)

    @staticmethod
    async def get_package_current_version(package_name: str) -> PackageVersion | None:
        version_file_path = Path(".versions") / f"{package_name}.json"

        if not os.path.exists(version_file_path):
            return None

        async with aiofiles.open(version_file_path, "rt") as file:
            file_content = await file.read()

        package_version_db = LocalPackageVersionDb(**json.loads(file_content))

        package_version = PackageVersion(
            package_name=package_version_db.package_name,
            package_version=package_version_db.package_version,
            package_publish_time=package_version_db.publish_datetime)
        return package_version

    @staticmethod
    async def save_package_current_version(package_version: PackageVersion):
        version_file_path = Path(".versions") / f"{package_version.package_name}.json"
        version_file_path.parent.mkdir(parents=True, exist_ok=True)

        package_version_db = LocalPackageVersionDb.create_from_data(
            package_name=package_version.package_name,
            package_version=package_version.package_version,
            publish_datetime=package_version.package_publish_time)

        async with aiofiles.open(version_file_path, "wt") as file:
            await file.write(package_version_db.model_dump_json(indent=4))