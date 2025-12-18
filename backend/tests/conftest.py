# tests/conftest.py
import pytest
#from sqlalchemy.ext.asyncio import AsyncSession
#from tables.users import User
from httpx import AsyncClient, ASGITransport
from argon2 import PasswordHasher
import sys
from pathlib import Path
import asyncio
import pytest_asyncio 
from asgi_lifespan import LifespanManager

ph = PasswordHasher()

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        async with LifespanManager(app):
            yield client
        
@pytest_asyncio.fixture(scope="session")
async def get_token(client):
    headers = {"Content-Type": "application/json"}
    data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    response = await client.post("/auth/login", headers=headers, json=data)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response text: {response.text}")
    assert response.status_code == 200, f"Login failed with status {response.status_code}: {response.text}"
    response_json = response.json()
    print(f"Parsed JSON: {response_json}")
    access_token = response_json["access_token"]
    return access_token