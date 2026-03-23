from abc import ABC, abstractmethod
from typing import Optional
from app.domain.models import Order

class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> Order:
        pass

    @abstractmethod
    def get_by_id(self, order_id: int) -> Optional[Order]:
        pass

class MessengerPort(ABC):
    @abstractmethod
    def publish_order_event(self, order_data: dict):
        pass

class ClientServicePort(ABC):
    @abstractmethod
    async def validate_client(self, client_id: int) -> bool:
        pass
