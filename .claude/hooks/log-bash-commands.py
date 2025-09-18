#!/usr/bin/env python3
"""
Log bash commands to a log file.
This script is called after bash tool use to log the command and description.
"""

import json
import sys
import os
from datetime import datetime


def load_preferences():
    """Load preferences from preferences.json file."""
    try:
        prefs_path = '.claude/preferences.json'
        if os.path.exists(prefs_path):
            with open(prefs_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception:
        return {}


def main():
    """Main function to log bash commands."""
    try:
        # Check if bash command logging is enabled
        preferences = load_preferences()
        logging_enabled = preferences.get('logging', {}).get('bash_commands', {}).get('enabled', False)
        
        if not logging_enabled:
            # Exit early if logging is disabled
            sys.exit(0)
        
        # Read input from stdin
        data = json.load(sys.stdin)
        tool_input = data.get('tool_input', {})
        command = tool_input.get('command', '')
        description = tool_input.get('description', 'No description')
        
        # Create logs directory if it doesn't exist
        logs_dir = '.claude/logs'
        os.makedirs(logs_dir, exist_ok=True)
        
        # Format the log entry
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} - {command} - {description}\n--------------------------------\n"
        
        # Write to bash-logs.txt
        log_file = os.path.join(logs_dir, 'bash-logs.txt')
        with open(log_file, 'a') as f:
            f.write(log_entry)
        
        # Exit successfully
        sys.exit(0)
        
    except Exception as e:
        # Log error but don't block the operation
        print(f"Error in log-bash-commands: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 