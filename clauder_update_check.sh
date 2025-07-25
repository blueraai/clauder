#!/bin/bash

# Script to check for clauder updates and handle the update process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
DARK_GRAY='\033[90m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if we're in a git repository
check_git_repo() {
    local dir="$1"
    if [[ -d "$dir/.git" ]]; then
        return 0
    else
        return 1
    fi
}

# Function to check for updates
check_for_updates() {
    local clauder_dir="$1"
    local current_dir="$2"
    
    if ! check_git_repo "$clauder_dir"; then
        print_status $YELLOW "⚠️  Clauder directory is not a git repository. Skipping update check."
        return 1
    fi
    
    # Change to clauder directory
    cd "$clauder_dir"
    
    # Fetch latest changes
    print_status $BLUE "🔍 Checking for updates..."
    git fetch origin main > /dev/null 2>&1 || {
        print_status $RED "❌ Failed to fetch updates from remote repository"
        cd "$current_dir"
        return 1
    }
    
    # Check if local is behind remote
    local local_commit=$(git rev-parse HEAD)
    local remote_commit=$(git rev-parse origin/main)
    
    if [[ "$local_commit" != "$remote_commit" ]]; then
        print_status $YELLOW "🔄 Update available for clauder!"
        print_status $BLUE "Local:  $(git rev-parse --short HEAD)"
        print_status $BLUE "Remote: $(git rev-parse --short origin/main)"
        cd "$current_dir"
        return 0
    else
        print_status $GREEN "✅ Clauder is up to date"
        cd "$current_dir"
        return 1
    fi
}

# Function to perform update
perform_update() {
    local clauder_dir="$1"
    local current_dir="$2"
    
    print_status $YELLOW "🔄 Updating clauder..."
    
    # Change to clauder directory
    cd "$clauder_dir"
    
    # Pull latest changes
    git pull origin main || {
        print_status $RED "❌ Failed to pull latest changes"
        return 1
    }
    
    print_status $GREEN "✅ Successfully pulled latest changes"
    
    # Reinstall clauder
    print_status $YELLOW "🔧 Reinstalling clauder..."
    source ./clauder_install.sh || {
        print_status $RED "❌ Failed to reinstall clauder"
        return 1
    }
    
    print_status $GREEN "✅ Clauder reinstalled successfully"
    
    # Return to original directory and activate
    cd "$current_dir"
    print_status $YELLOW "🔧 Activating clauder in current directory..."
    clauder_activate || {
        print_status $RED "❌ Failed to activate clauder"
        return 1
    }
    
    print_status $GREEN "✅ Clauder updated and activated successfully!"
    return 0
}

# Function to prompt user for update
prompt_for_update() {
    local clauder_dir="$1"
    local current_dir="$2"
    
    echo
    print_status $YELLOW "Would you like to update clauder? (y/n)"
    read -r response
    
    case "$response" in
        [yY]|[yY][eE][sS])
            perform_update "$clauder_dir" "$current_dir"
            return 0
            ;;
        [nN]|[nN][oO])
            print_status $BLUE "Skipping update. Continuing with current version..."
            return 1
            ;;
        *)
            print_status $RED "Invalid response. Skipping update."
            return 1
            ;;
    esac
}

# Main function
main() {
    local clauder_dir="${CLAUDER_DIR:-$(dirname "$(realpath "$0")")}"
    local current_dir="$(pwd)"
    
    # Display directory information
    print_status $DARK_GRAY "Clauder directory: $clauder_dir"
    print_status $DARK_GRAY "Project directory: $current_dir"
    
    # Check for updates
    if check_for_updates "$clauder_dir" "$current_dir"; then
        prompt_for_update "$clauder_dir" "$current_dir"
    fi
}

# Run main function
main "$@" 