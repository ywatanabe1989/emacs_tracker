"""Integration tests for real Emacs connections (requires running Emacs server)."""

import asyncio
import os
import pytest
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from emacs_tracker import EmacsClient, Tracker


@pytest.fixture(scope="class")
def emacs_available():
    """Check if Emacs server is available."""
    socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
    socket_path = Path(socket_name)
    return socket_path.exists()


@pytest.mark.integration
class TestRealEmacsConnection:
    """Test real connection to Emacs server."""

    @pytest.mark.asyncio
    async def test_emacsclient_connection(self, emacs_available):
        """Test EmacsClient connects to real Emacs."""
        if not emacs_available:
            pytest.skip("Emacs server not running")
        
        socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
        client = EmacsClient(socket_name=socket_name)
        
        # Test connection
        result = await client.eval_elisp("(buffer-name)")
        
        assert client.connected is True
        assert isinstance(result, str)
        assert len(result) > 0
        assert result != "nil"

    @pytest.mark.asyncio
    async def test_server_parameter_bug_fix(self, emacs_available):
        """Test the critical server parameter fix."""
        if not emacs_available:
            pytest.skip("Emacs server not running")
        
        socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
        client = EmacsClient(socket_name=socket_name)
        
        # This was the exact bug scenario - server=None should work
        result = await client.eval_elisp("(buffer-name)", server=None)
        
        assert client.connected is True
        assert result != "nil"

    @pytest.mark.asyncio
    async def test_multiple_queries(self, emacs_available):
        """Test multiple consecutive queries."""
        if not emacs_available:
            pytest.skip("Emacs server not running")
        
        socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
        client = EmacsClient(socket_name=socket_name)
        
        queries = [
            "(buffer-name)",
            "(symbol-name major-mode)", 
            "(buffer-file-name)",
            "(point)"
        ]
        
        results = []
        for query in queries:
            result = await client.eval_elisp(query)
            results.append(result)
            assert client.connected is True
        
        # Should have gotten results for all queries
        assert len(results) == len(queries)

    @pytest.mark.asyncio
    async def test_monitor_real_tracking(self, emacs_available):
        """Test Tracker with real Emacs tracking."""
        if not emacs_available:
            pytest.skip("Emacs server not running")
        
        socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
        client = EmacsClient(socket_name=socket_name)
        monitor = Tracker(client)
        
        result = await monitor.track_interaction()
        
        if result["success"]:
            assert "result" in result
            assert "current_interaction" in result["result"]
            
            interaction = result["result"]["current_interaction"]
            assert "buffer" in interaction
            assert "cursor" in interaction
            assert "timestamp" in interaction
        else:
            pytest.fail(f"Real tracking failed: {result.get('error')}")


@pytest.mark.integration  
class TestErrorHandling:
    """Test error handling with various failure scenarios."""
    
    @pytest.mark.asyncio
    async def test_invalid_socket_path(self):
        """Test behavior with completely invalid socket."""
        client = EmacsClient(socket_name="/completely/invalid/socket/path")
        
        result = await client.eval_elisp("(buffer-name)")
        
        assert client.connected is False
        assert result == "nil"
    
    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, emacs_available):
        """Test timeout handling with real connection but long query."""
        if not emacs_available:
            pytest.skip("Emacs server not running")
        
        socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
        client = EmacsClient(socket_name=socket_name)
        
        # This should still work within timeout
        result = await client.eval_elisp("(+ 1 1)")
        assert result.strip() == "2"

    @pytest.mark.asyncio
    async def test_simple_expressions(self, emacs_available):
        """Test simple Elisp expressions from standalone tests."""
        if not emacs_available:
            pytest.skip("Emacs server not running")
        
        socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
        client = EmacsClient(socket_name=socket_name)
        
        # Test various simple expressions
        test_cases = [
            ("(+ 2 3)", "5"),
            ("(* 4 5)", "20"),
            ("(length \"hello\")", "5")
        ]
        
        for expr, expected in test_cases:
            result = await client.eval_elisp(expr)
            assert result.strip() == expected, f"Expected {expected} for {expr}, got {result}"

    @pytest.mark.asyncio
    async def test_tracking_session(self, emacs_available):
        """Test a complete tracking session from test_1min_tracking."""
        if not emacs_available:
            pytest.skip("Emacs server not running")
        
        socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
        client = EmacsClient(socket_name=socket_name)
        monitor = Tracker(client)
        
        # Track several interactions
        successful_tracks = 0
        for i in range(5):
            result = await monitor.track_interaction()
            if result["success"]:
                successful_tracks += 1
            await asyncio.sleep(0.1)
        
        # Should have some successful tracking
        assert successful_tracks > 0, "No successful tracking in session"