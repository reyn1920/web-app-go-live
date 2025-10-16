# The Right Perspective - Full-Body Avatar Production System

A professional video production workflow that creates talking head videos using full-body avatars, AI animation, and Blender compositing for "The Right Perspective" news channel.

## 🎯 Overview

This system solves the "floating head" problem by:
1. **Cropping** the head from full-body avatars
2. **Animating** the head using AI (Linly-Talker/SadTalker)
3. **Compositing** the animated head back onto the full-body avatar
4. **Layering** everything onto professional backgrounds

## 🏗️ Architecture

```
Full-Body Avatar → Head Crop → AI Animation → Blender Composite → Final Video
     ↓              ↓            ↓              ↓                ↓
   Woman.png    head.png    animated.mp4    layers.blend    final.mp4
```

## 📁 File Structure

```
monkeypaw-v5/
├── producer_script.py              # Blender compositing script
├── avatar_head_cropper.py          # Head cropping utility
├── run_avatar_workflow.sh          # Main production workflow
├── run_dual_host.sh               # Dual-host management
├── test_avatar_basic.sh           # Basic component testing
├── test_avatar_workflow.sh        # Full workflow testing
├── the_right_perspective_config.json # Channel configuration
└── assets/
    ├── studio_background.jpg      # Professional studio background
    ├── newsroom_background.jpg    # Newsroom background
    └── office_background.jpg      # Office background
```

## 🚀 Quick Start

### 1. Test Components
```bash
cd monkeypaw-v5
./test_avatar_basic.sh ~/Downloads/woman_avatar.png
```

### 2. Run Single Production
```bash
./run_avatar_workflow.sh "Welcome to The Right Perspective" ~/Downloads/woman_avatar.png
```

### 3. Run Dual-Host Production
```bash
# Breaking news with Sarah Chen
./run_dual_host.sh breaking_news "Election results announced"

# Analysis with Marcus Johnson  
./run_dual_host.sh analysis "Market volatility"

# Commentary with Sarah Chen
./run_dual_host.sh commentary "Political implications"
```

## 👥 Hosts Configuration

### Sarah Chen (Female Host)
- **Role**: Senior Political Analyst
- **Voice**: Professional Female
- **Specialties**: Breaking news, Commentary
- **Head Position**: x=0, y=150, scale=1.0

### Marcus Johnson (Male Host)
- **Role**: Chief News Correspondent  
- **Voice**: Professional Male
- **Specialties**: Analysis, Deep dives
- **Head Position**: x=0, y=120, scale=1.1

## 🎬 Content Types

| Type | Host | Background | Template |
|------|------|------------|----------|
| `breaking_news` | Sarah (Female) | Newsroom | "Breaking news: {topic}. Here's what you need to know..." |
| `analysis` | Marcus (Male) | Studio | "Let's analyze the implications of {topic}..." |
| `commentary` | Sarah (Female) | Office | "From The Right Perspective, here's my take on {topic}..." |

## 🛠️ Dependencies

### Required
- **Python 3.8+** - Core scripting
- **ImageMagick** - Image processing and cropping
- **Blender 3.0+** - Video compositing
- **FFmpeg** - Video processing
- **curl** - API communication

### Optional APIs
- **Linly-Talker** - AI head animation
- **TTS Service** - Text-to-speech
- **Monkey Paw API** - Integrated services

### Install Dependencies
```bash
# macOS
brew install imagemagick blender ffmpeg

# Ubuntu/Debian
sudo apt install imagemagick blender ffmpeg

# Verify installation
python3 --version
magick --version
blender --version
ffmpeg -version
```

## 🔧 Configuration

### Channel Settings (`the_right_perspective_config.json`)
```json
{
  "channel": {
    "name": "The Right Perspective",
    "hosts": {
      "female": {
        "name": "Sarah Chen",
        "avatar_path": "~/Downloads/woman_avatar.png",
        "voice_profile": "professional_female"
      },
      "male": {
        "name": "Marcus Johnson", 
        "avatar_path": "~/Downloads/man_avatar.png",
        "voice_profile": "professional_male"
      }
    }
  }
}
```

