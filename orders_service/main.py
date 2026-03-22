import os
import pika
import httpx
import json
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base

app = FastAPI(title="Orders Service")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer)
    product = Column(String(100))
    price = Column(Float)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

CLIENTS_SERVICE_URL = os.getenv("CLIENTS_SERVICE_URL")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

def publish_order_event(order_data):
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='order_notifications', durable=True)
    channel.basic_publish(
        exchange='',
        routing_key='order_notifications',
        body=json.dumps(order_data),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )
    connection.close()

@app.post("/orders/")
async def create_order(client_id: int, product: str, price: float, db: Session = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{CLIENTS_SERVICE_URL}/clients/{client_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid client")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Clients service unavailable")

    order = Order(client_id=client_id, product=product, price=price)
    db.add(order)
    db.commit()
    db.refresh(order)

    publish_order_event({"id": order.id, "client_id": client_id})

    return order

@app.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
