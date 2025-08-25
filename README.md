<!-- ---
!-- Timestamp: 2025-08-26 01:32:58
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/emacs_tracker/README.md
!-- --- -->

# Emacs Tracker

MCP server for tracking Emacs user interactions and buffer sequences.

Note: This package is still in a conceptual stage.

## Overview

Emacs can work as a sensor for developer activity, providing non-verbal context for AI agents to understand user interactions and anticipate needs.

## Demo Snapshot Data

# python -m emacs_tracker.Tracker > "./docs/tracking-demo.txt"

``` plaintext
=== Emacs Tracker Demo ===
Connection Status: {'socket_exists': True, 'is_connected': True}

=== Starting Tracking (5 seconds) ===
{'result': {'interval_seconds': 1.0,
            'session_id': '2025-08-25T14:39:49.056716',
            'status': 'tracking_started'},
 'success': True}

=== Ending Tracking ===
{'result': {'session_summary': {'session_duration': 5.030378,
                                'session_end': '2025-08-25T14:39:54.087114',
                                'session_start': '2025-08-25T14:39:49.056716',
                                'total_snapshots': 5},
            'status': 'tracking_ended'},
 'success': True}

=== Getting Recent Traffic ===
{'result': {'is_tracking': False,
            'recent_interactions': [{'buffer': {'file': None,
                                                'mode': 'vterm-mode',
                                                'modified': True,
                                                'name': 'tracker-14:23:26',
                                                'size': 2214},
                                     'commands': {'last_command': 'vterm-send-return',
                                                  'this_command': 'nil'},
                                     'content': {'content_hash': '80a48271',
                                                 'content_preview': '#("(.env-3.11) '
                                                                    '(wsl) '
                                                                    'emacs_tracker '
                                                                    '$ python '
                                                                    '-m '
                                                                    'emacs_tracker.Tracker '
                                                                    '> '
                                                                    '\\"tracking-de\\nmo.txt\\"\\n<frozen '
                                                                    'runpy>:128: '
                                                                    'RuntimeWarning: '
                                                                    "'emacs_tracker.Tracker' "
                                                                    'found in '
                                                                    'sys.modules\\n '
                                                                    'after '
                                                                    'import of '
                                                                    'packa...',
                                                 'diff_lines': 0,
                                                 'has_changes': False},
                                     'cursor': {'column': 0,
                                                'line': 42,
                                                'position': 2172},
                                     'environment': {'window_count': 2},
                                     'sequence_position': 2,
                                     'timestamp': '2025-08-25T14:39:51.169386'},
                                    {'buffer': {'file': None,
                                                'mode': 'vterm-mode',
                                                'modified': True,
                                                'name': 'tracker-14:23:26',
                                                'size': 2215},
                                     'commands': {'last_command': 'vterm--self-insert',
                                                  'this_command': 'nil'},
                                     'content': {'content_hash': 'e63f6d89',
                                                 'content_preview': '#("(.env-3.11) '
                                                                    '(wsl) '
                                                                    'emacs_tracker '
                                                                    '$ python '
                                                                    '-m '
                                                                    'emacs_tracker.Tracker '
                                                                    '> '
                                                                    '\\"tracking-de\\nmo.txt\\"\\n<frozen '
                                                                    'runpy>:128: '
                                                                    'RuntimeWarning: '
                                                                    "'emacs_tracker.Tracker' "
                                                                    'found in '
                                                                    'sys.modules\\n '
                                                                    'after '
                                                                    'import of '
                                                                    'package '
                                                                    "'emacs_tracker', "
                                                                    'but prior '
                                                                    'to '
                                                                    'execution '
                                                                    'of '
                                                                    "'emacs_track\\ner.Tracker'; "
                                                                    'this may '
                                                                    'result in '
                                                                    'unpredictable '
                                                                    'behaviour\\nINFO:root:Emacs '
                                                                    'server '
                                                                    'socket '
                                                                    'exists at '
                                                                    '/home/ywatanabe/.emacs.d/server/server: '
                                                                    '\\nFalse\\nINFO:root:Emacs '
                                                                    'server '
                                                                    'connection '
                                                                    'active: '
                                                                    'False\\nTraceback '
                                                                    '(most '
                                                                    'recent '
                                                                    'call '
                                                                    'last):\\n  '
                                                                    'File '
                                                                    '\\"...',
                                                 'diff_lines': 9,
                                                 'has_changes': True},
                                     'cursor': {'column': 1,
                                                'line': 42,
                                                'position': 2173},
                                     'environment': {'window_count': 2},
                                     'sequence_position': 3,
                                     'timestamp': '2025-08-25T14:39:52.199594'},
                                    {'buffer': {'file': None,
                                                'mode': 'vterm-mode',
                                                'modified': True,
                                                'name': 'tracker-14:23:26',
                                                'size': 2219},
                                     'commands': {'last_command': 'vterm--self-insert',
                                                  'this_command': 'nil'},
                                     'content': {'content_hash': 'edaa90da',
                                                 'content_preview': '#("(.env-3.11) '
                                                                    '(wsl) '
                                                                    'emacs_tracker '
                                                                    '$ python '
                                                                    '-m '
                                                                    'emacs_tracker.Tracker '
                                                                    '> '
                                                                    '\\"tracking-de\\nmo.txt\\"\\n<frozen '
                                                                    'runpy>:128: '
                                                                    'RuntimeWarning: '
                                                                    "'emacs_tracker.Tracker' "
                                                                    'found in '
                                                                    'sys.modules\\n '
                                                                    'after '
                                                                    'import of '
                                                                    'package '
                                                                    "'emacs_tracker', "
                                                                    'but prior '
                                                                    'to '
                                                                    'execution '
                                                                    'of '
                                                                    "'emacs_track\\ner.Tracker'; "
                                                                    'this may '
                                                                    'result in '
                                                                    'unpredictable '
                                                                    'behaviour\\nINFO:root:Emacs '
                                                                    'server '
                                                                    'socket '
                                                                    'exists at '
                                                                    '/home/ywatanabe/.emacs.d/server/server: '
                                                                    '\\nFalse\\nINFO:root:Emacs '
                                                                    'server '
                                                                    'connection '
                                                                    'active: '
                                                                    'False\\nTraceback '
                                                                    '(most '
                                                                    'recent '
                                                                    'call '
                                                                    'last):\\n  '
                                                                    'File '
                                                                    '\\"...',
                                                 'diff_lines': 12,
                                                 'has_changes': True},
                                     'cursor': {'column': 5,
                                                'line': 42,
                                                'position': 2177},
                                     'environment': {'window_count': 2},
                                     'sequence_position': 4,
                                     'timestamp': '2025-08-25T14:39:53.232210'}],
            'sequence_length': 5,
            'session_start': '2025-08-25T14:39:49.056716'},
 'success': True}
```

