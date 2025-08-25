#!/usr/bin/env python3
"""
emacs-tracker - User interaction tracking for Emacs MCP Server
"""

from .EmacsClient import EmacsClient
from .Tracker import Tracker

__version__ = "0.1.0"
__all__ = ["Tracker", "EmacsClient"]
