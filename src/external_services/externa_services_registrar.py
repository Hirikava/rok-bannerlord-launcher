import os

import punq

from src.external_services.rok_packages_service.rok_package_service_factory import RokPackageServiceFactory


class ExternalServicesRegistrar:

    @staticmethod
    def configure(container: punq.Container):
        container.register(
            RokPackageServiceFactory,
            instance=RokPackageServiceFactory(
                ExternalServicesRegistrar.__get_rokb_server_addr(),
                7272))

    @staticmethod
    def __get_rokb_server_addr():
        is_stage = os.getenv('ROKB_STAGE_ENV', default=None)
        if is_stage is None:
            return "rokbannerlord.ru"
        return "127.0.0.1"
