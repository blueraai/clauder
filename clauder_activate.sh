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
    echo "Usage: clauder_activate [target_project_path] [--expansions <name> <name> <name>]"
    echo "Example: clauder_activate ./my-project"
    echo "Example: clauder_activate                    # Use current directory"
    echo "Example: clauder_activate . --expansions frontend-dev backend-dev"
    echo ""
    echo "Arguments:"
    echo "  target_project_path    Directory to activate (default: current directory)"
    echo ""
    echo "Options:"
    echo "  --expansions          Apply expansion packs (space-separated list)"
    echo "  -h, --help            Show this help message"
    echo "  -v, --version         Show version information"
    safe_exit 0
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

# Function to check if we're trying to activate in the clauder directory itself
check_clauder_directory_activation() {
    local target_project="$1"
    local clauder_dir="${CLAUDER_DIR:-$(dirname "$(realpath "$0")")}"
    
    # Get absolute paths for comparison
    local target_abs_path=$(realpath "$target_project")
    local clauder_abs_path=$(realpath "$clauder_dir")
    
    # Check if target project is the clauder directory itself
    if [ "$target_abs_path" = "$clauder_abs_path" ]; then
        echo "Error: Cannot activate clauder in the clauder directory itself."
        echo "Please run clauder_activate from a different project directory."
        echo "Target: $target_abs_path"
        echo "Clauder: $clauder_abs_path"
        safe_exit 1
    fi
    
    # Also check if we're currently in the clauder directory
    local current_dir=$(pwd)
    local current_abs_path=$(realpath "$current_dir")
    
    if [ "$current_abs_path" = "$clauder_abs_path" ]; then
        echo "Error: Cannot run clauder_activate from within the clauder directory."
        echo "Please navigate to a different project directory first."
        echo "Current: $current_abs_path"
        echo "Clauder: $clauder_abs_path"
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
    # Use macOS compatible find command
    local backups=($(find "$backup_dir" -maxdepth 1 -type d -name "20*" -exec stat -f "%m %N" {} \; | sort -nr | cut -d' ' -f2-))
    
    # Remove backups beyond the 10th one
    if [ ${#backups[@]} -gt 10 ]; then
        local backups_to_remove=()
        i=10
        while [ $i -lt ${#backups[@]} ]; do
            backups_to_remove+=("$(basename "${backups[$i]}")")
            i=$((i + 1))
        done
        
        echo "Found ${#backups_to_remove[@]} old backup(s) to remove (keeping 10 most recent):"
        printf '  %s\n' "${backups_to_remove[@]}"
        echo ""
        echo -n "Do you want to remove these old backups? (y/N): "
        read -r reply
        echo
        
        if [[ $reply =~ ^[Yy]$ ]]; then
            echo "Removing old backups..."
            i=10
            while [ $i -lt ${#backups[@]} ]; do
                local old_backup="${backups[$i]}"
                echo "Removing: $(basename "$old_backup")"
                rm -rf "$old_backup"
                i=$((i + 1))
            done
            echo "✓ Old backups removed successfully"
        else
            echo "Skipping cleanup of old backups"
        fi
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
        echo "Warning: The following files will be backed up and overwritten:"
        printf '  %s\n' "${files_to_overwrite[@]}"
        echo ""
        echo -n "Do you want to backup and replace these existing files? (y/N): "
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

# Function to merge JSON files deeply
merge_json_files() {
    local target_file="$1"
    local source_file="$2"
    
    # Check if both files exist
    if [ ! -f "$target_file" ] || [ ! -f "$source_file" ]; then
        echo "Debug: Missing files - target: $target_file, source: $source_file" >&2
        return 1
    fi
    
    # Use jq to merge JSON files if available
    if command -v jq >/dev/null 2>&1; then
        # Create a temporary file for the merged result
        local temp_file=$(mktemp)
        
        # Check if source file is essentially empty (template)
        local source_content=$(jq -c '.' "$source_file" 2>/dev/null)
        if [ "$source_content" = "{}" ] || [ "$source_content" = "[]" ]; then
            rm -f "$temp_file"
            return 0
        fi
        
        # Use Python for deep merge
        if python3 -c "
import json
import sys

def deep_merge(base, override):
    if isinstance(base, dict) and isinstance(override, dict):
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], (dict, list)) and isinstance(value, type(result[key])):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    elif isinstance(base, list) and isinstance(override, list):
        # Always concatenate arrays, even if override is empty
        return base + override
    else:
        # If override is empty/null, keep base value
        if override is None or override == {} or override == []:
            return base
        else:
            return override

try:
    with open('$target_file', 'r') as f:
        base = json.load(f)
    with open('$source_file', 'r') as f:
        override = json.load(f)
    
    merged = deep_merge(base, override)
    
    with open('$temp_file', 'w') as f:
        json.dump(merged, f, indent=2)
    
    sys.exit(0)
except Exception as e:
    print(f'Debug: Python merge failed: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
            # Replace the target file with the merged content
            mv "$temp_file" "$target_file"
            return 0
        else
            # If Python merge fails, fall back to simple concatenation
            rm -f "$temp_file"
            echo "Warning: Python merge failed, using fallback method" >&2
            return 1
        fi
    else
        # Fallback: simple concatenation for JSON files
        # This is not ideal but works for simple cases
        echo "Debug: jq not available" >&2
        return 1
    fi
}

# Function to merge text files by preserving custom configurations
merge_text_files() {
    local target_file="$1"
    local source_file="$2"
    
    # Check if both files exist
    if [ ! -f "$target_file" ] || [ ! -f "$source_file" ]; then
        return 1
    fi
    
    # Create a temporary file for the merged result
    local temp_file=$(mktemp)
    
    # Start with target file content (preserve existing custom configurations)
    cat "$target_file" > "$temp_file"
    
    # Add a newline if the target file doesn't end with one
    if [ -s "$target_file" ] && [ "$(tail -c1 "$target_file" | wc -l)" -eq 0 ]; then
        echo "" >> "$temp_file"
    fi
    
    # Read source file line by line and add only non-duplicate lines
    while IFS= read -r line; do
        # Skip empty lines
        if [ -n "$line" ]; then
            # Check if line already exists in target file (case-sensitive)
            if ! grep -q "^$(echo "$line" | sed 's/[[\.*^$()+?{|]/\\&/g')$" "$target_file"; then
                echo "$line" >> "$temp_file"
            fi
        fi
    done < "$source_file"
    
    # Replace target file with merged content
    mv "$temp_file" "$target_file"
    return 0
}

# Function to copy expansion pack
copy_expansion_pack() {
    local expansion_name="$1"
    local target_project="$2"
    local target_claude="$target_project/.claude"
    local clauder_dir="${CLAUDER_DIR:-$(dirname "$(realpath "$0")")}"
    local expansion_dir="$clauder_dir/.claude-expansion-packs/$expansion_name"
    
    # Check if expansion pack exists
    if [ ! -d "$expansion_dir" ]; then
        echo "Warning: Expansion pack '$expansion_name' does not exist."
        return 1
    fi
    
    echo "Applying expansion pack: $expansion_name"
    
    # Files that need special merging
    local mergeable_files=(".exclude_security_checks" ".ignore" ".immutable" "preferences.json" "settings.json")
    
    # Copy all files from expansion pack
    while IFS= read -r -d '' source_file; do
        # Get relative path from source
        local relative_path="${source_file#$expansion_dir/}"
        local target_file="$target_claude/$relative_path"
        
        # Create target directory if it doesn't exist
        local target_dir=$(dirname "$target_file")
        if [ ! -d "$target_dir" ]; then
            mkdir -p "$target_dir"
        fi
        
        # Check if this is a mergeable file
        local filename=$(basename "$relative_path")
        local should_merge=false
        
        for mergeable_file in "${mergeable_files[@]}"; do
            if [ "$filename" = "$mergeable_file" ]; then
                should_merge=true
                break
            fi
        done
        
        # Handle file copying/merging
        if [ "$should_merge" = true ]; then
            # For mergeable files, create target if it doesn't exist, then merge
            if [ ! -f "$target_file" ]; then
                # Create empty target file for merging
                touch "$target_file"
            fi
            
            # Merge the file
            if [[ "$filename" == *.json ]]; then
                if merge_json_files "$target_file" "$source_file"; then
                    echo "  ✓ Merged: $relative_path"
                else
                    echo "  ⚠ Merged (fallback): $relative_path"
                fi
            else
                if merge_text_files "$target_file" "$source_file"; then
                    echo "  ✓ Merged: $relative_path"
                else
                    echo "  ⚠ Merged (fallback): $relative_path"
                fi
            fi
        else
            # Copy the file normally
            if cp -f "$source_file" "$target_file" 2>/dev/null; then
                echo "  ✓ Copied: $relative_path"
            else
                echo "  ✗ Failed to copy: $relative_path"
            fi
        fi
    done < <(find "$expansion_dir" -type f -print0 2>/dev/null)
    
    # Add expansion name to .claude.expansion_packs if not already present
    local expansion_packs_file="$target_claude/.expansion_packs"
    if [ ! -f "$expansion_packs_file" ]; then
        touch "$expansion_packs_file"
    fi
    
    # Check if expansion name is already in the file
    if ! grep -q "^$expansion_name$" "$expansion_packs_file" 2>/dev/null; then
        echo "$expansion_name" >> "$expansion_packs_file"
        echo "  ✓ Added to expansion packs list"
    else
        echo "  ℹ Already in expansion packs list"
    fi
    
    echo "✓ Expansion pack '$expansion_name' applied successfully"
}

# Function to apply expansion packs
apply_expansion_packs() {
    local target_project="$1"
    shift
    local expansions=("$@")
    
    if [ ${#expansions[@]} -eq 0 ]; then
        return 0
    fi
    
    echo ""
    echo "Applying expansion packs..."
    
    for expansion in "${expansions[@]}"; do
        copy_expansion_pack "$expansion" "$target_project"
    done
    
    echo ""
    echo "All expansion packs applied."
}

# Function to apply previously applied expansion packs
apply_previous_expansions() {
    local target_project="$1"
    local target_claude="$target_project/.claude"
    local expansion_packs_file="$target_claude/.expansion_packs"
    
    if [ ! -f "$expansion_packs_file" ]; then
        return 0
    fi
    
    # Read expansion packs from file
    local previous_expansions=()
    while IFS= read -r line; do
        # Skip empty lines and comments
        if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
            previous_expansions+=("$line")
        fi
    done < "$expansion_packs_file"
    
    if [ ${#previous_expansions[@]} -gt 0 ]; then
        echo ""
        echo "Applying previously installed expansion packs..."
        for expansion in "${previous_expansions[@]}"; do
            copy_expansion_pack "$expansion" "$target_project"
        done
        echo ""
        echo "All previous expansion packs applied."
    fi
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
    
    # Change to target project directory for backup operations
    cd "$target_project"
    
    # Check if target .claude directory exists
    if [ ! -d "$target_claude" ]; then
        # Create target .claude directory if it doesn't exist
        echo "Creating .claude directory in $target_project..."
        mkdir -p "$target_claude"
    else
        # Backup existing .claude directory and check for existing files
        create_backup "$target_claude" "$target_project"
        
        # Check for existing files and prompt for approval
        check_existing_files "$source_claude" "$target_claude"
        if [ $? -ne 0 ]; then
            return 0
        fi
    fi
    
    # Copy all files from source .claude to target .claude
    echo "Source directory: $source_claude"
    echo "Target directory: $target_claude"
    echo "Copying .claude files to $target_claude..."
    
    # Files that need special merging to preserve existing configurations
    local mergeable_files=(".exclude_security_checks" ".ignore" ".immutable" "preferences.json") # settings.json is not mergeable to ensure working operations upon auto-updates, for custom settings use .claude/settings.local.json instead
    
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
        
        # Check if this is a mergeable file
        local filename=$(basename "$relative_path")
        local should_merge=false
        
        for mergeable_file in "${mergeable_files[@]}"; do
            if [ "$filename" = "$mergeable_file" ]; then
                should_merge=true
                break
            fi
        done
        
        # Handle file copying/merging
        if [ "$should_merge" = true ] && [ -f "$target_file" ]; then
            # Merge with existing configuration to preserve custom settings
            if [[ "$filename" == *.json ]]; then
                if merge_json_files "$target_file" "$source_file"; then
                    successful_copies+=("$relative_path (merged)")
                else
                    failed_copies+=("$relative_path (merge failed)")
                fi
            else
                if merge_text_files "$target_file" "$source_file"; then
                    successful_copies+=("$relative_path (merged)")
                else
                    failed_copies+=("$relative_path (merge failed)")
                fi
            fi
        else
            # Copy the file normally (overwrite if it doesn't exist or isn't mergeable)
            if cp -f "$source_file" "$target_file" 2>/dev/null; then
                successful_copies+=("$relative_path")
            else
                failed_copies+=("$relative_path")
                echo "Failed to copy: $source_file -> $target_file" >&2
            fi
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
    
    # Parse arguments
    local target_path="."
    local expansions=()
    local i=1
    
    while [ $i -le $# ]; do
        case "${!i}" in
            -h|--help)
                usage
                ;;
            -v|--version)
                version
                ;;
            --expansions)
                # Collect expansion names
                i=$((i + 1))
                while [ $i -le $# ] && [[ "${!i}" != -* ]]; do
                    expansions+=("${!i}")
                    i=$((i + 1))
                done
                continue
                ;;
            -*)
                echo "Error: Unknown option '${!i}'"
                usage
                ;;
            *)
                if [ "$target_path" = "." ]; then
                    target_path="${!i}"
                else
                    echo "Error: Multiple target paths specified"
                    usage
                fi
                ;;
        esac
        i=$((i + 1))
    done
    
    # Check if we're trying to activate in the clauder directory itself
    check_clauder_directory_activation "$target_path"
    
    # Copy the .claude folder
    copy_claude_folder "$target_path"
    
    # Apply previously applied expansion packs first
    apply_previous_expansions "$target_path"
    
    # Apply new expansion packs if specified (these will override previous ones)
    if [ ${#expansions[@]} -gt 0 ]; then
        apply_expansion_packs "$target_path" "${expansions[@]}"
    fi
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
