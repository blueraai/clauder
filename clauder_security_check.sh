#!/bin/bash

# Script to check if a project is safe for indexing
# Returns 0 (safe) or 1 (unsafe) based on presence of sensitive files/directories

set -e

# Check if running in interactive terminal
if [[ -t 0 ]]; then
    INTERACTIVE=true
else
    INTERACTIVE=false
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to run the Python security checker
check_patterns() {
    local project_dir="${1:-.}"
    
    # Get the directory where this script is located
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local python_script="$script_dir/.claude/hooks/prevent-learning-secrets.py"
    
    # Check if Python script exists
    if [[ ! -f "$python_script" ]]; then
        print_status $RED "Error: Python security checker not found at $python_script"
        return 1
    fi
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_status $RED "Error: python3 is required but not installed"
        return 1
    fi
    
    # Run the Python script and capture exit code
    python3 "$python_script" "$project_dir" --standalone --json
    exit_code=$?
    
    # Handle exit codes 1 and 2 by killing current command but not crashing terminal
    if [[ $exit_code -eq 1 || $exit_code -eq 2 ]]; then
        # Kill the current process group (current command) but not the terminal
        kill -TERM 0 2>/dev/null || true
        return $exit_code
    elif [[ $exit_code -ne 0 ]]; then
        # For other non-zero exit codes, just return them normally
        return $exit_code
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [project_directory]"
    echo ""
    echo "Checks if a project directory is safe for indexing by looking for sensitive files/directories."
    echo ""
    echo "Arguments:"
    echo "  project_directory    Directory to check (default: current directory)"
    echo ""
    echo "Exit codes:"
    echo "  0 - Project is safe for indexing"
    echo "  1 - Project is NOT safe for indexing (kills current command)"
    echo "  2 - Security violation detected (kills current command)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Check current directory"
    echo "  $0 /path/to/project   # Check specific directory"
}

# Function to safely exit or return based on interactive mode
safe_exit() {
    local exit_code=$1
    if [[ "$INTERACTIVE" == "true" ]]; then
        # For exit codes 1 and 2, return "Aborting.." instead of the exit code
        if [[ $exit_code -eq 1 || $exit_code -eq 2 ]]; then
            echo "Aborting.."
            return 0
        else
            return $exit_code
        fi
    else
        # For exit codes 1 and 2, kill the current command but don't crash terminal
        if [[ $exit_code -eq 1 || $exit_code -eq 2 ]]; then
            echo "Aborting.."
            # Kill the current process group (current command) but not the terminal
            kill -TERM 0 2>/dev/null || true
            exit $exit_code
        else
            exit $exit_code
        fi
    fi
}

# Function to exit with error (kills current command for codes 1/2, otherwise crashes)
crash_on_failure() {
    local exit_code=$1
    # For exit codes 1 and 2, kill the current command but don't crash terminal
    if [[ $exit_code -eq 1 || $exit_code -eq 2 ]]; then
        # Kill the current process group (current command) but not the terminal
        kill -TERM 0 2>/dev/null || true
        exit $exit_code
    else
        exit $exit_code
    fi
}

# Main script logic
main() {
    # Check for help flag
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        show_usage
        safe_exit 0
    fi
    
    # Get project directory (default to current directory)
    local project_dir="${1:-.}"
    
    # Validate directory exists
    if [[ ! -d "$project_dir" ]]; then
        print_status $RED "Error: Directory '$project_dir' does not exist"
        safe_exit 1
    fi
    
    # Run the safety check
    check_patterns "$project_dir"
    if [ $? -ne 0 ]; then
        crash_on_failure 1
    fi
}

# Run main function with all arguments
main "$@"

# If running in interactive mode and this script was executed (not sourced),
# keep the terminal open by waiting for user input
if [[ "$INTERACTIVE" == "true" && "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo ""
    echo "Security check complete. Press Enter to continue..."
    read -r
fi
