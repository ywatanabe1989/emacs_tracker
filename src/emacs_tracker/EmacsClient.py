#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-25 14:39:24 (ywatanabe)"
# File: /home/ywatanabe/proj/emacs_tracker/src/emacs_tracker/EmacsClient.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./emacs_tracker/src/emacs_tracker/EmacsClient.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Tracking Context tools for Emacs MCP Server.

These tools track user interaction patterns, buffer sequences, and editing workflows
to provide personalized AI assistance based on observed patterns.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


class EmacsClient:
    """Simple Emacs client for evaluating elisp expressions."""

    def __init__(self, socket_name: Optional[str] = None):
        self.socket_name = socket_name
        self._connected = False

    async def eval_elisp(
        self,
        expression: str,
        server: Optional[Union[Path, str]] = None,
    ) -> str:
        """Evaluate elisp expression using emacsclient."""
        server = (
            (str(server) if server is not None else None)
            or self.socket_name
            or os.getenv("EMACS_SOCKET_NAME")
            or "/tmp/emacs1000/server"
        )

        try:
            proc = await asyncio.create_subprocess_exec(
                "emacsclient",
                "--socket-name",
                server,
                "--eval",
                expression,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=5
            )

            if proc.returncode == 0:
                self._connected = True
                return stdout.decode().strip()
            else:
                self._connected = False
                return "nil"

        except Exception as e:
            logger.error(e)
            self._connected = False
            return "nil"

    async def _get_status(self, verbose=True):
        # Server Socket File
        exist_socket = os.path.exists(self.socket_name)
        msg_exist = (
            f"Emacs server socket exists at {self.socket_name}: {exist_socket}"
        )

        # Server Connection
        result = await self.eval_elisp("(+ 1 1)")
        is_connected = result == "2"
        msg_connected = f"Emacs server connection active: {is_connected}"

        # Logging
        if verbose:
            logging.info(msg_exist)
            logging.info(msg_connected)

        return {"socket_exists": exist_socket, "is_connected": is_connected}

    @property
    async def status(self):
        return await self._get_status(verbose=True)

    @property
    async def connected(self):
        status = await self._get_status(verbose=True)
        return status.get("is_connected")

    @classmethod
    def parse_elisp_list(cls, output: str):
        """Parse simple elisp list output."""
        if not output or output == "nil":
            return []

        # Remove outer parentheses
        content = output.strip()
        if content.startswith("(") and content.endswith(")"):
            content = content[1:-1]

        # Split by spaces, handling strings with quotes
        parts = []
        current = ""
        in_string = False

        for char in content:
            if char == '"':
                in_string = not in_string
                current += char
            elif char == " " and not in_string:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char

        if current:
            parts.append(current)

        # Clean up parts
        cleaned = []
        for part in parts:
            if part == "nil":
                cleaned.append(None)
            elif part == "t":
                cleaned.append(True)
            elif part.startswith('"') and part.endswith('"'):
                cleaned.append(part[1:-1])
            elif part.isdigit():
                cleaned.append(int(part))
            else:
                cleaned.append(part)

        return cleaned


if __name__ == "__main__":

    async def main_async():
        import os

        # from emacs_tracker import EmacsClient

        logging.basicConfig(level=logging.DEBUG)

        emacsclient = EmacsClient(socket_name=os.getenv("EMACS_SOCKET_NAME"))
        await emacsclient.status
        await emacsclient.connected

    asyncio.run(main_async())

# python -m emacs_tracker.EmacsClient

# EOF
