from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.application.use_cases import CreateOrderUseCase, GetOrderUseCase
from app.infrastructure.db.repository import SqlAlchemyOrderRepository
from app.infrastructure.messaging.pika_publisher import PikaMessenger
from app.infrastructure.http_clients.clients_service import HttpClientsService
from app.infrastructure.db.database import get_db

router = APIRouter()

@router.post("/orders/")
async def create_order(client_id: int, product: str, price: float, db: Session = Depends(get_db)):
    repository = SqlAlchemyOrderRepository(db)
    messenger = PikaMessenger()
    client_service = HttpClientsService()
    
    use_case = CreateOrderUseCase(repository, messenger, client_service)
    try:
        return await use_case.execute(client_id, product, price)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    repository = SqlAlchemyOrderRepository(db)
    use_case = GetOrderUseCase(repository)
    order = use_case.execute(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
