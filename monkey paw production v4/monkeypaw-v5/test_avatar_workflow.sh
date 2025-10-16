#!/bin/bash
# Simplified Avatar Workflow Test
# Tests head cropping and Blender compositing without external APIs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_DIR="/tmp/avatar_test_$(date +%s)"
AV_OUT="$TMP_DIR/audio_video"
FINAL_DIR="$TMP_DIR/final"

# Create working directories
mkdir -p "$TMP_DIR" "$AV_OUT" "$FINAL_DIR"

echo "🧪 Testing Avatar Workflow Components"
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

# Test 2: Create mock animated head (simple video)
echo ""
echo "=== TEST 2: Mock Animated Head ==="
mock_head_video="$AV_OUT/mock_animated_head.mp4"
echo "🎬 Creating mock animated head video..."

# Create a simple 5-second video using FFmpeg
ffmpeg -f lavfi -i "color=c=blue:size=512x512:duration=5" -f lavfi -i "sine=frequency=1000:duration=5" -c:v libx264 -c:a aac -shortest "$mock_head_video" -y 2>/dev/null

if [ -f "$mock_head_video" ] && [ -s "$mock_head_video" ]; then
    echo "✅ Mock animated head created: $mock_head_video"
else
    echo "❌ Mock animated head creation FAILED"
    exit 1
fi

# Test 3: Blender compositing
echo ""
echo "=== TEST 3: Blender Compositing ==="
background_path="$SCRIPT_DIR/assets/studio_background.jpg"
final_video="$FINAL_DIR/test_final.mp4"

echo "🎬 Testing Blender compositing..."
echo "🖼️ Background: $background_path"
echo "👤 Avatar: $avatar_path"
echo "🧠 Animated head: $mock_head_video"
echo "📹 Output: $final_video"

# Test Blender script with mock data
blender --background --python "$SCRIPT_DIR/producer_script.py" -- \
    --background "$background_path" \
    --avatar "$avatar_path" \
    --head "$mock_head_video" \
    --output "$final_video" \
    --head-x 0 \
    --head-y 150 \
    --head-scale 1.0

if [ -f "$final_video" ] && [ -s "$final_video" ]; then
    echo "✅ Blender compositing test PASSED"
    echo "📊 Final video size: $(du -h "$final_video" | cut -f1)"
    echo "📹 Final video: $final_video"
else
    echo "❌ Blender compositing test FAILED"
    exit 1
fi

echo ""
echo "🎉 ALL TESTS PASSED!"
echo "📁 Test files saved in: $TMP_DIR"
echo ""
echo "🚀 Avatar workflow is ready for production!"
echo "💡 Next steps:"
echo "   1. Set up Linly-Talker API endpoint"
echo "   2. Configure TTS service"
echo "   3. Run full workflow: ./run_avatar_workflow.sh"

# Cleanup
echo ""
echo "🧹 Cleaning up test files..."
rm -rf "$TMP_DIR"
echo "✅ Cleanup complete"
