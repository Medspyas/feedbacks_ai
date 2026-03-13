import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
from app.main import app
import asyncio

@pytest.fixture(scope="session")
def event_loop():

    try:
        loop = asyncio.get_event_loop_policy().new_event_loop()
    except RuntimeError:
        policy = asyncio.get_event_loop_policy()
        loop = policy.new_event_loop()

    yield loop
    loop.close()

@pytest.fixture
async def client():

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(autouse=True)
def mock_db_repo():

    with patch("app.repositories.feedback_repo.FeedbackRepository.__init__", return_value=None):
        yield