import socket
import pytest
from unittest.mock import AsyncMock
from sqlalchemy import create_engine, text
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def get_effective_db_url(url: str) -> str:
    if "@db:" in url:
        try:
            socket.gethostbyname("db")
        except socket.gaierror:
            return url.replace("@db:", "@localhost:")
    return url


@pytest.fixture(autouse=True)
def clear_tickets():
    raw_url = get_effective_db_url(settings.DATABASE_URL)
    sync_url = raw_url.replace("postgresql+asyncpg://", "postgresql://")
    engine = create_engine(sync_url)
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE tickets CASCADE;"))
    engine.dispose()
    yield


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def existing_ticket_id():
    client = TestClient(app)
    res = client.post(
        "/tickets/",
        json={"title": "Integration test ticket", "priority": "medium"}
    )
    return res.json()["id"]
