#!/usr/bin/env python3
import json
import sys
import os
from utils.trace_decision import log_decision

# ANSI color codes
YELLOW = '\033[93m'
LIGHT_BLUE = '\033[94m'
LIGHT_GRAY = '\033[37m'
RESET = '\033[0m'

# Load input from stdin
try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

# Extract tool information
tool_name = input_data.get("tool_name", "Unknown")
tool_input = input_data.get("tool_input", {})

# Check for safe commands that don't require approval
command = tool_input.get("command", "")
if command.startswith("say ") or command.startswith("ls "):
    sys.exit(0)

# Always block and require human approval
output = {
    "continue": True,
    "stopReason": "[Flagged for human review] Risk detected. This action may be destructive beyond recovery, or may have significant consequences, and needs explicit human approval.",
    "suppressOutput": False,
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": f"[Flagged for human review] Risk detected. This action may be destructive beyond recovery, or may have significant consequences, and needs your explicit approval."
    }
}
log_decision(output, operation_type="human_approval_decision")
print(json.dumps(output))
sys.exit(2)
