import threading
import time
from fastapi import FastAPI
from app.infrastructure.db.models import Base
from app.infrastructure.db.database import engine, SessionLocal
from app.infrastructure.api.routes import router as orders_router

def init_db():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            break
        except Exception as e:
            print(f"Waiting for database... ({retries} retries left). Error: {e}")
            time.sleep(5)
            retries -= 1

# FastAPI App Setup
app = FastAPI(title="Orders Service (Hexagonal)")
app.include_router(orders_router)

@app.on_event("startup")
def startup_event():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
