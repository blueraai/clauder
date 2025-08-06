#!/bin/bash

# Script to run the Claude tracer with argument forwarding
# This ensures cross-shell compatibility and proper argument handling

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if CLAUDER_DIR is set, otherwise use script directory
if [[ -z "$CLAUDER_DIR" ]]; then
    CLAUDER_DIR="$SCRIPT_DIR"
fi

# Check if .claude directory exists in current directory
if [[ ! -d ".claude" ]]; then
    echo "Error: No .claude directory found in current directory"
    echo "Please run clauder_activate first to set up the Claude configuration."
    exit 1
fi

# Path to the tracer app
TRACER_APP=".claude/tracer/app.py"

# Check if the tracer app exists
if [[ ! -f "$TRACER_APP" ]]; then
    echo "Error: Tracer app not found at $TRACER_APP"
    echo "Please run clauder_activate first to set up the Claude configuration."
    exit 1
fi

# Forward all arguments to the Python tracer app
python3 "$TRACER_APP" "$@" 