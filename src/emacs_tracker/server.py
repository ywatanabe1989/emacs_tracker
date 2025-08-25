#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-25 01:15:47 (ywatanabe)"
# File: /home/ywatanabe/proj/emacs_tracker/src/emacs_tracker/server.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./emacs_tracker/src/emacs_tracker/server.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""emacs-tracker: User Interaction Traffic Recording Server (FastMCP).

FastMCP-based MCP server for recording and serving user interaction data.
Captures comprehensive interaction data for AI analysis and workflow understanding.
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from fastmcp import FastMCP, Context
from .Tracker import Tracker
from .EmacsClient import EmacsClient


# Create FastMCP server instance
mcp = FastMCP("emacs-tracker")

# Global instances (initialized on first use)
emacsclient: Optional[EmacsClient] = None
tracker: Optional[Tracker] = None
config: Dict[str, Any] = {}

# Global monitoring state
monitoring_task: Optional[asyncio.Task] = None
monitoring_active: bool = False
monitoring_config = {
    "interval": 1.0,
    "auto_save": True
}

# Default configuration
DEFAULT_CONFIG = {
    "tracking": {
        "interval": 1.0,
        "capture_detail": "detailed",
        "auto_save": True,
        "interaction_types": ["buffer_switch", "command_execution", "file_operation"]
    },
    "storage": {
        "path": "~/.cache/emacs_tracker",
        "anonymize_exports": True,
        "retention_days": 30
    },
    "emacs": {
        "socket_name": None,  # Will use EMACS_SOCKET env var or default
        "timeout": 5.0
    }
}


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or use defaults."""
    global config
    config = DEFAULT_CONFIG.copy()

    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Deep merge user config with defaults
                for section, values in user_config.items():
                    if section in config:
                        config[section].update(values)
                    else:
                        config[section] = values
            logging.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            logging.warning(f"Failed to load config from {config_path}: {e}, using defaults")
    else:
        logging.info("Using default configuration")

    return config


async def ensure_initialized():
    """Ensure Emacs client and tracker are initialized."""
    global emacsclient, tracker

    if emacsclient is None:
        try:
            socket_name = (
                config.get("emacs", {}).get("socket_name") or
                os.getenv("EMACS_SOCKET_NAME") or
                "/tmp/emacs1000/server"
            )
            storage_path = config.get("storage", {}).get("path", "~/.cache/emacs_tracker")

            emacsclient = EmacsClient(socket_name=socket_name)
            tracker = Tracker(emacsclient, storage_path=storage_path)
            logging.info("Emacs Tracker MCP Server initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize tracker server: {e}")
            raise


async def background_monitoring_loop():
    """Background monitoring loop that continuously tracks Emacs interactions."""
    global monitoring_active, tracker, emacsclient

    logging.info("Starting background monitoring loop")

    while monitoring_active:
        try:
            if emacsclient and tracker:
                # Always attempt tracking (connection status will be updated in eval_elisp)
                result = await tracker.track_interaction()

                if result.get("success"):
                    logging.debug(f"Tracked interaction: buffer={result.get('result', {}).get('current_interaction', {}).get('buffer', {}).get('name', 'unknown')}")
                else:
                    logging.warning(f"Failed to track interaction: {result.get('error')}")

            else:
                logging.warning("Emacs client or tracker not initialized, skipping tracking")

        except Exception as e:
            logging.error(f"Error in monitoring loop: {e}")

        # Wait for next interval
        await asyncio.sleep(monitoring_config["interval"])

    logging.info("Background monitoring loop stopped")


@mcp.tool
async def track_interaction(
    interaction_type: str = None,
    capture_detail: str = None,
    ctx: Context = None
) -> str:
    """Record comprehensive user interaction data.

    Args:
        interaction_type: Type of interaction to record (buffer_switch, command_execution, keystroke_sequence, mode_change, file_operation)
        capture_detail: Level of detail to capture (basic, detailed, comprehensive)
        ctx: MCP context for logging
    """
    await ensure_initialized()

    # Use config defaults if not specified
    interaction_type = interaction_type or config.get("tracking", {}).get("interaction_types", ["buffer_switch"])[0]
    capture_detail = capture_detail or config.get("tracking", {}).get("capture_detail", "detailed")

    if ctx:
        await ctx.info(f"Recording {interaction_type} interaction with {capture_detail} detail")

    if not emacsclient:
        raise Exception("Emacs client not initialized")

    try:
        result = await tracker.track_interaction()

        if result.get("success"):
            message = f"📊 Successfully recorded {interaction_type} interaction"
            if "result" in result:
                interaction_count = result["result"].get("interaction_count", 0)
                message += f"\nCaptured {interaction_count} interactions"
            return message
        else:
            error_msg = result.get("error", "Unknown error")
            raise Exception(f"Interaction recording failed: {error_msg}")

    except Exception as e:
        if ctx:
            await ctx.error(f"Failed to record interaction: {e}")
        raise


@mcp.tool
async def get_tracking_log(
    limit: int = 10,
    filter_type: str = "all",
    time_range: str = "this_session",
    ctx: Context = None
) -> str:
    """Retrieve recorded user interaction traffic.

    Args:
        limit: Number of recent interactions to return (1-100)
        filter_type: Filter interactions by type (all, buffer_switches, commands, keystrokes, modes)
        time_range: Time range for interactions (last_hour, today, this_session, all)
        ctx: MCP context for logging
    """
    await ensure_initialized()

    if ctx:
        await ctx.info(f"Retrieving {limit} interactions (filter: {filter_type}, range: {time_range})")

    # Validate limit
    limit = max(1, min(100, limit))

    # Get recent interactions
    recent_traffic = tracker.buffer_sequence[-limit:]

    # Apply filtering
    if filter_type != "all":
        # Simple filtering based on interaction type
        filtered_traffic = [
            interaction
            for interaction in recent_traffic
            if filter_type in str(interaction).lower()
        ]
        recent_traffic = filtered_traffic

    # Format result
    result_data = {
        "traffic_data": recent_traffic,
        "count": len(recent_traffic),
        "filter_applied": filter_type,
        "time_range": time_range,
        "session_total": len(tracker.buffer_sequence),
        "retrieved_at": datetime.now().isoformat()
    }

    # Return formatted JSON string
    return f"📈 **User Traffic Retrieved**\n\n" + \
           f"**Count:** {len(recent_traffic)} interactions\n" + \
           f"**Filter:** {filter_type}\n" + \
           f"**Session Total:** {len(tracker.buffer_sequence)}\n\n" + \
           f"**Recent Traffic:**\n```json\n{json.dumps(result_data, indent=2)}\n```"


@mcp.tool
async def export_data(
    output_file: str,
    export_format: str = "json",
    anonymize: bool = True,
    ctx: Context = None
) -> str:
    """Export user interaction data for external analysis.

    Args:
        output_file: Output file path
        export_format: Export format (json, csv, org)
        anonymize: Whether to anonymize file paths and content
        ctx: MCP context for logging
    """
    await ensure_initialized()

    if ctx:
        await ctx.info(f"Exporting tracked data to {output_file} (format: {export_format}, anonymized: {anonymize})")

    try:
        # Prepare data for export
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "session_start": tracker.session_start.isoformat(),
            "total_interactions": len(tracker.buffer_sequence),
            "interactions": tracker.buffer_sequence,
            "export_settings": {
                "format": export_format,
                "anonymized": anonymize
            }
        }

        # Anonymize if requested
        if anonymize:
            for interaction in export_data["interactions"]:
                if "buffer" in interaction and "file" in interaction["buffer"]:
                    if interaction["buffer"]["file"]:
                        # Replace with generic path
                        interaction["buffer"]["file"] = "anonymized_file_path"

        # Write to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if export_format == "json":
            with open(output_path, "w") as f:
                json.dump(export_data, f, indent=2)
        elif export_format == "csv":
            # Basic CSV export (could be enhanced)
            import csv
            with open(output_path, "w", newline='') as f:
                if export_data["interactions"]:
                    # Get keys from first interaction
                    fieldnames = export_data["interactions"][0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(export_data["interactions"])
        else:
            raise Exception(f"Export format '{export_format}' not yet supported")

        return f"✅ **Export Successful**\n\n" + \
               f"**File:** {output_path}\n" + \
               f"**Format:** {export_format}\n" + \
               f"**Interactions:** {len(tracker.buffer_sequence)}\n" + \
               f"**Anonymized:** {anonymize}"

    except Exception as e:
        if ctx:
            await ctx.error(f"Export failed: {e}")
        raise Exception(f"Export failed: {e}")


@mcp.tool
async def start_real_time_tracking(
    tracking_interval_sec: float = None,
    auto_save: bool = None,
    ctx: Context = None
) -> str:
    """Start continuous real-time interaction monitoring.

    Args:
        tracking_interval_sec: Recording interval in seconds (0.1-60.0)
        auto_save: Whether to auto-save recorded data
        ctx: MCP context for logging
    """
    global monitoring_task, monitoring_active, monitoring_config

    await ensure_initialized()

    # Use defaults if not specified
    tracking_interval_sec = tracking_interval_sec or monitoring_config["interval"]
    auto_save = auto_save if auto_save is not None else monitoring_config["auto_save"]

    # Validate interval
    tracking_interval_sec = max(0.1, min(60.0, tracking_interval_sec))

    if ctx:
        await ctx.info(f"Starting real-time tracking (interval: {tracking_interval_sec}s, auto-save: {auto_save})")

    # Stop existing monitoring if running
    if monitoring_active and monitoring_task:
        monitoring_active = False
        if not monitoring_task.done():
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass

    # Update monitoring configuration
    monitoring_config["interval"] = tracking_interval_sec
    monitoring_config["auto_save"] = auto_save

    # Start new monitoring task
    monitoring_active = True
    monitoring_task = asyncio.create_task(background_monitoring_loop())

    logging.info(f"Real-time tracking started with interval {tracking_interval_sec}s")

    return f"🔄 **Real-time Tracking Started**\n\n" + \
           f"**Interval:** {tracking_interval_sec} seconds\n" + \
           f"**Auto-save:** {auto_save}\n" + \
           f"**Status:** Active background monitoring\n" + \
           f"**Task ID:** {id(monitoring_task)}"


@mcp.tool
async def stop_real_time_tracking(ctx: Context = None) -> str:
    """Stop continuous real-time interaction tracking.

    Args:
        ctx: MCP context for logging
    """
    global monitoring_task, monitoring_active

    if ctx:
        await ctx.info("Stopping real-time tracking")

    if not monitoring_active:
        return "⏹️ **Real-time Tracking Already Stopped**\n\nNo monitoring task was running."

    # Stop monitoring
    monitoring_active = False

    if monitoring_task and not monitoring_task.done():
        monitoring_task.cancel()
        try:
            await monitoring_task
            logging.info("Real-time tracking stopped successfully")
        except asyncio.CancelledError:
            logging.info("Real-time tracking cancelled")

    return "⏹️ **Real-time Tracking Stopped**\n\n" + \
           f"**Status:** Trackering task terminated\n" + \
           f"**Data preserved:** Session data remains available"


@mcp.tool
async def get_monitoring_status(ctx: Context = None) -> str:
    """Get current monitoring status and statistics.

    Args:
        ctx: MCP context for logging
    """
    global monitoring_task, monitoring_active, tracker

    await ensure_initialized()

    if ctx:
        await ctx.info("Retrieving monitoring status")

    # Get basic status
    status_info = {
        "monitoring_active": monitoring_active,
        "tracking_interval_sec": monitoring_config.get("interval", 0),
        "auto_save": monitoring_config.get("auto_save", False),
        "task_running": monitoring_task is not None and not monitoring_task.done() if monitoring_task else False,
        "emacs_connected": emacsclient.connected if emacsclient else False,
        "session_start": tracker.session_start.isoformat() if tracker else None,
        "total_interactions": len(tracker.buffer_sequence) if tracker else 0,
    }

    return f"📊 **Trackering Status**\n\n" + \
           f"**Active:** {'Yes' if status_info['monitoring_active'] else 'No'}\n" + \
           f"**Interval:** {status_info['tracking_interval_sec']} seconds\n" + \
           f"**Auto-save:** {'Enabled' if status_info['auto_save'] else 'Disabled'}\n" + \
           f"**Emacs Connected:** {'Yes' if status_info['emacs_connected'] else 'No'}\n" + \
           f"**Session Start:** {status_info['session_start']}\n" + \
           f"**Total Interactions:** {status_info['total_interactions']}\n\n" + \
           f"```json\n{json.dumps(status_info, indent=2)}\n```"


@mcp.tool
async def query_interaction_context(
    query_type: str,
    query_params: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> str:
    """Query specific aspects of user interaction context.

    Args:
        query_type: Type of context query (current_state, recent_files, active_modes, command_history, buffer_history)
        query_params: Additional query parameters
        ctx: MCP context for logging
    """
    await ensure_initialized()

    if ctx:
        await ctx.info(f"Querying interaction context: {query_type}")

    if not emacsclient:
        raise Exception("Emacs client not initialized")

    if query_type == "current_state":
        try:
            # Get current Emacs state
            current_buffer = await emacsclient.eval_elisp("(buffer-name)")
            current_mode = await emacsclient.eval_elisp("(symbol-name major-mode)")
            current_file = await emacsclient.eval_elisp("(buffer-file-name)")

            result = {
                "current_buffer": current_buffer.strip('"'),
                "current_mode": current_mode.strip('"'),
                "current_file": (
                    current_file.strip('"')
                    if current_file != "nil"
                    else None
                ),
                "query_timestamp": datetime.now().isoformat(),
                "query_type": query_type
            }

            return f"📋 **Current Emacs State**\n\n" + \
                   f"**Buffer:** {result['current_buffer']}\n" + \
                   f"**Mode:** {result['current_mode']}\n" + \
                   f"**File:** {result['current_file'] or 'No file'}\n\n" + \
                   f"```json\n{json.dumps(result, indent=2)}\n```"

        except Exception as e:
            if ctx:
                await ctx.error(f"Failed to query current state: {e}")
            raise Exception(f"Failed to query current state: {e}")

    else:
        # For other query types, return placeholder
        return f"🔍 **Context Query: {query_type}**\n\n" + \
               f"Query type '{query_type}' implementation is pending.\n" + \
               f"Available: current_state\n" + \
               f"Coming soon: recent_files, active_modes, command_history, buffer_history"


@mcp.tool
async def clear_data(
    clear_scope: str = "current_session",
    confirm: bool = False,
    ctx: Context = None
) -> str:
    """Clear stored interaction data.

    Args:
        clear_scope: Scope of data to clear (current_session, today, all)
        confirm: Confirmation flag (must be True to proceed)
        ctx: MCP context for logging
    """
    await ensure_initialized()

    if not confirm:
        return "⚠️ **Confirmation Required**\n\n" + \
               "To clear interaction data, you must set `confirm=True`\n" + \
               f"This will clear data for scope: {clear_scope}"

    if ctx:
        await ctx.info(f"Clearing interaction data (scope: {clear_scope})")

    if clear_scope == "current_session":
        original_count = len(tracker.buffer_sequence)
        tracker.buffer_sequence = []

        return f"🗑️ **Data Cleared**\n\n" + \
               f"**Scope:** {clear_scope}\n" + \
               f"**Cleared:** {original_count} interactions"
    else:
        raise Exception(f"Clear scope '{clear_scope}' not yet implemented")


def main():
    """Main entry point for emacs-tracker-context FastMCP server."""
    parser = argparse.ArgumentParser(
        description="Emacs Tracker FastMCP Server"
    )
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument(
        "--debug", "-d", action="store_true", help="Enable debug logging"
    )
    parser.add_argument(
        "--transport", "-t",
        choices=["stdio", "sse", "http"],
        default="stdio",
        help="Transport protocol to use"
    )
    parser.add_argument("--host", default="localhost", help="Host for HTTP/SSE transport")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP/SSE transport")

    args = parser.parse_args()

    # Load configuration first
    load_config(args.config)

    # Setup logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Run FastMCP server
        if args.transport == "stdio":
            mcp.run()
        elif args.transport == "sse":
            mcp.run(transport="sse", host=args.host, port=args.port)
        elif args.transport == "http":
            mcp.run(transport="http", host=args.host, port=args.port, path="/mcp")

    except KeyboardInterrupt:
        print("\nShutting down tracker server...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Tracker server failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# EOF
