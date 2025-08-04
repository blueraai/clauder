#!/usr/bin/env python3
"""
Log bash commands to a log file.
This script is called after bash tool use to log the command and description.
"""

import json
import sys
import os
from datetime import datetime


def main():
    """Main function to log bash commands."""
    try:
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