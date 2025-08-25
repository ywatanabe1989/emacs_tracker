"""Test configuration and fixtures for emacs-tracker MCP server."""

import pytest
import asyncio
import tempfile
import sys
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from emacs_tracker import Tracker, EmacsClient


# Configure pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as unit test (uses mocks)")
    config.addinivalue_line("markers", "integration: mark test as integration test (needs real Emacs)")
    config.addinivalue_line("markers", "mcp: mark test as MCP server test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_emacsclient():
    """Create a mock Emacs client for testing."""
    client = Mock(spec=EmacsClient)
    client.connected = True
    client.eval_elisp = AsyncMock(return_value="nil")
    return client


@pytest.fixture  
def detailed_mock_emacsclient():
    """Create a detailed mock Emacs client with realistic responses."""
    client = Mock(spec=EmacsClient)
    client.connected = True
    
    async def mock_eval_elisp(expression, server=None):
        """Mock elisp evaluation with realistic responses."""
        responses = {
            "(buffer-name)": '"*scratch*"',
            "(buffer-file-name)": '"/tmp/test.py"',
            "(symbol-name major-mode)": '"python-mode"',
            "(point)": "123",
            "(buffer-size)": "456", 
            "(line-number-at-pos)": "10",
            "(current-column)": "5",
            "(symbol-name last-command)": '"self-insert-command"',
            "(symbol-name this-command)": '"self-insert-command"',
            "(buffer-modified-p)": "nil",
            "(length (window-list))": "1",
            '(with-current-buffer "*Messages*" (buffer-substring-no-properties (max 1 (- (point-max) 2000)) (point-max)))': '"Loading test.py...\\nFor information about GNU Emacs..."'
        }
        return responses.get(expression, "nil")
    
    client.eval_elisp = mock_eval_elisp
    return client


@pytest.fixture
def mock_tracker(detailed_mock_emacsclient, tmp_path):
    """Create a Tracker instance for testing."""
    return Tracker(detailed_mock_emacsclient, storage_path=str(tmp_path / "tracker_data"))


@pytest.fixture
def temp_storage_path(tmp_path):
    """Create temporary storage path for testing."""
    storage_path = tmp_path / "test_tracker_storage" 
    storage_path.mkdir(exist_ok=True)
    return str(storage_path)


@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables."""
    original_env = os.environ.copy()
    
    # Set test environment
    test_vars = {
        "EMACS_SERVER_FILE": "/tmp/test_emacs_server",
        "HOME": str(Path.home()),
    }
    
    os.environ.update(test_vars)
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def emacs_available():
    """Check if Emacs server is available for integration tests."""
    socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
    socket_path = Path(socket_name)
    return socket_path.exists()


@pytest.fixture
def real_emacsclient(emacs_available):
    """Create real EmacsClient for integration tests."""
    if not emacs_available:
        pytest.skip("Emacs server not running")
    
    socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
    return EmacsClient(socket_name=socket_name)