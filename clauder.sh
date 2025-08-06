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

# Run the update check script
bash "$UPDATE_SCRIPT"

# Run the security check script
bash "$SECURITY_SCRIPT"

# Display footer
clauder_footer

# Finally, run Claude with all forwarded arguments
claude "$@" 