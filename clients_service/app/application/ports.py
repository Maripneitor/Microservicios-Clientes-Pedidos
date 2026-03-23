from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models import Client

class ClientRepository(ABC):
    @abstractmethod
    def create(self, name: str, email: str) -> Client:
        pass

    @abstractmethod
    def get_by_id(self, client_id: int) -> Optional[Client]:
        pass

    @abstractmethod
    def increment_orders_count(self, client_id: int) -> bool:
        pass