### Avatar Requirements
- **Format**: PNG with transparency
- **Resolution**: 1024x1024 or higher
- **Content**: Full-body shot with clear head
- **Background**: Transparent or solid color
- **Quality**: High resolution, good lighting

## 🎨 Customization

### Head Positioning
Adjust head placement in the configuration:
```json
"head_position": {
  "x": 0,      // Horizontal offset
  "y": 150,    // Vertical offset  
  "scale": 1.0  // Size multiplier
}
```

### Backgrounds
Add custom backgrounds to `assets/`:
- `studio_background.jpg` - Professional studio
- `newsroom_background.jpg` - Newsroom setting
- `office_background.jpg` - Office environment

### Voice Profiles
Configure TTS voices:
- `professional_female` - Sarah's voice
- `professional_male` - Marcus's voice
- `authoritative` - Breaking news tone
- `analytical` - Analysis tone

## 🧪 Testing

### Basic Component Test
```bash
./test_avatar_basic.sh ~/Downloads/woman_avatar.png
```
Tests: Head cropping, simple compositing, configuration validation

### Full Workflow Test
```bash
./test_avatar_workflow.sh ~/Downloads/woman_avatar.png
```
Tests: All components including Blender compositing

### Manual Testing
```bash
# Test head cropping only
python3 avatar_head_cropper.py ~/Downloads/woman.png /tmp/head.png

# Test Blender script
blender --background --python producer_script.py -- \
  --background assets/studio_background.jpg \
  --avatar ~/Downloads/woman.png \
  --head /tmp/animated_head.mp4 \
  --output /tmp/final.mp4
```

## 🚨 Troubleshooting

### Common Issues

**Blender Segmentation Fault**
```bash
# Solution: Use system Python
export PYTHONPATH=""
blender --background --python producer_script.py
```

**ImageMagick Command Not Found**
```bash
# Solution: Use modern syntax
magick convert input.png output.png
# Instead of: convert input.png output.png
```

**Avatar File Not Found**
```bash
# Solution: Update configuration paths
# Use absolute paths: /Users/username/Downloads/avatar.png
# Or expand tildes: ~/Downloads/avatar.png
```

**Head Cropping Fails**
```bash
# Solution: Check image format
file ~/Downloads/avatar.png
# Should show: PNG image data
```

### Debug Mode
```bash
# Enable verbose output
export DEBUG=1
./run_avatar_workflow.sh "test" ~/Downloads/avatar.png
```

## 📊 Performance

### Typical Processing Times
- **Head Cropping**: 1-2 seconds
- **TTS Generation**: 5-10 seconds
- **AI Animation**: 30-60 seconds
- **Blender Compositing**: 10-30 seconds
- **Total**: 1-2 minutes per video

### Output Specifications
- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 30 FPS
- **Codec**: H.264
- **Audio**: AAC, 44.1kHz
- **Format**: MP4

## 🔄 Workflow Integration

### With Monkey Paw API
```bash
# Use integrated TTS
curl -X POST http://127.0.0.1:8789/api/tts/generate \
  -d '{"text": "Breaking news", "voice": "professional_female"}'

# Use Linly-Talker
curl -X POST http://127.0.0.1:8000/talker_response/ \
  -F "source_image=@head.png" \
  -F "driven_audio=@voice.mp3"
```

### Batch Processing
```bash
# Process multiple topics
for topic in "Election" "Economy" "Technology"; do
  ./run_dual_host.sh breaking_news "$topic"
done
```

## 📈 Future Enhancements

- [ ] **Multi-language Support** - International voice profiles
- [ ] **Gesture Recognition** - Hand movement animation
- [ ] **Emotion Detection** - Context-aware expressions
- [ ] **Live Streaming** - Real-time avatar generation
- [ ] **Mobile App** - iOS/Android integration
- [ ] **Cloud Processing** - AWS/GCP deployment

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Run the test scripts
3. Verify all dependencies are installed
4. Check the configuration file format

## 📄 License

This project is part of the Monkey Paw Production system. All rights reserved.

---

**The Right Perspective** - Professional news analysis with cutting-edge avatar technology.
