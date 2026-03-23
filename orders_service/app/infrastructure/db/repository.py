from sqlalchemy.orm import Session
from app.application.ports import OrderRepository
from app.domain.models import Order
from app.infrastructure.db.models import DBOrder

class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, order: Order) -> Order:
        db_order = DBOrder(client_id=order.client_id, product=order.product, price=order.price)
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        return Order(id=db_order.id, client_id=db_order.client_id, product=db_order.product, price=db_order.price)

    def get_by_id(self, order_id: int) -> Order | None:
        db_order = self.db.query(DBOrder).filter(DBOrder.id == order_id).first()
        if not db_order:
            return None
        return Order(id=db_order.id, client_id=db_order.client_id, product=db_order.product, price=db_order.price)
