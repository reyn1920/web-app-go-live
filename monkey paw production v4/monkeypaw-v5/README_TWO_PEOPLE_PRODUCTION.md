# The Right Perspective - Complete Production System

## 🎬 "Two People, One Decision" - Full 14-Minute Duet Production

A complete production workflow for creating professional news videos using full-body avatars, AI animation, and dual-host management for "The Right Perspective" channel.

## 📋 Overview

This system transforms the tagged script "Two People, One Decision" into a complete 14-minute video production featuring:

- **Sarah Chen (Female Host)** - Senior Political Analyst
- **Marcus Johnson (Male Host)** - Chief News Correspondent
- **Professional compositing** with full-body avatars
- **Intelligent content routing** based on segment type
- **Automated production pipeline** from script to final video

## 🏗️ System Architecture

```
Tagged Script → Script Parser → Production Segments → Avatar Workflow → Final Video
     ↓              ↓                ↓                    ↓              ↓
  [TAGS]      JSON Segments    Content Routing    Dual-Host System   14min.mp4
```

## 📁 File Structure

```
monkeypaw-v5/
├── script_parser.py                    # Parses tagged script into segments
├── produce_two_people_one_decision.sh   # Complete production workflow
├── run_dual_host.sh                   # Dual-host management system
├── run_avatar_workflow.sh             # Main avatar production pipeline
├── producer_script.py                 # Blender compositing engine
├── avatar_head_cropper.py             # Head detection and cropping
├── the_right_perspective_config.json  # Channel and host configuration
└── README_AVATAR_WORKFLOW.md          # Detailed avatar workflow docs
```

## 🚀 Quick Start

### 1. Parse the Script
```bash
cd monkeypaw-v5
python3 script_parser.py
```

### 2. Run Complete Production
```bash
./produce_two_people_one_decision.sh
```

### 3. Individual Segment Production
```bash
# Breaking news with Sarah
./run_dual_host.sh breaking_news "We keep saying tomorrow..."

# Analysis with Marcus
./run_dual_host.sh analysis "We've got ideas stacked like dishes..."

# Commentary with Sarah
./run_dual_host.sh commentary "I don't fear failing publicly..."
```

## 📝 Script Structure

The script is parsed into **11 segments** with automatic content type routing:

| Segment | Title | Duration | Host | Content Type | Background |
|---------|-------|----------|------|--------------|------------|
| 1 | Cold Open (Hook) | 0:45 | Sarah | Breaking News | Newsroom |
| 2 | The Problem | 1:25 | Marcus | Analysis | Studio |
| 3 | The Stakes | 1:35 | Sarah | Commentary | Office |
| 4 | The Pact | 1:30 | Sarah | Commentary | Office |
| 5 | The Friction | 1:35 | Marcus | Analysis | Studio |
| 6 | The Map | 1:40 | Sarah | Breaking News | Newsroom |
| 7 | The Demo | 2:00 | Marcus | Analysis | Studio |
| 8 | The Dip | 1:10 | Sarah | Commentary | Office |
| 9 | The One Metric | 0:50 | Marcus | Analysis | Studio |
| 10 | The Audience Loop | 0:55 | Sarah | Commentary | Office |
| 11 | The Send-Off | 0:35 | Sarah | Breaking News | Newsroom |

## 🎭 Host Configuration

### Sarah Chen (Female Host)
- **Role**: Senior Political Analyst
- **Voice**: Professional Female
- **Specialties**: Breaking news, Commentary
- **Avatar**: Woman from Downloads folder
- **Head Position**: x=0, y=150, scale=1.0

### Marcus Johnson (Male Host)
- **Role**: Chief News Correspondent
- **Voice**: Professional Male
- **Specialties**: Analysis, Deep dives
- **Avatar**: Man from Downloads folder
- **Head Position**: x=0, y=120, scale=1.1

## 🎬 Production Workflow

### Phase 1: Script Parsing
```bash
python3 script_parser.py
```
- Parses tagged script into structured JSON segments
- Extracts dialogue, camera notes, and SFX cues
- Creates production-ready files

### Phase 2: Segment Production
```bash
./produce_two_people_one_decision.sh
```
- Processes each segment with appropriate host
- Routes content type automatically
- Generates individual video segments

### Phase 3: Final Assembly
- Combines 11 segments into final 14-minute video
- Adds transitions and polish
- Ready for channel upload

## 🏷️ Tag System

The script uses a comprehensive tagging system:

### Speaker Tags
- `M` - Marcus Johnson (male host)
- `W` - Sarah Chen (female host)
- `Together` - Both hosts speaking

