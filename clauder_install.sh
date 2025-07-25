#!/bin/bash

# Script to define clauder aliases in shell configuration files
# Detects the appropriate config file and adds aliases for the current project

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

# Function to detect all available shell configuration files
detect_shell_configs() {
    local configs=()
    
    # Check for all possible shell configuration files
    for config in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
        if [[ -f "$config" ]]; then
            configs+=("$config")
        fi
    done
    
    echo "${configs[@]}"
}

# Function to create aliases
create_aliases() {
    local config_file="$1"
    local project_dir="$2"
    
    # Get absolute paths
    local project_abs_path=$(realpath "$project_dir")
    local activate_script="$project_abs_path/clauder_activate.sh"
    local security_script="$project_abs_path/clauder_security_check.sh"
    
    # Check if scripts exist
    if [[ ! -f "$activate_script" ]]; then
        print_status $RED "Error: clauder_activate.sh not found at $activate_script"
        return 1
    fi
    
    if [[ ! -f "$security_script" ]]; then
        print_status $RED "Error: clauder_security_check.sh not found at $security_script"
        return 1
    fi
    
    # Create backup of config file
    local backup_file="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    cp "$config_file" "$backup_file"
    print_status $NC "📋 Created backup: $backup_file"
    
    # Remove existing clauder aliases and CLAUDER_DIR export if they exist
    local temp_file=$(mktemp)
    grep -v "clauder_footer()\|alias clauder_\|alias clauder=\|export CLAUDER_DIR\|# Clauder project aliases" "$config_file" > "$temp_file"
    
    # Add new aliases and environment variable
    cat >> "$temp_file" << EOF
# Clauder project aliases
export CLAUDER_DIR="$project_abs_path"
alias clauder_activate='source "$activate_script"'
alias clauder_security_check='source "$security_script"'
clauder_footer() { local footer_content="\$(cat "$project_abs_path/assets/clauder_footer.txt")"; echo -e "\$footer_content"; }
alias clauder='cat "$project_abs_path/assets/clauder_banner.txt" && source "$project_abs_path/clauder_update_check.sh" && clauder_security_check && clauder_footer && claude'
EOF
    
    # Replace original file
    mv "$temp_file" "$config_file"
    
    print_status $NC "✅ Added clauder aliases to $config_file"
    print_status $DARK_GRAY "   export CLAUDER_DIR='$project_abs_path'"
    print_status $DARK_GRAY "   alias clauder_activate='source $activate_script'"
    print_status $DARK_GRAY "   alias clauder_security_check='source $security_script'"
    print_status $DARK_GRAY "   clauder_footer() { local footer_content=\"\$(cat "$project_abs_path/assets/clauder_footer.txt")\"; echo -e \"\$footer_content\"; }"
    print_status $DARK_GRAY "   alias clauder='cat "$project_abs_path/assets/clauder_banner.txt" && source "$project_abs_path/clauder_update_check.sh" && clauder_security_check && clauder_footer && claude'"
    
    return 0
}

# Function to source the configuration file
source_config() {
    local config_file="$1"
    local current_shell=$(basename "$SHELL")
    
    if [[ "$current_shell" == "zsh" ]]; then
        source "$config_file" 2>/dev/null || return 1
    elif [[ "$current_shell" == "bash" ]]; then
        source "$config_file" 2>/dev/null || return 1
    else
        return 1
    fi
    
    return 0
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [project_directory]"
    echo ""
    echo "Defines clauder aliases in shell configuration files and sources them."
    echo ""
    echo "Arguments:"
    echo "  project_directory    Directory containing clauder scripts (default: current directory)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Use current directory"
    echo "  $0 /path/to/clauder   # Use specific directory"
}

# Main script logic
main() {
    # Check for help flag
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    # Get project directory (default to current directory)
    local project_dir="${1:-.}"
    
    # Validate directory exists
    if [[ ! -d "$project_dir" ]]; then
        print_status $RED "Error: Directory '$project_dir' does not exist"
        exit 1
    fi
    
    print_status $BLUE "🔍 Detecting shell configuration files..."
    
    # Detect all shell configuration files
    local config_files=($(detect_shell_configs))
    
    if [[ ${#config_files[@]} -eq 0 ]]; then
        print_status $RED "Error: No shell configuration files found"
        print_status $RED "Please create one of: ~/.zshrc, ~/.bashrc, ~/.bash_profile, or ~/.profile"
        exit 1
    fi
    
    print_status $NC "📁 Found ${#config_files[@]} configuration file(s):"
    for config_file in "${config_files[@]}"; do
        print_status $DARK_GRAY "   - $config_file"
    done
    
    # Create aliases in all config files
    print_status $BLUE "🔧 Creating clauder aliases in all configuration files..."
    local success_count=0
    for config_file in "${config_files[@]}"; do
        print_status $NC "Processing: $config_file"
        if create_aliases "$config_file" "$project_dir"; then
            ((success_count++))
            print_status $NC "✅ Successfully processed $config_file"
        else
            print_status $RED "❌ Failed to process $config_file"
        fi
    done
    
    if [[ $success_count -eq 0 ]]; then
        print_status $RED "Error: Failed to create aliases in any configuration file"
        exit 1
    fi
    
    print_status $NC "✅ Successfully created aliases in $success_count configuration file(s)"
    
    # Source the current shell's configuration
    local current_shell=$(basename "$SHELL")
    local current_config=""
    
    if [[ "$current_shell" == "zsh" && -f "$HOME/.zshrc" ]]; then
        current_config="$HOME/.zshrc"
    elif [[ "$current_shell" == "bash" && -f "$HOME/.bashrc" ]]; then
        current_config="$HOME/.bashrc"
    elif [[ "$current_shell" == "bash" && -f "$HOME/.bash_profile" ]]; then
        current_config="$HOME/.bash_profile"
    elif [[ -f "$HOME/.profile" ]]; then
        current_config="$HOME/.profile"
    fi
    
    if [[ -n "$current_config" ]]; then
        print_status $BLUE "🔄 Attempting to source $current_config..."
        if source_config "$current_config" 2>/dev/null; then
            print_status $NC "✅ Configuration sourced successfully"
        else
            print_status $YELLOW "⚠️  Could not source configuration automatically. Please restart your shell or manually source one of the configuration files"
        fi
    else
        print_status $YELLOW "⚠️  Please restart your shell to activate the aliases"
    fi
    
    print_status $GREEN "> Clauder aliases successfully installed and activated."
    print_status $BLUE "You can now use:"
    print_status $DARK_GRAY "  clauder_activate [project_path]        # Activate clauder in a project (default: current directory if not provided)"
    print_status $DARK_GRAY "  clauder_security_check [project_path]  # Check project security (default: current directory if not provided)"
    print_status $DARK_GRAY "  clauder                                # Start Claude Code with security checks"
}

# Run main function with all arguments
main "$@"
