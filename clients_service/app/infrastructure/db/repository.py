from sqlalchemy.orm import Session
from app.application.ports import ClientRepository
from app.domain.models import Client
from app.infrastructure.db.models import DBClient

class SqlAlchemyClientRepository(ClientRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, email: str) -> Client:
        db_client = DBClient(name=name, email=email)
        self.db.add(db_client)
        self.db.commit()
        self.db.refresh(db_client)
        return Client(id=db_client.id, name=db_client.name, email=db_client.email, orders_count=db_client.orders_count)

    def get_by_id(self, client_id: int) -> Client | None:
        db_client = self.db.query(DBClient).filter(DBClient.id == client_id).first()
        if not db_client:
            return None
        return Client(id=db_client.id, name=db_client.name, email=db_client.email, orders_count=db_client.orders_count)

    def increment_orders_count(self, client_id: int) -> bool:
        db_client = self.db.query(DBClient).filter(DBClient.id == client_id).first()
        if db_client:
            db_client.orders_count += 1
            self.db.commit()
            return True
        return False
