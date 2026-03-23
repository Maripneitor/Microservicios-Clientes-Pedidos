from pydantic import BaseModel

class Client(BaseModel):
    id: int | None = None
    name: str
    email: str
    orders_count: int = 0
