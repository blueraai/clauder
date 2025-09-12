#!/bin/bash

# Script to run Claude with all security checks and customizations
# This ensures cross-shell compatibility and proper argument handling

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if CLAUDER_DIR is set, otherwise use script directory
if [[ -z "$CLAUDER_DIR" ]]; then
    CLAUDER_DIR="$SCRIPT_DIR"
fi

# Paths to various scripts and files
BANNER_SCRIPT="$CLAUDER_DIR/clauder_banner.sh"
BANNER_FILE="$CLAUDER_DIR/assets/clauder_banner.txt"
UPDATE_SCRIPT="$CLAUDER_DIR/clauder_update_check.sh"
SECURITY_SCRIPT="$CLAUDER_DIR/clauder_security_check.sh"
FOOTER_FILE="$CLAUDER_DIR/assets/clauder_footer.txt"

# Function to display footer
clauder_footer() {
    if [[ -f "$FOOTER_FILE" ]]; then
        local footer_content="$(cat "$FOOTER_FILE")"
        echo -e "$footer_content"
    fi
}

# Function to check if colors are supported
colors_supported() {
    # Check if we're in a terminal and colors are supported
    if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && [[ $(tput colors 2>/dev/null) -ge 8 ]]; then
        return 0
    else
        return 1
    fi
}

# Function to print text in gray
print_gray() {
    if colors_supported; then
        echo -n "$(tput setaf 8)$1$(tput sgr0)"
    else
        echo -n "$1"
    fi
}

# Function to source shell configuration files
source_shell_configs() {
    # print_gray "Sourcing terminal configuration.."
    # echo ""
    
    # Define shell configuration files
    local shell_files=("$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile" "$HOME/.zshrc")
    
    for shell_file in "${shell_files[@]}"; do
        if [ -f "$shell_file" ]; then
            local display_path="${shell_file/#$HOME/~}"
            if . "$shell_file" >/dev/null 2>&1; then
                # Silently source successful files
                :
            else
                print_gray "  ⚠ Failed to source $display_path"
            fi
        fi
    done
    
    # Reset color to default
    if colors_supported; then
        echo -n "$(tput sgr0)"
    fi
    echo ""
}

# Check if required files exist
if [[ ! -f "$BANNER_SCRIPT" ]]; then
    echo "Error: Banner script not found at $BANNER_SCRIPT"
    exit 1
fi

if [[ ! -f "$UPDATE_SCRIPT" ]]; then
    echo "Error: Update check script not found at $UPDATE_SCRIPT"
    exit 1
fi

if [[ ! -f "$SECURITY_SCRIPT" ]]; then
    echo "Error: Security check script not found at $SECURITY_SCRIPT"
    exit 1
fi

# Run the banner script
if [[ -f "$BANNER_FILE" ]]; then
    bash "$BANNER_SCRIPT" "$BANNER_FILE"
fi

# Source shell configuration files before update check
source_shell_configs

# Run the update check script
bash "$UPDATE_SCRIPT"

# Source shell configuration files after update check
source_shell_configs

# Run the security check script and capture exit code
bash "$SECURITY_SCRIPT"
security_exit_code=$?

# Check if security check failed with codes 1 or 2
if [[ $security_exit_code -eq 1 || $security_exit_code -eq 2 ]]; then
    echo "Security check failed. Aborting execution."
    exit $security_exit_code
fi

# Display footer
clauder_footer

# Display active MCP servers
display_mcp_servers() {
    echo ""
    print_gray "Active MCP servers:"
    echo ""
    if command -v claude >/dev/null 2>&1; then
        local mcp_output=$(claude mcp list 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$mcp_output" ]; then
            local server_names=$(echo "$mcp_output" | grep -E '^[a-zA-Z0-9_-]+:' | sed 's/:.*$//' | tr '\n' ' ')
            if [ -n "$server_names" ]; then
                print_gray "⚭ $server_names"
                echo ""
                echo ""
            else
                print_gray "⌀ (none)"
                echo ""
                echo ""
            fi
        else
            print_gray "⌀ (none)"
            echo ""
            echo ""
        fi
    else
        print_gray "⌀ (none)"
        echo ""
        echo ""
    fi
    
}

display_mcp_servers

# Finally, run Claude with all forwarded arguments
claude "$@" 