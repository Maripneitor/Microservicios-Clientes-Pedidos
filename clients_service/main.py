import threading
import time
import os
from fastapi import FastAPI
from app.infrastructure.db.models import Base
from app.infrastructure.db.database import engine, SessionLocal
from app.infrastructure.api.routes import router as clients_router
from app.infrastructure.messaging.consumer import rabbitmq_listener

def init_db():
    retries = 10
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception as e:
            print(f"Waiting for database... ({retries} retries left). Error: {e}")
            time.sleep(5)
            retries -= 1

# FastAPI App Setup
app = FastAPI(title="Clients Service (Hexagonal)")
app.include_router(clients_router)

@app.on_event("startup")
def startup_event():
    init_db()
    # RabbitMQ Listener in background
    threading.Thread(target=rabbitmq_listener, args=(SessionLocal,), daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
