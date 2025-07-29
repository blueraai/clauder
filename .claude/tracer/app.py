#!/usr/bin/env python3
"""
Claude Trace Viewer - Web application to display trace logs in real-time
"""

import sqlite3
import json
import time
import os
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
SCRIPT_DIR = Path(__file__).parent.parent.parent
DB_PATH = SCRIPT_DIR / '.claude' / 'logs' / 'trace.sqlite'
PORT = 4441

def get_db_connection():
    """Get a database connection."""
    if not DB_PATH.exists():
        return None
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error:
        return None

def table_exists(conn, table_name):
    """Check if a table exists in the database."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        return cursor.fetchone() is not None
    except sqlite3.Error:
        return False

def get_trace_data(limit=100):
    """Get trace data from the database."""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        # Check if table exists
        if not table_exists(conn, 'trace_logs'):
            return []
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, operation_type, data, created_at
            FROM trace_logs
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        data = []
        for row in rows:
            try:
                json_data = json.loads(row[3]) if row[3] else {}
            except json.JSONDecodeError:
                json_data = {"raw_data": row[3]}
            
            data.append({
                'id': row[0],
                'timestamp': row[1],
                'operation_type': row[2] or 'unknown',
                'data': json_data,
                'created_at': row[4]
            })
        
        return data
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def get_stats():
    """Get database statistics."""
    conn = get_db_connection()
    if not conn:
        return {"total_events": 0, "last_event": None, "db_exists": False, "table_exists": False}
    
    try:
        # Check if table exists
        table_exists_flag = table_exists(conn, 'trace_logs')
        if not table_exists_flag:
            return {"total_events": 0, "last_event": None, "db_exists": True, "table_exists": False}
        
        cursor = conn.cursor()
        
        # Total events
        cursor.execute('SELECT COUNT(*) FROM trace_logs')
        total_events = cursor.fetchone()[0]
        
        # Last event
        cursor.execute('''
            SELECT timestamp, operation_type 
            FROM trace_logs 
            ORDER BY id DESC 
            LIMIT 1
        ''')
        last_row = cursor.fetchone()
        last_event = {
            'timestamp': last_row[0],
            'operation_type': last_row[1]
        } if last_row else None
        
        return {
            "total_events": total_events,
            "last_event": last_event,
            "db_exists": True,
            "table_exists": True
        }
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"total_events": 0, "last_event": None, "db_exists": True, "table_exists": False}
    finally:
        conn.close()

@app.route('/')
def index():
    """Main page."""
    stats = get_stats()
    return render_template('index.html', stats=stats)

@app.route('/api/events')
def api_events():
    """API endpoint to get trace events."""
    limit = int(request.args.get('limit', 100))
    data = get_trace_data(limit)
    return jsonify(data)

@app.route('/api/stats')
def api_stats():
    """API endpoint to get database statistics."""
    return jsonify(get_stats())

@app.route('/api/stream')
def stream():
    """Server-Sent Events stream for live updates."""
    def generate():
        last_id = 0
        
        while True:
            conn = get_db_connection()
            if conn:
                try:
                    # Check if table exists
                    if not table_exists(conn, 'trace_logs'):
                        # Send a status message
                        yield f"data: {json.dumps({'type': 'status', 'message': 'Waiting for database table...'})}\n\n"
                        time.sleep(2)
                        continue
                    
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT id, timestamp, operation_type, data, created_at
                        FROM trace_logs
                        WHERE id > ?
                        ORDER BY id ASC
                    ''', (last_id,))
                    
                    new_rows = cursor.fetchall()
                    
                    for row in new_rows:
                        try:
                            json_data = json.loads(row[3]) if row[3] else {}
                        except json.JSONDecodeError:
                            json_data = {"raw_data": row[3]}
                        
                        event_data = {
                            'id': row[0],
                            'timestamp': row[1],
                            'operation_type': row[2] or 'unknown',
                            'data': json_data,
                            'created_at': row[4]
                        }
                        
                        yield f"data: {json.dumps(event_data)}\n\n"
                        last_id = row[0]
                
                except sqlite3.Error as e:
                    print(f"Database error in stream: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Database error: {e}'})}\n\n"
                
                finally:
                    conn.close()
            else:
                # Database doesn't exist yet
                yield f"data: {json.dumps({'type': 'status', 'message': 'Waiting for database to be created...'})}\n\n"
            
            time.sleep(1)  # Check for updates every second
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print(f"Starting Claude Trace Viewer...")
    print(f"Database: {DB_PATH}")
    print(f"Web App: http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    print()
    
    app.run(host='0.0.0.0', port=PORT, debug=False) 