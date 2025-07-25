#!/bin/bash

# Check if running in interactive terminal
if [[ -t 0 ]]; then
    INTERACTIVE=true
else
    INTERACTIVE=false
fi

# Function to safely exit or return based on interactive mode
safe_exit() {
    local exit_code=$1
    if [[ "$INTERACTIVE" == "true" ]]; then
        return $exit_code
    else
        exit $exit_code
    fi
}

# Function to display usage
usage() {
    echo "Usage: source activate.sh [target_project_path]"
    echo "Example: source activate.sh ./my-project"
    echo "Example: source activate.sh                    # Use current directory"
    echo ""
    echo "Arguments:"
    echo "  target_project_path    Directory to activate (default: current directory)"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --version  Show version information"
    safe_exit 1
}

# Function to display version
version() {
    echo "Claude Configuration Activator"
    echo "Version: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
    echo "Commit: $(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
    safe_exit 0
}

# Function to check if a directory exists
check_directory() {
    if [ ! -d "$1" ]; then
        echo "Error: Project directory '$1' does not exist."
        safe_exit 1
    fi
}

# Function to check if current directory is named 'clauder'
check_current_directory() {
    local current_dir_name=$(basename "$(pwd)")
    if [ "$current_dir_name" = "clauder" ]; then
        echo "Error: Cannot run clauder_activate.sh from within a directory named 'clauder'."
        echo "Please navigate to a different directory before running this script."
        safe_exit 1
    fi
}

# Function to create backup of existing .claude directory
create_backup() {
    local target_claude="$1"
    local target_project="$2"
    
    if [ ! -d "$target_claude" ]; then
        return 0  # No existing .claude directory to backup
    fi
    
    # Create .claude-backup directory if it doesn't exist
    local backup_dir="$target_project/.claude-backup"
    if [ ! -d "$backup_dir" ]; then
        mkdir -p "$backup_dir"
    fi
    
    # Generate timestamp in lowercase-dashed format (including seconds)
    local timestamp=$(date +%Y-%m-%d-%H-%M-%S | tr '[:upper:]' '[:lower:]')
    local backup_name="$backup_dir/$timestamp"
    
    echo "Creating backup of existing .claude directory..."
    echo "Backup location: $backup_name"
    
    # Copy existing .claude directory to backup
    if cp -r "$target_claude" "$backup_name" 2>/dev/null; then
        echo "✓ Backup created successfully"
        
        # Clean up old backups (keep only 10 most recent)
        cleanup_old_backups "$backup_dir"
    else
        echo "✗ Failed to create backup"
        return 1
    fi
    
    return 0
}

