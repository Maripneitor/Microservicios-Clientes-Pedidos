import os
import pika
import json
import threading
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base

app = FastAPI(title="Clients Service")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    orders_count = Column(Integer, default=0)

import time

def init_db():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception as e:
            print(f"Waiting for database... ({retries} retries left)")
            time.sleep(5)
            retries -= 1

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/clients/")
def create_client(name: str, email: str, db: Session = Depends(get_db)):
    client = Client(name=name, email=email)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@app.get("/clients/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

def update_client_stats(client_id):
    db = SessionLocal()
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        client.orders_count += 1
        db.commit()
    db.close()

def rabbitmq_listener():
    rabbitmq_url = os.getenv("RABBITMQ_URL")
    params = pika.URLParameters(rabbitmq_url)
    
    while True:
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue='order_notifications', durable=True)

            def callback(ch, method, properties, body):
                data = json.loads(body)
                print(f"Received order notification: {data}")
                update_client_stats(data['client_id'])
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue='order_notifications', on_message_callback=callback)
            print("Clients service listening for RabbitMQ messages...")
            channel.start_consuming()
            break
        except Exception as e:
            print("Waiting for RabbitMQ...")
            time.sleep(5)


@app.on_event("startup")
def startup_event():
    init_db()
    threading.Thread(target=rabbitmq_listener, daemon=True).start()

