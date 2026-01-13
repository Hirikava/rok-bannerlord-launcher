from src.external_services.rok_packages_service.rok_packages_service import RokPackagesService


class RokPackageServiceFactory:
    host: str
    port: int

    def __init__(
            self,
            host: str,
            port: int):
        self.host = host
        self.port = port

    def create(
            self,
            user_api_key: str) -> RokPackagesService:
        client = RokPackagesService(
            self.host,
            self.port,
            user_api_key=user_api_key)

        return client