# Emacs Tracker

MCP server for tracking Emacs user interactions and buffer sequences.

## Installation

```bash
pip install emacs-tracker
```

## Setup

Add to Claude Desktop settings:
```json
{
  "mcpServers": {
    "emacs-tracker": {
      "command": "python",
      "args": ["-m", "emacs_tracker"]
    }
  }
}
```

## Usage

Start server:
```bash
python -m emacs_tracker
```

Set Emacs socket:
```bash
export EMACS_SOCKET_NAME="/tmp/emacs1000/server"
```

## MCP Tools

- `track_interaction` - Record current interaction
- `get_tracking_log` - Retrieve interaction history  
- `start_real_time_tracking` / `stop_real_time_tracking` - Continuous tracking
- `export_data` - Export to JSON/CSV
- `query_interaction_context` - Get current Emacs state
- `clear_data` - Clear stored data

## Python API

```python
import emacs_tracker
import os

client = emacs_tracker.EmacsClient(socket_name=os.getenv("EMACS_SOCKET_NAME"))
tracker = emacs_tracker.Tracker(client)

# Track single interaction
result = await tracker.track_interaction()

# Start continuous tracking  
await tracker.start_tracking(1.0)
await tracker.end_tracking()

```

## Configuration

Optional config file:
```json
{
  "tracking": {
    "interval": 1.0,
    "auto_save": true
  },
  "storage": {
    "path": "~/.cache/emacs_tracker"
  },
  "emacs": {
    "socket_name": null
  }
}
```

Run with config:
```bash
python -m emacs_tracker --config config.json
```

## Requirements

- Python 3.8+
- Emacs with emacsclient  
- Active Emacs server

## License

MIT

## Contact
yusuke.watanabe@scitex.ai

<!-- EOF -->