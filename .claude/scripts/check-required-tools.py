#!/usr/bin/env python3
"""
Check for required tools and git directory.
This script is called before user prompt submission to ensure required tools are available.
"""

import subprocess
import sys
import os
import json
from utils.trace_decision import log_decision

def main():
    """Main function to check required tools."""
    try:
        # Define required tools
        required_tools = ['git', 'jq']
        
        # Check if tools are available
        missing_tools = []
        for tool in required_tools:
            result = subprocess.run(['which', tool], capture_output=True)
            if result.returncode != 0:
                missing_tools.append(tool)
        
        # Check if .git/ directory exists
        git_dir_exists = os.path.exists('.git/')
        if not git_dir_exists:
            missing_tools.append('.git/ directory (run `git init` to create it)')
        
        # If any tools are missing, exit with error
        if missing_tools:
            missing_tools_str = ", ".join(missing_tools)
            output = {
                "continue": False,
                "stopReason": f"Missing required tools: {missing_tools_str}",
                "suppressOutput": False,
                "decision": "block",
                "reason": f"Missing required tools: {missing_tools_str}"
            }
            log_decision(output, operation_type="required_tools_decision")
            print(json.dumps(output))
            sys.exit(2)
        
        # All tools are available
        sys.exit(0)
        
    except Exception as e:
        # Log error and exit with error code
        output = {
            "continue": False,
            "stopReason": f"Error in check-required-tools: {e}",
            "suppressOutput": False,
            "decision": "block",
            "reason": f"Error in check-required-tools: {e}"
        }
        log_decision(output, operation_type="required_tools_error_decision")
        print(json.dumps(output))
        sys.exit(2)


if __name__ == "__main__":
    main() 