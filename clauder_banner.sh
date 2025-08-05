#!/bin/bash

# Script to display clauder banner with animated random characters
# Characters appear randomly until the full banner is revealed

# Colors for output
NC='\033[0m' # No Color

# Function to animate banner
animate_banner() {
    local banner_file="$1"
    
    if [[ ! -f "$banner_file" ]]; then
        echo "Error: Banner file not found: $banner_file"
        return 1
    fi
    
    # Read the banner content
    local banner_content=$(cat "$banner_file")
    local banner_lines=()
    local line_lengths=()
    
    # Split banner into lines and get line lengths
    while IFS= read -r line; do
        banner_lines+=("$line")
        line_lengths+=(${#line})
    done <<< "$banner_content"
    
    local total_lines=${#banner_lines[@]}
    local total_chars=0
    
    # Count total characters
    for length in "${line_lengths[@]}"; do
        ((total_chars += length))
    done
    
    # Create arrays to track revealed characters
    local revealed_positions=()
    local revealed_count=0
    
    # Initialize revealed positions array
    for ((i=0; i<total_chars; i++)); do
        revealed_positions+=("0")
    done
    
    # Clear screen once and position cursor at top
    clear
    echo -en "\033[H"
    
    # Calculate timing for 0.15-second animation (lightning fast)
    local target_frames=8   # 8 frames for 0.15 seconds
    local sleep_time=0.018  # ~55 FPS for ultra smooth animation
    
    # Animation loop
    local frame=0
    local chars_per_frame=$((total_chars / target_frames + 1))
    
    while [[ $revealed_count -lt $total_chars && $frame -lt $target_frames ]]; do
        # Reveal multiple characters per frame for faster completion
        local chars_to_reveal=$chars_per_frame
        if [[ $((revealed_count + chars_to_reveal)) -gt $total_chars ]]; then
            chars_to_reveal=$((total_chars - revealed_count))
        fi
        
        # Reveal characters
        for ((i=0; i<chars_to_reveal; i++)); do
            # Find next unrevealed position
            local random_pos=$((RANDOM % total_chars))
            local attempts=0
            while [[ ${revealed_positions[$random_pos]} -eq 1 && $attempts -lt 10 ]]; do
                random_pos=$((RANDOM % total_chars))
                ((attempts++))
            done
            
            if [[ ${revealed_positions[$random_pos]} -eq 0 ]]; then
                revealed_positions[$random_pos]=1
                ((revealed_count++))
            fi
        done
        
        # Build the entire output and display it all at once
        local full_output=""
        local char_index=0
        for ((line_idx=0; line_idx<total_lines; line_idx++)); do
            local line="${banner_lines[$line_idx]}"
            local line_length=${#line}
            local line_output=""
            
            for ((char_idx=0; char_idx<line_length; char_idx++)); do
                if [[ $char_index -lt ${#revealed_positions[@]} && ${revealed_positions[$char_index]} -eq 1 ]]; then
                    line_output+="${line:$char_idx:1}"
                else
                    line_output+=" "
                fi
                ((char_index++))
            done
            
            full_output+="$line_output"$'\n'
        done
        
        # Position cursor at top and display all at once
        echo -en "\033[H"
        echo -en "$full_output"
        
        # Sleep for calculated time
        sleep $sleep_time
        ((frame++))
    done
    
    # Clear the entire console and display the final static content
    clear
    echo -e "$banner_content"
}

# Main execution
if [[ $# -eq 0 ]]; then
    # Default banner file location
    banner_file="assets/clauder_banner.txt"
else
    banner_file="$1"
fi

animate_banner "$banner_file" 