#!/bin/bash

# clauder_trace.sh - Trace viewer for Claude operations
# Usage: ./clauder_trace.sh [--help]

# Assume script is run from project root
TRACER_DIR=".claude/tracer"
DB_PATH=".claude/logs/trace.sqlite"

show_help() {
    echo "clauder_trace.sh - Trace viewer for Claude operations"
    echo ""
    echo "Usage:"
    echo "  ./clauder_trace.sh"
    echo ""
    echo "Options:"
    echo "  --help     Show this help message"
    echo ""
    echo "The trace viewer will display all Claude operations in real-time."
}

start_tracer() {
    echo "Starting Claude Trace Viewer in new terminal..."
    echo "Database: $DB_PATH"
    echo "Web App: http://localhost:4441"
    echo ""
    
    # Check if database exists
    if [ ! -f "$DB_PATH" ]; then
        echo "Warning: No trace database found at $DB_PATH"
        echo "The database will be created when Claude operations are performed."
        echo ""
    fi
    
    # Detect OS and open new terminal accordingly
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - use Terminal.app
        osascript -e "
        tell application \"Terminal\"
            do script \"python3 .claude/tracer/app.py\"
            set custom title of front window to \"Claude Trace Viewer\"
        end tell
        "
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - try different terminal emulators
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --title="Claude Trace Viewer" -- bash -c "python3 .claude/tracer/app.py; exec bash"
        elif command -v konsole &> /dev/null; then
            konsole --title "Claude Trace Viewer" -e bash -c "python3 .claude/tracer/app.py; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -title "Claude Trace Viewer" -e bash -c "python3 .claude/tracer/app.py; exec bash"
        else
            echo "No supported terminal found. Starting in background..."
            python3 .claude/tracer/app.py &
        fi
    elif [[ "$OSTYPE" == "msys"* ]] || [[ "$OSTYPE" == "cygwin"* ]] || [[ "$OSTYPE" == "win32"* ]]; then
        # Windows - try different terminal options
        if command -v cmd.exe &> /dev/null; then
            start cmd.exe /k "python .claude/tracer/app.py"
        elif command -v powershell.exe &> /dev/null; then
            start powershell.exe -Command "python .claude/tracer/app.py; Read-Host 'Press Enter to close'"
        elif command -v wt.exe &> /dev/null; then
            # Windows Terminal
            wt.exe -w 0 new-tab --title "Claude Trace Viewer" -- python .claude/tracer/app.py
        else
            echo "No supported terminal found. Starting in background..."
            python .claude/tracer/app.py &
        fi
    else
        # Fallback for other systems
        echo "Starting in background..."
        python3 .claude/tracer/app.py &
    fi
    
    echo "Trace viewer started! Check the new terminal window."
    echo "Web interface available at: http://localhost:4441"
    echo ""
    echo "To stop the viewer, close the terminal window or press Ctrl+C in that window."
}

case "${1:-}" in
    --help|-h)
        show_help
        ;;
    "")
        start_tracer
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac 