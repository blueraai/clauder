#!/usr/bin/env python3
"""
Log events to a local SQLlite database file, for auditing and debugging.
This script is called on all Claude operations.
"""

import json
import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path


def ensure_logs_directory():
    """Ensure the logs directory exists."""
    logs_dir = Path('.claude/logs')
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def init_database_if_needed(db_path):
    """Initialize the SQLite database with the trace table only if it doesn't exist."""
    # Only initialize if the database file doesn't exist
    if not db_path.exists():
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create the trace table
        cursor.execute('''
            CREATE TABLE trace_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation_type TEXT,
                data TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()


def log_to_database(db_path, data):
    """Log the trace data to the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Extract operation type if available in the data
    operation_type = data.get('hook_event_name', data.get('type', 'unknown'))
    
    # Insert the trace data
    cursor.execute('''
        INSERT INTO trace_logs (timestamp, operation_type, data)
        VALUES (?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        operation_type,
        json.dumps(data, ensure_ascii=False)
    ))
    
    conn.commit()
    conn.close()


def main():
    """Main function to log bash commands."""
    try:
        # Read input from stdin
        data = json.load(sys.stdin)
        
        # Ensure logs directory exists
        logs_dir = ensure_logs_directory()
        
        # Initialize database only if needed
        db_path = logs_dir / 'trace.sqlite'
        init_database_if_needed(db_path)
        
        # Log to SQLite database
        log_to_database(db_path, data)
        
        # Exit successfully
        sys.exit(0)
        
    except Exception as e:
        # Log error but don't block the operation
        print(f"Error in trace: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 