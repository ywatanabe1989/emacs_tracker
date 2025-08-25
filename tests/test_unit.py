"""Unit tests for emacs-tracker core functionality (using mocks)."""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, Mock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from emacs_tracker import Tracker, EmacsClient


class TestEmacsClientUnit:
    """Unit tests for EmacsClient (mocked)."""
    
    def test_emacsclient_initialization(self):
        """Test EmacsClient initialization."""
        client = EmacsClient()
        assert client.connected is False
        assert client.socket_name is None
        
        # Test with socket name
        socket_name = "/test/socket"
        client_with_socket = EmacsClient(socket_name=socket_name)
        assert client_with_socket.socket_name == socket_name
        assert client_with_socket.connected is False

    @pytest.mark.asyncio
    async def test_emacsclient_mock_eval_elisp(self):
        """Test EmacsClient with mocked eval_elisp."""
        client = EmacsClient()
        
        # Mock the eval_elisp method
        client.eval_elisp = AsyncMock(return_value='"test-result"')
        
        result = await client.eval_elisp('(buffer-name)')
        assert result == '"test-result"'
        client.eval_elisp.assert_called_once_with('(buffer-name)')


class TestTrackerUnit:
    """Unit tests for Tracker class (using mocks)."""
    
    def test_monitor_initialization(self, mock_emacsclient):
        """Test Tracker initialization."""
        monitor = Tracker(mock_emacsclient)
        assert monitor.emacsclient == mock_emacsclient
        assert monitor.buffer_sequence == []
        assert isinstance(monitor.session_start, datetime)

    @pytest.mark.asyncio
    async def test_track_interaction_success(self, detailed_mock_emacsclient):
        """Test successful interaction tracking with detailed mock."""
        monitor = Tracker(detailed_mock_emacsclient)
        
        result = await monitor.track_interaction()
        
        # Verify result structure
        assert result["success"] is True
        assert "result" in result
        assert "current_interaction" in result["result"]
        
        interaction = result["result"]["current_interaction"]
        assert "timestamp" in interaction
        assert "buffer" in interaction
        assert "cursor" in interaction
        assert "commands" in interaction
        
        # Verify buffer info matches mock responses
        buffer_info = interaction["buffer"]
        assert buffer_info["name"] == "*scratch*"
        assert buffer_info["file"] == "/tmp/test.py"
        assert buffer_info["mode"] == "python-mode"
        
        # Verify cursor info
        cursor_info = interaction["cursor"]
        assert cursor_info["position"] == 123
        assert cursor_info["line"] == 10
        assert cursor_info["column"] == 5

    @pytest.mark.asyncio
    async def test_track_interaction_failure(self, mock_emacsclient):
        """Test interaction tracking failure handling."""
        # Mock client to raise exception
        mock_emacsclient.eval_elisp.side_effect = Exception("Connection failed")
        
        monitor = Tracker(mock_emacsclient)
        
        result = await monitor.track_interaction()
        
        # Should handle failure gracefully
        assert result["success"] is False
        assert "error" in result
        assert "Connection failed" in result["error"]

    @pytest.mark.asyncio
    async def test_multiple_interactions_sequence(self, detailed_mock_emacsclient):
        """Test tracking multiple interactions."""
        monitor = Tracker(detailed_mock_emacsclient)
        
        # Track multiple interactions
        results = []
        for i in range(3):
            result = await monitor.track_interaction()
            results.append(result)
        
        # All should succeed
        assert all(r["success"] for r in results)
        
        # Buffer sequence should grow
        assert len(monitor.buffer_sequence) == 3
        
        # Each interaction should have sequence position
        for i, result in enumerate(results):
            interaction = result["result"]["current_interaction"]
            assert interaction["sequence_position"] == i

    def test_monitor_storage_path(self, mock_emacsclient, tmp_path):
        """Test Tracker with custom storage path."""
        storage_path = str(tmp_path / "custom_storage")
        monitor = Tracker(mock_emacsclient, storage_path=storage_path)
        assert str(monitor.storage_path) == storage_path

    @pytest.mark.asyncio
    async def test_buffer_sequence_tracking(self, detailed_mock_emacsclient):
        """Test buffer sequence is properly tracked."""
        monitor = Tracker(detailed_mock_emacsclient)
        
        # Mock different buffer names over time
        buffer_names = ['"*scratch*"', '"test.py"', '"README.md"']
        
        async def changing_buffer_mock(expression, server=None):
            if "(buffer-name)" in expression:
                return buffer_names[len(monitor.buffer_sequence)]
            # Return default responses for other queries
            responses = {
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
        
        detailed_mock_emacsclient.eval_elisp = changing_buffer_mock
        
        # Track interactions across buffer changes
        for expected_count in range(1, 4):
            result = await monitor.track_interaction()
            assert result["success"]
            assert len(monitor.buffer_sequence) == expected_count