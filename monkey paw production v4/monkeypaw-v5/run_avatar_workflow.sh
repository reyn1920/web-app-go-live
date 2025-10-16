#!/bin/bash
# Full-Body Avatar Production Workflow for The Right Perspective
# Integrates head cropping, AI animation, and Blender compositing

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_DIR="/tmp/monkeypaw_avatar_workflow"
AV_OUT="$TMP_DIR/audio_video"
FINAL_DIR="$TMP_DIR/final"

# Create working directories
mkdir -p "$TMP_DIR" "$AV_OUT" "$FINAL_DIR"

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up temporary files..."
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# Function to check dependencies
check_dependencies() {
    echo "🔍 Checking dependencies..."
    
    local missing_deps=()
    
    # Check for required tools
    command -v python3 >/dev/null || missing_deps+=("python3")
    command -v curl >/dev/null || missing_deps+=("curl")
    command -v convert >/dev/null || missing_deps+=("ImageMagick")
    command -v blender >/dev/null || missing_deps+=("Blender")
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo "❌ Missing dependencies: ${missing_deps[*]}"
        echo "Please install: brew install imagemagick blender"
        exit 1
    fi
    
    echo "✅ All dependencies available"
}

# Function to validate avatar file
validate_avatar() {
    local avatar_path="$1"
    
    if [ ! -f "$avatar_path" ]; then
        echo "❌ Avatar file not found: $avatar_path"
        exit 1
    fi
    
    # Check if it's an image file
    if ! file "$avatar_path" | grep -q "image"; then
        echo "❌ File is not an image: $avatar_path"
        exit 1
    fi
    
    echo "✅ Avatar file validated: $avatar_path"
}

# Function to crop head from full-body avatar
crop_head() {
    local avatar_path="$1"
    local head_output="$2"
    
    echo "✂️ Cropping head from full-body avatar..."
    
    python3 "$SCRIPT_DIR/avatar_head_cropper.py" "$avatar_path" "$head_output"
    
    if [ ! -f "$head_output" ] || [ ! -s "$head_output" ]; then
        echo "❌ Head cropping failed!"
        exit 1
    fi
    
    echo "✅ Head cropped successfully: $head_output"
}

# Function to generate TTS audio
generate_tts() {
    local prompt="$1"
    local audio_output="$2"
    
    echo "🎤 Generating TTS audio..."
    
    # Use existing TTS system (adjust API endpoint as needed)
    curl -sS -X POST "http://127.0.0.1:8789/api/tts/generate" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$prompt\", \"voice\": \"professional_female\"}" \
        -o "$audio_output"
    
    if [ ! -f "$audio_output" ] || [ ! -s "$audio_output" ]; then
        echo "❌ TTS generation failed!"
        exit 1
    fi
    
    echo "✅ TTS audio generated: $audio_output"
}

# Function to generate animated head
generate_animated_head() {
    local head_image="$1"
    local audio_file="$2"
    local output_video="$3"
    
    echo "🧠 Generating animated head with Linly-Talker..."
    
    # Use Linly-Talker API (adjust endpoint as needed)
    curl -sS -X POST "http://127.0.0.1:8000/talker_response/" \
        -F "source_image=@$head_image" \
        -F "driven_audio=@$audio_file" \
        -o "$output_video"
    
    if [ ! -f "$output_video" ] || [ ! -s "$output_video" ]; then
        echo "❌ Linly-Talker animation failed!"
        exit 1
    fi
    
    echo "✅ Animated head generated: $output_video"
}

# Function to composite final video in Blender
composite_final_video() {
    local background_path="$1"
    local avatar_path="$2"
    local animated_head="$3"
    local output_video="$4"
    local head_x="${5:-0}"
    local head_y="${6:-150}"
    local head_scale="${7:-1.0}"
    
    echo "🎬 Compositing final video in Blender..."
    
    blender --background --python "$SCRIPT_DIR/producer_script.py" -- \
        --background "$background_path" \
        --avatar "$avatar_path" \
        --head "$animated_head" \
        --output "$output_video" \
        --head-x "$head_x" \
        --head-y "$head_y" \
        --head-scale "$head_scale"
    
    if [ ! -f "$output_video" ] || [ ! -s "$output_video" ]; then
        echo "❌ Blender compositing failed!"
        exit 1
    fi
    
    echo "✅ Final video composited: $output_video"
}

# Main workflow function
main() {
    local prompt="$1"
    local avatar_path="$2"
    local background_path="${3:-$SCRIPT_DIR/assets/default_background.jpg}"
    local head_x="${4:-0}"
    local head_y="${5:-150}"
    local head_scale="${6:-1.0}"
    
    echo "🚀 Starting Full-Body Avatar Production Workflow"
    echo "📝 Prompt: $prompt"
    echo "👤 Avatar: $avatar_path"
    echo "🖼️ Background: $background_path"
    echo "📍 Head position: x=$head_x, y=$head_y, scale=$head_scale"
    
    # Check dependencies
    check_dependencies
    
    # Validate inputs
    validate_avatar "$avatar_path"
    
    # Generate unique filenames
    local timestamp=$(date +%s)
    local head_png="$AV_OUT/head_${timestamp}.png"
    local audio_mp3="$AV_OUT/voice_${timestamp}.mp3"
    local animated_head="$AV_OUT/animated_head_${timestamp}.mp4"
    local final_video="$FINAL_DIR/the_right_perspective_${timestamp}.mp4"
    
    # Step 1: Crop head from full-body avatar
    crop_head "$avatar_path" "$head_png"
    
    # Step 2: Generate TTS audio
    generate_tts "$prompt" "$audio_mp3"
    
    # Step 3: Generate animated head
    generate_animated_head "$head_png" "$audio_mp3" "$animated_head"
    
    # Step 4: Composite final video
    composite_final_video "$background_path" "$avatar_path" "$animated_head" "$final_video" "$head_x" "$head_y" "$head_scale"
    
    echo ""
    echo "🎉 PRODUCTION COMPLETE!"
    echo "📹 Final video: $final_video"
    echo "📊 File size: $(du -h "$final_video" | cut -f1)"
    echo ""
    echo "🎬 The Right Perspective video is ready for upload!"
}

# Show usage if no arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <prompt> <avatar_path> [background_path] [head_x] [head_y] [head_scale]"
    echo ""
    echo "Examples:"
    echo "  $0 \"Welcome to The Right Perspective\" ~/Downloads/woman.png"
    echo "  $0 \"Breaking news analysis\" ~/Downloads/man.png ~/Downloads/studio_bg.jpg"
    echo "  $0 \"Today's top stories\" ~/Downloads/woman.png ~/Downloads/bg.jpg 50 200 1.2"
    echo ""
    echo "Arguments:"
    echo "  prompt         - Text to be spoken by the avatar"
    echo "  avatar_path    - Path to full-body avatar image"
    echo "  background_path- Optional background image (default: studio background)"
    echo "  head_x         - X position offset for head (default: 0)"
    echo "  head_y         - Y position offset for head (default: 150)"
    echo "  head_scale     - Scale factor for head (default: 1.0)"
    exit 1
fi

# Run main workflow
main "$@"
