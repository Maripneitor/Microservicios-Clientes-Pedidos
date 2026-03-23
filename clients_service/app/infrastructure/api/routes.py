from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.application.use_cases import CreateClientUseCase, GetClientUseCase
from app.infrastructure.db.repository import SqlAlchemyClientRepository
from app.infrastructure.db.database import get_db

router = APIRouter()

@router.post("/clients/")
def create_client(name: str, email: str, db: Session = Depends(get_db)):
    repository = SqlAlchemyClientRepository(db)
    use_case = CreateClientUseCase(repository)
    return use_case.execute(name, email)

@router.get("/clients/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db)):
    repository = SqlAlchemyClientRepository(db)
    use_case = GetClientUseCase(repository)
    client = use_case.execute(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client
