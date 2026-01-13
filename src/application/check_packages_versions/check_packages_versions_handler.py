import typing

from mediatr import Mediator

from src.application.check_packages_versions.contracts.check_packages_versions_request import \
    CheckPackagesVersionsRequestInternal
from src.application.check_packages_versions.contracts.check_packages_versions_response import \
    CheckPackagesVersionsResponseInternal
from src.domain.package_version import PackageVersion
from src.external_services.rok_packages_service.rok_package_service_factory import RokPackageServiceFactory
from src.infrastructure.repositories.local_version_repository.local_version_repository import LocalVersionRepository


@typing.final
@Mediator.handler
class CheckPackagesVersionsHandlerInternal:
    local_version_repository: LocalVersionRepository
    rok_packages_service_factory: RokPackageServiceFactory

    def __init__(
            self,
            local_version_repository: LocalVersionRepository,
            rok_packages_service_factory: RokPackageServiceFactory):
        self.local_version_repository = local_version_repository
        self.rok_packages_service_factory = rok_packages_service_factory

    async def handle(
            self,
            request: CheckPackagesVersionsRequestInternal) -> CheckPackagesVersionsResponseInternal:
        packages_to_update = list()

        packages_client = self.rok_packages_service_factory.create(user_api_key=request.user_api_key)

        for package_name in request.packages_names:
            server_version: PackageVersion = await packages_client.get_latest_package_version(
                package_name=package_name)

            local_version: PackageVersion = await self.local_version_repository.get_package_current_version(
                package_name=package_name)

            if local_version is None:
                packages_to_update.append(server_version)
                continue

            if (local_version.package_version != server_version.package_version and local_version.package_publish_time
                    < server_version.package_publish_time):
                packages_to_update.append(server_version)

        internal_response = CheckPackagesVersionsResponseInternal(packages_to_update=packages_to_update)

        return internal_response
