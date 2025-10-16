#!/bin/bash
# Basic Avatar Workflow Test (No Blender)
# Tests head cropping and creates a simple composite using ImageMagick

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_DIR="/tmp/avatar_test_$(date +%s)"
AV_OUT="$TMP_DIR/audio_video"
FINAL_DIR="$TMP_DIR/final"

# Create working directories
mkdir -p "$TMP_DIR" "$AV_OUT" "$FINAL_DIR"

echo "🧪 Testing Avatar Workflow Components (Basic)"
echo "📁 Working directory: $TMP_DIR"

# Test 1: Head cropping
echo ""
echo "=== TEST 1: Head Cropping ==="
avatar_path="$1"
if [ -z "$avatar_path" ]; then
    avatar_path="$HOME/Downloads/Gemini_Generated_Image_7d45m97d45m97d45.png"
fi

head_png="$AV_OUT/test_head.png"
echo "✂️ Cropping head from: $avatar_path"
python3 "$SCRIPT_DIR/avatar_head_cropper.py" "$avatar_path" "$head_png"

if [ -f "$head_png" ] && [ -s "$head_png" ]; then
    echo "✅ Head cropping test PASSED"
    echo "📊 Cropped head size: $(du -h "$head_png" | cut -f1)"
else
    echo "❌ Head cropping test FAILED"
    exit 1
fi

# Test 2: Simple composite using ImageMagick
echo ""
echo "=== TEST 2: Simple Composite ==="
background_path="$SCRIPT_DIR/assets/studio_background.jpg"
composite_output="$FINAL_DIR/simple_composite.jpg"

echo "🖼️ Creating simple composite..."
echo "🖼️ Background: $background_path"
echo "👤 Avatar: $avatar_path"
echo "🧠 Head: $head_png"
echo "📹 Output: $composite_output"

# Create a simple composite: background + avatar + head overlay
magick "$background_path" \
    \( "$avatar_path" -resize 800x800 \) \
    -gravity center -composite \
    \( "$head_png" -resize 200x200 \) \
    -gravity north -geometry +0+50 -composite \
    "$composite_output"

if [ -f "$composite_output" ] && [ -s "$composite_output" ]; then
    echo "✅ Simple composite test PASSED"
    echo "📊 Composite size: $(du -h "$composite_output" | cut -f1)"
    echo "📹 Composite image: $composite_output"
else
    echo "❌ Simple composite test FAILED"
    exit 1
fi

# Test 3: Validate The Right Perspective configuration
echo ""
echo "=== TEST 3: Configuration Validation ==="
config_file="$SCRIPT_DIR/the_right_perspective_config.json"

if [ -f "$config_file" ]; then
    echo "✅ Configuration file exists: $config_file"
    
    # Check if JSON is valid
    if python3 -m json.tool "$config_file" > /dev/null 2>&1; then
        echo "✅ Configuration JSON is valid"
        
        # Extract key information
        channel_name=$(python3 -c "import json; print(json.load(open('$config_file'))['channel']['name'])")
        female_host=$(python3 -c "import json; print(json.load(open('$config_file'))['channel']['hosts']['female']['name'])")
        male_host=$(python3 -c "import json; print(json.load(open('$config_file'))['channel']['hosts']['male']['name'])")
        
        echo "📺 Channel: $channel_name"
        echo "👩 Host: $female_host"
        echo "👨 Host: $male_host"
        
    else
        echo "❌ Configuration JSON is invalid"
        exit 1
    fi
else
    echo "❌ Configuration file not found: $config_file"
    exit 1
fi

echo ""
echo "🎉 ALL BASIC TESTS PASSED!"
echo "📁 Test files saved in: $TMP_DIR"
echo ""
echo "🚀 Avatar workflow components are working!"
echo "💡 Next steps:"
echo "   1. Fix Blender installation for full video compositing"
echo "   2. Set up Linly-Talker API endpoint"
echo "   3. Configure TTS service"
echo "   4. Run full workflow: ./run_avatar_workflow.sh"
echo ""
echo "📹 Preview composite: $composite_output"

# Keep test files for inspection
echo "📁 Test files preserved in: $TMP_DIR"