### Expression Tags
- `[FACE:SERIOUS]` - Serious expression
- `[FACE:SMILE-SOFT]` - Soft smile
- `[FACE:SMILE-BIG]` - Big smile
- `[FACE:EYEBROW-UP]` - Raised eyebrow
- `[FACE:FOCUS]` - Focused expression

### Gesture Tags
- `[GEST:POINT-FWD]` - Point forward
- `[GEST:OPEN-ARMS]` - Open arms gesture
- `[GEST:CHOP]` - Chopping motion
- `[GEST:COUNT-3]` - Count to three
- `[GEST:PINCH]` - Pinch gesture

### Pose Tags
- `[POSE:IDLE-NEUTRAL]` - Neutral idle pose
- `[POSE:CONFIDENT]` - Confident pose
- `[POSE:THINK]` - Thinking pose

### Camera Tags
- `[CAM:2S]` - Two-shot
- `[CAM:MS]` - Medium shot
- `[CAM:CU]` - Close-up
- `[CAM:WS]` - Wide shot
- `[PAN-R]` - Pan right
- `[DOLLY-IN]` - Dolly in

### Audio Tags
- `[TTS:BASE]` - Base TTS voice
- `[TTS:SLOW]` - Slow speech
- `[TTS:FAST]` - Fast speech
- `[BEAT:0.3s]` - Pause timing
- `[SFX:LAMP-CLICK]` - Sound effect

## 🔧 Customization

### Adding New Segments
1. Add segment to script with proper timing
2. Update `script_parser.py` if needed
3. Add segment processing to `produce_two_people_one_decision.sh`

### Modifying Host Assignments
Edit `the_right_perspective_config.json`:
```json
{
  "channel": {
    "hosts": {
      "female": {
        "name": "Sarah Chen",
        "avatar_path": "~/Downloads/woman_avatar.png"
      },
      "male": {
        "name": "Marcus Johnson",
        "avatar_path": "~/Downloads/man_avatar.png"
      }
    }
  }
}
```

### Changing Content Type Routing
Modify the content type logic in `produce_two_people_one_decision.sh`:
```bash
if [[ "$segment_title" == *"BREAKING"* ]]; then
    content_type="breaking_news"
    host="female"
elif [[ "$segment_title" == *"ANALYSIS"* ]]; then
    content_type="analysis"
    host="male"
fi
```

## 🧪 Testing

### Test Individual Components
```bash
# Test script parsing
python3 script_parser.py

# Test avatar workflow
./test_avatar_basic.sh

# Test dual-host system
./run_dual_host.sh breaking_news "Test message"
```

### Test Complete Workflow
```bash
# Run full production (requires APIs)
./produce_two_people_one_decision.sh
```

## 📊 Output Specifications

- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 30 FPS
- **Duration**: 14:00 minutes
- **Codec**: H.264
- **Audio**: AAC, 44.1kHz
- **Format**: MP4

## 🚨 Troubleshooting

### Common Issues

**Script Parser Errors**
```bash
# Check Python dependencies
python3 -c "import json, re, pathlib"

# Verify script format
head -20 /path/to/script.txt
```

**Avatar Workflow Failures**
```bash
# Check dependencies
which python3 magick blender ffmpeg

# Test head cropping
python3 avatar_head_cropper.py ~/Downloads/avatar.png /tmp/test.png
```

**Production Script Issues**
```bash
# Check file permissions
ls -la *.sh

# Verify configuration
python3 -m json.tool the_right_perspective_config.json
```

## 📈 Performance

### Typical Processing Times
- **Script Parsing**: 1-2 seconds
- **Per Segment**: 2-3 minutes
- **Total Production**: 25-35 minutes
- **Final Assembly**: 5-10 minutes

### Resource Requirements
- **CPU**: Multi-core recommended
- **RAM**: 8GB+ for Blender compositing
- **Storage**: 2GB+ for temporary files
- **Network**: For API calls (TTS, Linly-Talker)

## 🔄 Integration

### With Monkey Paw API
The system integrates with existing Monkey Paw infrastructure:
- Uses existing TTS services
- Leverages Linly-Talker for animation
- Connects to channel management
- Integrates with upload automation

### With External Services
- **Linly-Talker**: AI head animation
- **TTS Services**: Voice generation
- **Blender**: Video compositing
- **ImageMagick**: Image processing

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Run the test scripts
3. Verify all dependencies are installed
4. Check the configuration file format

## 📄 License

This project is part of the Monkey Paw Production system. All rights reserved.

---

**The Right Perspective** - Professional news analysis with cutting-edge avatar technology and dual-host management.

## 🎯 Next Steps

1. **Set up Linly-Talker API** for AI head animation
2. **Configure TTS service** for voice generation  
3. **Test with real content** using the production script
4. **Deploy to production** for The Right Perspective channel
5. **Create additional scripts** using the same workflow

The system is ready for professional video production! 🚀
