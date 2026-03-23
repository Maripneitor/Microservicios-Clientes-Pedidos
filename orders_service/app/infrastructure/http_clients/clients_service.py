import os
import httpx
from app.application.ports import ClientServicePort

class HttpClientsService(ClientServicePort):
    def __init__(self):
        self.url = os.getenv("CLIENTS_SERVICE_URL")

    async def validate_client(self, client_id: int) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.url}/clients/{client_id}")
                return response.status_code == 200
            except httpx.RequestError:
                return False
