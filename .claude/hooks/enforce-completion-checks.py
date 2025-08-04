#!/usr/bin/env python3
import json
import sys
import subprocess
import os
from utils.trace_decision import log_decision

# Helper function to check if file should be ignored
def should_ignore_file(file_path):
    path_parts = file_path.split('/')
    # Check for .claude/logs at any nesting level
    for i in range(len(path_parts) - 1):
        if path_parts[i] == '.claude' and path_parts[i + 1] == 'logs':
            return True
    return False

# Check if there are any uncommitted changes
try:
    # Check for staged changes
    staged_result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
    # Check for unstaged changes
    unstaged_result = subprocess.run(['git', 'diff', '--quiet'], capture_output=True)
    # Check for untracked files
    untracked_result = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], capture_output=True, text=True)
    
    # Get all modified files to check if any are not in .claude/logs
    all_modified_files = []
    
    if staged_result.returncode != 0:
        staged_files = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True)
        staged_file_list = staged_files.stdout.strip().split('\n') if staged_files.stdout.strip() else []
        all_modified_files.extend([f for f in staged_file_list if not should_ignore_file(f)])
    
    if unstaged_result.returncode != 0:
        unstaged_files = subprocess.run(['git', 'diff', '--name-only'], capture_output=True, text=True)
        unstaged_file_list = unstaged_files.stdout.strip().split('\n') if unstaged_files.stdout.strip() else []
        all_modified_files.extend([f for f in unstaged_file_list if not should_ignore_file(f)])
    
    if untracked_result.stdout.strip():
        untracked_files = untracked_result.stdout.strip().split('\n') if untracked_result.stdout.strip() else []
        all_modified_files.extend([f for f in untracked_files if not should_ignore_file(f)])
    
    has_remaining_changes = len(all_modified_files) > 0
    
    if has_remaining_changes:
        # Check if HISTORY.md and SPECIFICATIONS.md exist at root level
        history_exists = os.path.exists('HISTORY.md')
        specs_exists = os.path.exists('SPECIFICATIONS.md')
        
        if history_exists or specs_exists:
            # Check if HISTORY.md or SPECIFICATIONS.md are in the modified files
            history_modified = 'HISTORY.md' in all_modified_files
            specs_modified = 'SPECIFICATIONS.md' in all_modified_files
            
            # If there are remaining changes and either file exists but hasn't been updated, enforce their update
            if has_remaining_changes and ((history_exists and not history_modified) or (specs_exists and not specs_modified)):
                missing_updates = []
                if history_exists and not history_modified:
                    missing_updates.append("HISTORY.md")
                if specs_exists and not specs_modified:
                    missing_updates.append("SPECIFICATIONS.md")
                
                output = {
                    "continue": True,
                    "stopReason": "Documentation updates required.",
                    "suppressOutput": True,
                    "decision": "block",
                    "reason": f"Changes detected but {', '.join(missing_updates)} not updated. You MUST update these files before proceeding. HISTORY.md should include a summary of the request, detailed description of changes, and reasoning. SPECIFICATIONS.md should reflect all latest specifications."
                }
                log_decision(output, operation_type="documentation_updates_decision")
                print(json.dumps(output))
                sys.exit(2)
        
        # If no documentation files to update, require commit
        output = {
            "continue": True,
            "stopReason": "Commit required.",
            "suppressOutput": True,
            "decision": "block",
            "reason": "Uncommitted changes detected. Please commit your changes with '[claude] <summary>' format before proceeding, including a meaningful summary and an extensive description of the changes."
        }
        log_decision(output, operation_type="commit_required_decision")
        print(json.dumps(output))
        sys.exit(2)
    
except subprocess.CalledProcessError as e:
    print(f"Error checking git status: {e}", file=sys.stderr)
    sys.exit(1)

# Allow the prompt to proceed with the additional context
sys.exit(0)