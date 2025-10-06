import pytest
from starlette.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from main import app


@pytest.fixture
def test_client():
    """Create a test client for the Starlette app."""
    return TestClient(app)


@pytest.fixture
def mock_agent():
    """Create a mock LangGraph agent for testing."""
    mock = MagicMock()
    mock.astream = AsyncMock()
    return mock


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    return MagicMock()
