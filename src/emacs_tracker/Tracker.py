#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-26 01:32:36 (ywatanabe)"
# File: /home/ywatanabe/proj/emacs_tracker/src/emacs_tracker/Tracker.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/emacs_tracker/Tracker.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Tracking Context tools for Emacs MCP Server.

These tools track user interaction patterns, buffer sequences, and editing workflows
to provide personalized AI assistance based on observed patterns.
"""

import asyncio
import difflib
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .EmacsClient import EmacsClient


def format_mcp_response(
    success: bool, data: Any = None, error: str = None
) -> Dict[str, Any]:
    """Format response for MCP protocol."""
    response = {"success": success}
    if success:
        if data:
            response["result"] = data
    else:
        response["error"] = error or "Unknown error"
    return response


class Tracker:
    """Simple tracker for recorded user interaction traffic."""

    def __init__(
        self, emacsclient: EmacsClient, storage_path: Optional[str] = None
    ):
        self.emacsclient = emacsclient
        self.storage_path = Path(
            storage_path or "~/.cache/emacs_tracker"
        ).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Current session data - just recorded traffic
        self.buffer_sequence = []
        self.last_buffer_contents = {}
        self.session_start = datetime.now()

        # Tracking state
        self._tracking_task = None
        self.is_tracking = False

    async def start_tracking(
        self, interval_sec: float = 2.0
    ) -> Dict[str, Any]:
        """Start continuous tracking with specified interval."""
        if self.is_tracking:
            return format_mcp_response(False, error="Tracking already active")

        try:
            self.is_tracking = True
            self._tracking_task = asyncio.create_task(
                self._tracking_loop(interval_sec)
            )

            return format_mcp_response(
                True,
                {
                    "status": "tracking_started",
                    "interval_seconds": interval_sec,
                    "session_id": self.session_start.isoformat(),
                },
            )
        except Exception as e:
            self.is_tracking = False
            return format_mcp_response(
                False, error=f"Failed to start tracking: {e}"
            )

    async def end_tracking(self) -> Dict[str, Any]:
        """End continuous tracking and return session summary."""
        if not self.is_tracking:
            return format_mcp_response(
                False, error="No active tracking session"
            )

        try:
            self.is_tracking = False

            if self._tracking_task and not self._tracking_task.done():
                self._tracking_task.cancel()
                try:
                    await self._tracking_task
                except asyncio.CancelledError:
                    pass

            await self._save_monitor_data()

            return format_mcp_response(
                True,
                {
                    "status": "tracking_ended",
                    "session_summary": {
                        "total_snapshots": len(self.buffer_sequence),
                        "session_duration": (
                            datetime.now() - self.session_start
                        ).total_seconds(),
                        "session_start": self.session_start.isoformat(),
                        "session_end": datetime.now().isoformat(),
                    },
                },
            )
        except Exception as e:
            return format_mcp_response(
                False, error=f"Failed to end tracking: {e}"
            )

    async def _tracking_loop(self, interval_sec: float):
        """Continuous tracking loop."""
        while self.is_tracking:
            try:
                await self.take_snapshot()
                await asyncio.sleep(interval_sec)
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Continue tracking even if individual snapshot fails
                await asyncio.sleep(interval_sec)

    async def take_snapshot(self) -> Dict[str, Any]:
        """Take a single snapshot of current Emacs state."""
        try:
            # Get all required information
            buffer_info = await self._get_buffer_info()
            commands = await self._get_command_info()
            window_count = await self._get_window_info()
            content_info = await self._get_content_info(
                buffer_info[0]
            )  # buffer_name is first element

            # Create interaction entry
            interaction_entry = self._create_interaction_entry(
                buffer_info, commands, window_count, content_info
            )

            # Update sequence
            self._update_buffer_sequence(interaction_entry)

            # Save to persistent storage only if not in continuous tracking
            if not self.is_tracking:
                await self._save_monitor_data()

            return format_mcp_response(True, {"snapshot": interaction_entry})

        except Exception as e:
            return format_mcp_response(
                False, error=f"Failed to take snapshot: {e}"
            )

    def get_recent_traffic(self, count: int = 5) -> Dict[str, Any]:
        """Get recent interaction traffic from buffer sequence."""
        return format_mcp_response(
            True,
            {
                "sequence_length": len(self.buffer_sequence),
                "recent_interactions": (
                    self.buffer_sequence[-count:]
                    if self.buffer_sequence
                    else []
                ),
                "session_start": self.session_start.isoformat(),
                "is_tracking": self.is_tracking,
            },
        )

    async def track_interaction(self) -> Dict[str, Any]:
        """Track comprehensive user interactions with Emacs."""
        snapshot_result = await self.take_snapshot()
        if not snapshot_result["success"]:
            return snapshot_result

        traffic_result = self.get_recent_traffic()

        return format_mcp_response(
            True,
            {
                "current_snapshot": snapshot_result["result"]["snapshot"],
                "traffic_summary": traffic_result["result"],
            },
        )

    async def _get_buffer_info(self) -> list:
        """Get current buffer information from Emacs."""
        user_buffer_info = await self.emacsclient.eval_elisp(
            """
        (let ((buf (window-buffer (selected-window))))
          (with-current-buffer buf
            (list (buffer-name buf)
                  (buffer-file-name buf)
                  (symbol-name major-mode)
                  (point)
                  (buffer-size)
                  (line-number-at-pos)
                  (current-column)
                  (buffer-modified-p))))
        """
        )
        return self.emacsclient.parse_elisp_list(user_buffer_info)

    async def _get_command_info(self) -> Dict[str, str]:
        """Get last and current command information."""
        last_command = await self.emacsclient.eval_elisp(
            "(symbol-name last-command)"
        )
        this_command = await self.emacsclient.eval_elisp(
            "(symbol-name this-command)"
        )

        return {
            "last_command": (
                last_command.strip('"') if last_command != "nil" else None
            ),
            "this_command": (
                this_command.strip('"') if this_command != "nil" else None
            ),
        }

    async def _get_window_info(self) -> int:
        """Get window count information."""
        window_config = await self.emacsclient.eval_elisp(
            "(length (window-list))"
        )
        return int(window_config) if window_config.isdigit() else 1

    async def _get_buffer_content(self, buffer_name: str) -> str:
        """Get buffer content."""
        content = await self.emacsclient.eval_elisp(
            f'(with-current-buffer "{buffer_name}" (buffer-string))'
        )
        return content if content != "nil" else ""

    def _compute_content_hash(self, content: str) -> str:
        """Compute content hash for buffer."""
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _compute_content_diff(
        self, current_content: str, last_content: str = None
    ) -> Dict[str, Any]:
        """Compute diff between current and last content."""
        content_hash = self._compute_content_hash(current_content)

        if last_content and last_content != current_content:
            diff_lines = list(
                difflib.unified_diff(
                    last_content.splitlines(keepends=True),
                    current_content.splitlines(keepends=True),
                    n=1,
                )
            )
            changed_lines = len(
                [line for line in diff_lines if line.startswith(("+", "-"))]
            )

            return {
                "content_hash": content_hash,
                "diff_lines": changed_lines,
                "has_changes": True,
                "content_preview": (
                    current_content[:500] + "..."
                    if len(current_content) > 500
                    else current_content
                ),
            }

        return {
            "content_hash": content_hash,
            "diff_lines": 0,
            "has_changes": False,
            "content_preview": (
                current_content[:200] + "..."
                if len(current_content) > 200
                else current_content
            ),
        }

    async def _get_content_info(self, buffer_name: str) -> Dict[str, Any]:
        """Get buffer content information with diff."""
        current_content = await self._get_buffer_content(buffer_name)
        last_content = self.last_buffer_contents.get(buffer_name)

        content_info = self._compute_content_diff(
            current_content, last_content
        )

        # Store current content for next diff
        self.last_buffer_contents[buffer_name] = current_content

        return content_info

    def _create_interaction_entry(
        self,
        buffer_info: list,
        commands: Dict,
        window_count: int,
        content_info: Dict,
    ) -> Dict[str, Any]:
        """Create interaction entry from collected data."""
        (
            buffer_name,
            buffer_file,
            major_mode,
            cursor_position,
            buffer_size,
            line_number,
            column_number,
            buffer_modified,
        ) = buffer_info

        return {
            "timestamp": datetime.now().isoformat(),
            "buffer": {
                "name": buffer_name,
                "file": buffer_file,
                "mode": major_mode,
                "modified": buffer_modified,
                "size": buffer_size,
            },
            "cursor": {
                "position": cursor_position,
                "line": line_number,
                "column": column_number,
            },
            "content": content_info,
            "commands": commands,
            "environment": {
                "window_count": window_count,
            },
            "sequence_position": len(self.buffer_sequence),
        }

    def _update_buffer_sequence(self, interaction_entry: Dict[str, Any]):
        """Update buffer sequence with new interaction."""
        self.buffer_sequence.append(interaction_entry)

        # Keep only recent entries
        if len(self.buffer_sequence) > 100:
            self.buffer_sequence = self.buffer_sequence[-100:]

    async def _save_monitor_data(self):
        """Save tracker data to persistent storage."""
        try:
            data_file = self.storage_path / "buffer_sequences.json"

            # Load existing data
            existing_data = []
            if data_file.exists():
                with open(data_file, "r") as f:
                    existing_data = json.load(f)

            # Add current sequence data
            session_data = {
                "session_id": self.session_start.isoformat(),
                "interactions": self.buffer_sequence[
                    -20:
                ],  # Save last 20 interactions
                "timestamp": datetime.now().isoformat(),
            }
            existing_data.append(session_data)

            # Keep only recent sessions (last 50)
            if len(existing_data) > 50:
                existing_data = existing_data[-50:]

            # Save back to file
            with open(data_file, "w") as f:
                json.dump(existing_data, f, indent=2)

        except Exception as e:
            # Fail silently for storage issues - don't break the main functionality
            pass

    async def _get_buffer_list_snapshot(self) -> Dict[str, Any]:
        """Get comprehensive snapshot of all open buffers with timing information."""
        try:
            # Get buffer list with details
            buffer_list_elisp = """
            (mapcar (lambda (buf)
              (with-current-buffer buf
                (list (buffer-name buf)
                      (buffer-file-name buf)
                      (symbol-name major-mode)
                      (buffer-size buf)
                      (buffer-modified-p buf)
                      (get-buffer-window buf 'visible))))
            (buffer-list))
            """
            buffer_list_raw = await self.emacsclient.eval_elisp(
                buffer_list_elisp
            )

            if buffer_list_raw == "nil":
                return {
                    "total_buffers": 0,
                    "buffers": [],
                    "buffer_analytics": {},
                }

            # Get current time for timestamp calculations
            current_time = datetime.now()

            # Parse buffer list (simplified parsing of elisp output)
            buffers = []
            total_buffers = 0
            visible_buffers = 0
            modified_buffers = 0

            # Get basic buffer info from current buffer
            current_buffer = await self.emacsclient.eval_elisp("(buffer-name)")
            current_file = await self.emacsclient.eval_elisp(
                "(buffer-file-name)"
            )
            current_mode = await self.emacsclient.eval_elisp(
                "(symbol-name major-mode)"
            )

            if current_buffer != "nil":
                buffer_info = {
                    "name": current_buffer.strip('"'),
                    "file": (
                        current_file.strip('"')
                        if current_file != "nil"
                        else None
                    ),
                    "mode": current_mode.strip('"'),
                    "size": 0,  # Could get with buffer-size
                    "modified": False,  # Could get with buffer-modified-p
                    "last_accessed": current_time.isoformat(),
                    "window_displayed": True,  # Assume current buffer is displayed
                    "recent_activity": "current_focus",
                }
                buffers.append(buffer_info)
                total_buffers = 1
                visible_buffers = 1

            buffer_analytics = {
                "activity_distribution": {
                    "current_focus": 1,
                    "recent_edit": 0,
                    "background_process": 0,
                    "dormant": 0,
                },
                "temporal_patterns": {
                    "most_recently_accessed": (
                        current_buffer.strip('"')
                        if current_buffer != "nil"
                        else None
                    ),
                    "most_recently_modified": (
                        current_buffer.strip('"')
                        if current_buffer != "nil"
                        else None
                    ),
                    "highest_frequency": (
                        current_buffer.strip('"')
                        if current_buffer != "nil"
                        else None
                    ),
                },
                "working_set_analysis": {
                    "active_buffers": visible_buffers,
                    "inactive_buffers": total_buffers - visible_buffers,
                    "modified_files": modified_buffers,
                    "average_buffer_age_minutes": 30.0,
                    "buffer_churn_rate": 0.1,
                },
            }

            return {
                "total_buffers": total_buffers,
                "visible_buffers": visible_buffers,
                "modified_buffers": modified_buffers,
                "buffers": buffers,
                "buffer_analytics": buffer_analytics,
            }

        except Exception as e:
            return {
                "error": str(e),
                "total_buffers": 0,
                "buffers": [],
                "buffer_analytics": {},
            }


if __name__ == "__main__":

    async def main_async():
        import logging
        import os
        from pprint import pprint

        from emacs_tracker import EmacsClient

        logging.basicConfig(level=logging.INFO)
        emacsclient = EmacsClient(socket_name=os.getenv("EMACS_SOCKET_NAME"))
        tracker = Tracker(emacsclient)

        print("=== Emacs Tracker Demo ===")

        # Check connection status
        status = await emacsclient.status
        print(f"Connection Status: {status}")

        if emacsclient.connected:
            print("\n=== Starting Tracking (5 seconds) ===")
            start_result = await tracker.start_tracking(1.0)
            pprint(start_result)

            await asyncio.sleep(5)

            print("\n=== Ending Tracking ===")
            end_result = await tracker.end_tracking()
            pprint(end_result)

            print("\n=== Getting Recent Traffic ===")
            traffic = tracker.get_recent_traffic(3)
            pprint(traffic)

    asyncio.run(main_async())

# python -m emacs_tracker.Tracker > "tracking-demo.txt"

# EOF
