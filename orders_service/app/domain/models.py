from pydantic import BaseModel

class Order(BaseModel):
    id: int | None = None
    client_id: int
    product: str
    price: float
