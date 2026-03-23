from app.application.ports import ClientRepository
from app.domain.models import Client

class CreateClientUseCase:
    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def execute(self, name: str, email: str) -> Client:
        return self.repository.create(name, email)

class GetClientUseCase:
    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def execute(self, client_id: int) -> Client | None:
        return self.repository.get_by_id(client_id)

class UpdateClientStatsUseCase:
    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def execute(self, client_id: int) -> bool:
        return self.repository.increment_orders_count(client_id)
