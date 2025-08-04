#!/usr/bin/env python3
"""
Log MCP commands to a log file.
This script is called after MCP tool use to log the complete command data.
"""

import json
import sys
import os
from datetime import datetime


def main():
    """Main function to log MCP commands."""
    try:
        # Read input from stdin
        data = json.load(sys.stdin)
        
        # Create logs directory if it doesn't exist
        logs_dir = '.claude/logs'
        os.makedirs(logs_dir, exist_ok=True)
        
        # Format the log entry with timestamp
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} - {json.dumps(data)}\n--------------------------------\n"
        
        # Write to mcp-logs.txt
        log_file = os.path.join(logs_dir, 'mcp-logs.txt')
        with open(log_file, 'a') as f:
            f.write(log_entry)
        
        # Exit successfully
        sys.exit(0)
        
    except Exception as e:
        # Log error but don't block the operation
        print(f"Error in log-mcp-commands: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 