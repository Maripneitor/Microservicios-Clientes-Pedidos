from app.application.ports import OrderRepository, MessengerPort, ClientServicePort
from app.domain.models import Order

class CreateOrderUseCase:
    def __init__(self, repository: OrderRepository, messenger: MessengerPort, client_service: ClientServicePort):
        self.repository = repository
        self.messenger = messenger
        self.client_service = client_service

    async def execute(self, client_id: int, product: str, price: float) -> Order:
        # Validate client first
        if not await self.client_service.validate_client(client_id):
            raise Exception("Invalid client")

        order = Order(client_id=client_id, product=product, price=price)
        saved_order = self.repository.save(order)
        
        # Notify via messenger
        self.messenger.publish_order_event({"id": saved_order.id, "client_id": client_id})
        
        return saved_order

class GetOrderUseCase:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def execute(self, order_id: int) -> Order | None:
        return self.repository.get_by_id(order_id)
