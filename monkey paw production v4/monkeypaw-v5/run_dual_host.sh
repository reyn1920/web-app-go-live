#!/bin/bash
# Dual-Host Avatar Workflow for The Right Perspective
# Supports both male and female hosts with automatic selection

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/the_right_perspective_config.json"

# Function to load configuration
load_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "❌ Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    # Extract configuration using Python
    python3 -c "
import json
import sys
config = json.load(open('$CONFIG_FILE'))
print('CHANNEL_NAME=' + config['channel']['name'].replace(' ', '_'))
print('FEMALE_NAME=' + config['channel']['hosts']['female']['name'].replace(' ', '_'))
print('FEMALE_AVATAR=' + config['channel']['hosts']['female']['avatar_path'])
print('FEMALE_VOICE=' + config['channel']['hosts']['female']['voice_profile'])
print('FEMALE_X=' + str(config['channel']['hosts']['female']['head_position']['x']))
print('FEMALE_Y=' + str(config['channel']['hosts']['female']['head_position']['y']))
print('FEMALE_SCALE=' + str(config['channel']['hosts']['female']['head_position']['scale']))
print('MALE_NAME=' + config['channel']['hosts']['male']['name'].replace(' ', '_'))
print('MALE_AVATAR=' + config['channel']['hosts']['male']['avatar_path'])
print('MALE_VOICE=' + config['channel']['hosts']['male']['voice_profile'])
print('MALE_X=' + str(config['channel']['hosts']['male']['head_position']['x']))
print('MALE_Y=' + str(config['channel']['hosts']['male']['head_position']['y']))
print('MALE_SCALE=' + str(config['channel']['hosts']['male']['head_position']['scale']))
print('STUDIO_BG=' + config['channel']['backgrounds']['studio'])
print('NEWSROOM_BG=' + config['channel']['backgrounds']['newsroom'])
print('OFFICE_BG=' + config['channel']['backgrounds']['office'])
"
}

# Function to select host based on content type
select_host() {
    local content_type="$1"
    
    case "$content_type" in
        "breaking_news")
            echo "female"
            ;;
        "analysis")
            echo "male"
            ;;
        "commentary")
            echo "female"
            ;;
        *)
            echo "female"  # Default to female
            ;;
    esac
}

# Function to select background based on content type
select_background() {
    local content_type="$1"
    
    case "$content_type" in
        "breaking_news")
            echo "newsroom"
            ;;
        "analysis")
            echo "studio"
            ;;
        "commentary")
            echo "office"
            ;;
        *)
            echo "studio"  # Default to studio
            ;;
    esac
}

# Function to generate content template
generate_content() {
    local content_type="$1"
    local topic="$2"
    
    case "$content_type" in
        "breaking_news")
            echo "Breaking news: $topic. Here's what you need to know..."
            ;;
        "analysis")
            echo "Let's analyze the implications of $topic..."
            ;;
        "commentary")
            echo "From The Right Perspective, here's my take on $topic..."
            ;;
        *)
            echo "$topic"  # Use topic as-is
            ;;
    esac
}

# Main dual-host workflow
main() {
    local content_type="$1"
    local topic="$2"
    local custom_host="${3:-}"
    local custom_background="${4:-}"
    
    echo "🎬 The Right Perspective - Dual-Host Production"
    echo "📺 Content Type: $content_type"
    echo "📝 Topic: $topic"
    
    # Load configuration
    echo "📋 Loading configuration..."
    eval $(load_config)
    
    # Select host and background
    if [ -n "$custom_host" ]; then
        selected_host="$custom_host"
        echo "👤 Using custom host: $selected_host"
    else
        selected_host=$(select_host "$content_type")
        echo "👤 Auto-selected host: $selected_host"
    fi
    
    if [ -n "$custom_background" ]; then
        selected_bg="$custom_background"
        echo "🖼️ Using custom background: $selected_bg"
    else
        selected_bg=$(select_background "$content_type")
        echo "🖼️ Auto-selected background: $selected_bg"
    fi
    
    # Set host-specific variables
    if [ "$selected_host" = "female" ]; then
        HOST_NAME="$FEMALE_NAME"
        HOST_AVATAR="$FEMALE_AVATAR"
        HOST_VOICE="$FEMALE_VOICE"
        HEAD_X="$FEMALE_X"
        HEAD_Y="$FEMALE_Y"
        HEAD_SCALE="$FEMALE_SCALE"
    else
        HOST_NAME="$MALE_NAME"
        HOST_AVATAR="$MALE_AVATAR"
        HOST_VOICE="$MALE_VOICE"
        HEAD_X="$MALE_X"
        HEAD_Y="$MALE_Y"
        HEAD_SCALE="$MALE_SCALE"
    fi
    
    # Set background path
    case "$selected_bg" in
        "studio")
            BACKGROUND_PATH="$SCRIPT_DIR/$STUDIO_BG"
            ;;
        "newsroom")
            BACKGROUND_PATH="$SCRIPT_DIR/$NEWSROOM_BG"
            ;;
        "office")
            BACKGROUND_PATH="$SCRIPT_DIR/$OFFICE_BG"
            ;;
        *)
            BACKGROUND_PATH="$SCRIPT_DIR/$STUDIO_BG"
            ;;
    esac
    
    # Generate content
    CONTENT=$(generate_content "$content_type" "$topic")
    
    echo ""
    echo "🎭 Production Details:"
    echo "   👤 Host: $HOST_NAME ($selected_host)"
    echo "   🎤 Voice: $HOST_VOICE"
    echo "   🖼️ Background: $selected_bg"
    echo "   📝 Content: $CONTENT"
    echo "   📍 Head position: x=$HEAD_X, y=$HEAD_Y, scale=$HEAD_SCALE"
    echo ""
    
    # Expand avatar path
    HOST_AVATAR_EXPANDED=$(eval echo "$HOST_AVATAR")
    
    # Check if avatar exists
    if [ ! -f "$HOST_AVATAR_EXPANDED" ]; then
        echo "❌ Avatar file not found: $HOST_AVATAR_EXPANDED"
        echo "💡 Please update the avatar path in the configuration file"
        exit 1
    fi
    
    # Run the main workflow
    echo "🚀 Starting production workflow..."
    "$SCRIPT_DIR/run_avatar_workflow.sh" "$CONTENT" "$HOST_AVATAR_EXPANDED" "$BACKGROUND_PATH" "$HEAD_X" "$HEAD_Y" "$HEAD_SCALE"
}

# Show usage if no arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <content_type> <topic> [custom_host] [custom_background]"
    echo ""
    echo "Content Types:"
    echo "  breaking_news  - Sarah Chen (female) + newsroom background"
    echo "  analysis       - Marcus Johnson (male) + studio background"
    echo "  commentary     - Sarah Chen (female) + office background"
    echo ""
    echo "Examples:"
    echo "  $0 breaking_news \"Election results announced\""
    echo "  $0 analysis \"Market volatility\""
    echo "  $0 commentary \"Political implications\""
    echo "  $0 breaking_news \"Tech breakthrough\" male studio"
    echo ""
    echo "Custom Options:"
    echo "  custom_host: female, male"
    echo "  custom_background: studio, newsroom, office"
    exit 1
fi

# Run main workflow
main "$@"
