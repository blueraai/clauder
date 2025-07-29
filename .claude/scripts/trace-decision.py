#!/usr/bin/env python3
"""
Log decision events to a local SQLite database file, for auditing and debugging.
This module exports a function that can be imported and used by other hooks.
"""

import json
import sqlite3
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


def log_decision(data, operation_type=None):
    """
    Log decision data to the SQLite database.
    
    Args:
        data: The data to log (will be JSON serialized)
        operation_type: Optional operation type (defaults to 'decision')
    
    Returns:
        bool: True if successful, False if failed
    """
    try:
        # Ensure logs directory exists
        logs_dir = ensure_logs_directory()
        
        # Initialize database only if needed
        db_path = logs_dir / 'trace.sqlite'
        init_database_if_needed(db_path)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Use provided operation_type or default to 'decision'
        if operation_type is None:
            operation_type = 'decision'
        
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
        
        return True
        
    except Exception as e:
        # Log error but don't block the operation
        print(f"Error in trace_decision: {e}", file=os.sys.stderr)
        return True