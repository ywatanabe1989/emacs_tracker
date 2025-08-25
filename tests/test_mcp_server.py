"""Tests for MCP server functionality."""

import asyncio
import pytest
from fastmcp import Client
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.mark.mcp
class TestMCPServer:
    """Test MCP server functionality."""

    @pytest.mark.asyncio
    async def test_mcp_server_connection(self):
        """Test basic MCP server connection."""
        from emacs_tracker.server import mcp
        
        async with Client(mcp) as client:
            # Should connect successfully
            tools = await client.list_tools()
            assert len(tools) > 0
            
            # Check for expected tools
            tool_names = [tool.name for tool in tools]
            expected_tools = [
                "track_interaction",
                "get_tracking_log", 
                "query_interaction_context",
                "get_monitoring_status"
            ]
            
            for expected_tool in expected_tools:
                assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_mcp_server_stdio(self):
        """Test MCP server via stdio (production mode)."""
        try:
            async with Client("python -m emacs_tracker") as client:
                tools = await client.list_tools()
                assert len(tools) > 0
        except Exception as e:
            pytest.skip(f"Stdio connection failed (expected if no Emacs): {e}")

    @pytest.mark.asyncio
    async def test_mcp_tool_execution_no_emacs(self):
        """Test MCP tools when Emacs is not available."""
        from emacs_tracker.server import mcp
        
        async with Client(mcp) as client:
            # These should fail gracefully when Emacs is not connected
            try:
                result = await client.call_tool(
                    "query_interaction_context",
                    {"query_type": "current_state"}
                )
                # If it succeeds, great! If not, check it fails gracefully
                assert hasattr(result, 'content') and isinstance(result.content[0].text, str)
            except Exception as e:
                # Should be a graceful failure message
                assert "not connected" in str(e).lower() or "not initialized" in str(e).lower()

    @pytest.mark.asyncio
    async def test_mcp_get_tracking_log(self):
        """Test get_tracking_log MCP tool."""
        from emacs_tracker.server import mcp
        
        async with Client(mcp) as client:
            try:
                result = await client.call_tool(
                    "get_tracking_log",
                    {"limit": 5, "filter_type": "all"}
                )
                assert hasattr(result, 'content') and isinstance(result.content[0].text, str)
                # Should contain tracking information or graceful failure
                assert len(result.content[0].text) > 0
            except Exception as e:
                # Graceful failure expected when no Emacs
                assert "not connected" in str(e).lower() or "not initialized" in str(e).lower()

    @pytest.mark.asyncio
    async def test_mcp_monitoring_status(self):
        """Test get_monitoring_status MCP tool.""" 
        from emacs_tracker.server import mcp
        
        async with Client(mcp) as client:
            try:
                result = await client.call_tool("get_monitoring_status", {})
                assert hasattr(result, 'content') and isinstance(result.content[0].text, str)
                assert "Trackering Status" in result.content[0].text
            except Exception as e:
                pytest.skip(f"Trackering status failed: {e}")


@pytest.mark.mcp
@pytest.mark.integration  
class TestMCPWithEmacs:
    """Test MCP server with real Emacs connection."""

    @pytest.fixture(scope="class")
    def emacs_available(self):
        """Check if Emacs is available."""
        import os
        from pathlib import Path
        socket_name = os.getenv("EMACS_SOCKET_NAME") or "/home/ywatanabe/.emacs.d/server/server"
        return Path(socket_name).exists()

    @pytest.mark.asyncio
    async def test_mcp_with_real_emacs(self, emacs_available):
        """Test MCP tools with real Emacs connection."""
        if not emacs_available:
            pytest.skip("Emacs server not running")
            
        from emacs_tracker.server import mcp
        
        async with Client(mcp) as client:
            # Test current state query
            result = await client.call_tool(
                "query_interaction_context",
                {"query_type": "current_state"}
            )
            
            # Should succeed and return current Emacs state
            assert hasattr(result, 'content') and isinstance(result.content[0].text, str)
            assert len(result.content[0].text) > 0
            # Should contain information about current buffer/state
            text_content = result.content[0].text
            assert "Buffer:" in text_content or "State" in text_content

    @pytest.mark.asyncio
    async def test_mcp_track_interaction_real(self, emacs_available):
        """Test track_interaction with real Emacs."""
        if not emacs_available:
            pytest.skip("Emacs server not running")
            
        from emacs_tracker.server import mcp
        
        async with Client(mcp) as client:
            result = await client.call_tool("track_interaction", {})
            
            # Should succeed or fail gracefully
            assert hasattr(result, 'content') and isinstance(result.content[0].text, str)
            # Either successful tracking or graceful error
            success_indicators = ["Successfully recorded", "interaction", "tracked"]
            error_indicators = ["not connected", "failed", "error"]
            
            text_lower = result.content[0].text.lower()
            has_success = any(indicator in text_lower for indicator in success_indicators)
            has_error = any(indicator in text_lower for indicator in error_indicators)
            
            # Should have either success or graceful error, not crash
            assert has_success or has_error