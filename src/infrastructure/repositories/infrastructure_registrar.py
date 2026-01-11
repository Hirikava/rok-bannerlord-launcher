import punq

from src.infrastructure.repositories.api_key_repository.api_key_repository import ApiKeyRepository
from src.infrastructure.repositories.local_version_repository.local_version_repository import LocalVersionRepository


class InfrastructureRegistrar:
    @staticmethod
    def configure(container: punq.Container):
        container.register(LocalVersionRepository)
        container.register(ApiKeyRepository)
