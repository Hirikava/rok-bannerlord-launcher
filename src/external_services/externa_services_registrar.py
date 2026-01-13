import punq

from src.external_services.rok_packages_service.rok_package_service_factory import RokPackageServiceFactory


class ExternalServicesRegistrar:

    @staticmethod
    def configure(container: punq.Container):
        container.register(
            RokPackageServiceFactory,
            instance=RokPackageServiceFactory("localhost", 7272))