# Function to clean up old backups (keep only 10 most recent)
cleanup_old_backups() {
    local backup_dir="$1"
    
    # Get list of backup directories sorted by modification time (newest first)
    local backups=($(find "$backup_dir" -maxdepth 1 -type d -name "20*" -printf "%T@ %p\n" | sort -nr | cut -d' ' -f2-))
    
    # Remove backups beyond the 10th one
    if [ ${#backups[@]} -gt 10 ]; then
        echo "Cleaning up old backups (keeping 10 most recent)..."
        for ((i=10; i<${#backups[@]}; i++)); do
            local old_backup="${backups[$i]}"
            echo "Removing old backup: $(basename "$old_backup")"
            rm -rf "$old_backup"
        done
    fi
}

# Function to check for existing .claude files that would be overwritten
check_existing_files() {
    local source_claude="$1"
    local target_claude="$2"
    local files_to_overwrite=()
    
    if [ ! -d "$source_claude" ]; then
        echo "Error: Source .claude directory does not exist."
        return 1
    fi
    
    if [ -d "$target_claude" ]; then
        # Check which files from source would overwrite existing files in target
        while IFS= read -r -d '' source_file; do
            # Get relative path from source
            local relative_path="${source_file#$source_claude/}"
            local target_file="$target_claude/$relative_path"
            
            # Check if target file exists
            if [ -f "$target_file" ]; then
                files_to_overwrite+=("$relative_path")
            fi
        done < <(find "$source_claude" -type f -print0 2>/dev/null)
    fi
    
    if [ ${#files_to_overwrite[@]} -gt 0 ]; then
        echo "Warning: The following files will be overwritten:"
        printf '  %s\n' "${files_to_overwrite[@]}"
        echo ""
        echo -n "Do you want to replace these existing files? (y/N): "
        read -r reply
        echo
        if [[ ! $reply =~ ^[Yy]$ ]]; then
            echo "Operation cancelled."
            return 1
        fi
        echo "Proceeding with replacement..."
    fi
    
    return 0
}

# Function to copy .claude folder
copy_claude_folder() {
    # Check if CLAUDER_DIR environment variable is set
    if [[ -z "$CLAUDER_DIR" ]]; then
        echo "Error: CLAUDER_DIR environment variable is not set."
        echo "Please run clauder_install.sh first within the 'clauder' directory to set up the environment."
        safe_exit 1
    fi
    
    local source_claude="$CLAUDER_DIR/.claude"
    local target_project="$1"
    local target_claude="$target_project/.claude"
    
    # Check if source .claude exists
    if [ ! -d "$source_claude" ]; then
        echo "Error: Source .claude directory does not exist."
        safe_exit 1
    fi
    
    # Check if target project exists
    check_directory "$target_project"
    
    # Note: Even if target is current directory, we still check and replace files as needed
    
    # Create backup of existing .claude directory if it exists
    create_backup "$target_claude" "$target_project"
    
    # Check for existing files and prompt for approval
    check_existing_files "$source_claude" "$target_claude"
    if [ $? -ne 0 ]; then
        return 0
    fi
    
    # Create target .claude directory if it doesn't exist
    if [ ! -d "$target_claude" ]; then
        echo "Creating .claude directory in $target_project..."
        mkdir -p "$target_claude"
    fi
    
    # Copy all files from source .claude to target .claude
    echo "Source directory: $source_claude"
    echo "Target directory: $target_claude"
    echo "Copying .claude files to $target_claude..."
    
    # Track successful and failed copies
    local successful_copies=()
    local failed_copies=()
    
    # Copy each file individually to track success/failure
    while IFS= read -r -d '' source_file; do
        # Get relative path from source
        local relative_path="${source_file#$source_claude/}"
        local target_file="$target_claude/$relative_path"
        
        # Create target directory if it doesn't exist
        local target_dir=$(dirname "$target_file")
        if [ ! -d "$target_dir" ]; then
            mkdir -p "$target_dir"
        fi
        
        # Copy the file
        if cp "$source_file" "$target_file" 2>/dev/null; then
            successful_copies+=("$relative_path")
        else
            failed_copies+=("$relative_path")
            echo "Failed to copy: $source_file -> $target_file" >&2
        fi
    done < <(find "$source_claude" -type f -print0 2>/dev/null)
    
    # Display results
    if [ ${#successful_copies[@]} -gt 0 ]; then
        echo "Successfully copied files:"
        printf '  ✓ %s\n' "${successful_copies[@]}"
    fi
    
    if [ ${#failed_copies[@]} -gt 0 ]; then
        echo "Failed to copy files:"
        printf '  ✗ %s\n' "${failed_copies[@]}"
    fi
    
    if [ ${#failed_copies[@]} -eq 0 ]; then
        echo "All files copied successfully."
    else
        echo "Some files could not be copied, but continuing with activation..."
    fi
    
    echo "Successfully activated Claude configuration in $target_project"
    echo "You can now use Claude in this project with your custom configuration."
}

# Main script logic
main() {
    # Check if current directory is named 'clauder'
    check_current_directory
    
    # Check if help or version is requested
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        usage
    fi
    
    if [ "$1" = "-v" ] || [ "$1" = "--version" ]; then
        version
    fi
    
    # Get the target project path (default to current directory if not provided)
    target_path="${1:-.}"
    
    # Copy the .claude folder
    copy_claude_folder "$target_path"
}

# Run main function with all arguments
main "$@"

# If running in interactive mode and this script was executed (not sourced),
# keep the terminal open by waiting for user input
if [[ "$INTERACTIVE" == "true" && "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo ""
    echo "Press Enter to continue..."
    read -r
fi
