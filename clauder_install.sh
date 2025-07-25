#!/bin/bash

# Script to define clauder aliases in shell configuration files
# Detects the appropriate config file and adds aliases for the current project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to detect the appropriate shell configuration file
detect_shell_config() {
    local shell_config=""
    
    # Check current shell
    local current_shell=$(basename "$SHELL")
    
    # Check for zsh
    if [[ "$current_shell" == "zsh" ]]; then
        if [[ -f "$HOME/.zshrc" ]]; then
            shell_config="$HOME/.zshrc"
        elif [[ -f "$HOME/.profile" ]]; then
            shell_config="$HOME/.profile"
        fi
    # Check for bash
    elif [[ "$current_shell" == "bash" ]]; then
        if [[ -f "$HOME/.bashrc" ]]; then
            shell_config="$HOME/.bashrc"
        elif [[ -f "$HOME/.bash_profile" ]]; then
            shell_config="$HOME/.bash_profile"
        elif [[ -f "$HOME/.profile" ]]; then
            shell_config="$HOME/.profile"
        fi
    fi
    
    # If no shell-specific config found, try common ones
    if [[ -z "$shell_config" ]]; then
        for config in "$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
            if [[ -f "$config" ]]; then
                shell_config="$config"
                break
            fi
        done
    fi
    
    echo "$shell_config"
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
    print_status $BLUE "📋 Created backup: $backup_file"
    
    # Remove existing clauder aliases and CLAUDER_DIR export if they exist
    local temp_file=$(mktemp)
    grep -v "alias clauder_\|alias clauder=\|export CLAUDER_DIR\|# Clauder project aliases" "$config_file" > "$temp_file"
    
    # Add new aliases and environment variable
    cat >> "$temp_file" << EOF
# Clauder project aliases
export CLAUDER_DIR="$project_abs_path"
alias clauder_activate='source "$activate_script"'
alias clauder_security_check='source "$security_script"'
alias clauder='cat "$project_abs_path/assets/clauder_banner.txt" && source "$project_abs_path/clauder_update_check.sh" && clauder_security_check && cat "$project_abs_path/assets/clauder_footer.txt" && claude'
EOF
    
    # Replace original file
    mv "$temp_file" "$config_file"
    
    print_status $GREEN "✅ Added clauder aliases to $config_file"
    print_status $GREEN "   export CLAUDER_DIR='$project_abs_path'"
    print_status $GREEN "   alias clauder_activate='source $activate_script'"
    print_status $GREEN "   alias clauder_security_check='source $security_script'"
    print_status $GREEN "   alias clauder='clauder_security_check && claude'"
}

# Function to source the configuration file
source_config() {
    local config_file="$1"
    local current_shell=$(basename "$SHELL")
    
    print_status $YELLOW "🔄 Sourcing $config_file..."
    
    if [[ "$current_shell" == "zsh" ]]; then
        source "$config_file"
    elif [[ "$current_shell" == "bash" ]]; then
        source "$config_file"
    else
        print_status $YELLOW "⚠️  Please manually source $config_file or restart your shell"
        return 1
    fi
    
    print_status $GREEN "✅ Configuration sourced successfully"
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
    
    print_status $YELLOW "🔍 Detecting shell configuration file..."
    
    # Detect shell configuration file
    local config_file=$(detect_shell_config)
    
    if [[ -z "$config_file" ]]; then
        print_status $RED "Error: No shell configuration file found"
        print_status $RED "Please create one of: ~/.zshrc, ~/.bashrc, ~/.bash_profile, or ~/.profile"
        exit 1
    fi
    
    print_status $GREEN "📁 Found configuration file: $config_file"
    
    # Create aliases
    print_status $YELLOW "🔧 Creating clauder aliases..."
    if ! create_aliases "$config_file" "$project_dir"; then
        exit 1
    fi
    
    # Source the configuration
    if ! source_config "$config_file"; then
        print_status $YELLOW "⚠️  Please restart your shell or manually source $config_file"
        exit 1
    fi
    
    print_status $GREEN "> Clauder aliases successfully installed and activated."
    print_status $GREEN "You can now use:"
    print_status $GREEN "  clauder_activate [project_path]        # Activate clauder in a project (default: current directory if not provided)"
    print_status $GREEN "  clauder_security_check [project_path]  # Check project security (default: current directory if not provided)"
    print_status $GREEN "  clauder                                # Start Claude Codewith security check"
}

# Run main function with all arguments
main "$@"
