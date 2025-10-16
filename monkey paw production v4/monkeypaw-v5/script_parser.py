#!/usr/bin/env python3
"""
Script Parser for The Right Perspective - "Two People, One Decision"
Parses the tagged script and creates production-ready segments for dual-host avatars.
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class DialogueLine:
    """Represents a single line of dialogue with all tags."""
    speaker: str  # M or W
    text: str
    tags: Dict[str, str]
    timing: Optional[str] = None

@dataclass
class ScriptSegment:
    """Represents a script segment with timing and dialogue."""
    title: str
    start_time: str
    end_time: str
    duration: str
    dialogue: List[DialogueLine]
    camera_notes: List[str]
    sfx_notes: List[str]

class ScriptParser:
    """Parses the tagged script into structured segments."""
    
    def __init__(self):
        self.segments: List[ScriptSegment] = []
        self.current_segment: Optional[ScriptSegment] = None
        
    def parse_script(self, script_content: str) -> List[ScriptSegment]:
        """Parse the full script content into segments."""
        lines = script_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check for segment headers
            if self._is_segment_header(line):
                self._start_new_segment(line)
            elif self._is_camera_note(line):
                if self.current_segment:
                    self.current_segment.camera_notes.append(line)
            elif self._is_sfx_note(line):
                if self.current_segment:
                    self.current_segment.sfx_notes.append(line)
            elif self._is_dialogue_line(line):
                dialogue = self._parse_dialogue_line(line)
                if self.current_segment and dialogue:
                    self.current_segment.dialogue.append(dialogue)
        
        return self.segments
    
    def _is_segment_header(self, line: str) -> bool:
        """Check if line is a segment header."""
        return re.match(r'^\d+:\d+–\d+:\d+', line) is not None
    
    def _is_camera_note(self, line: str) -> bool:
        """Check if line is a camera note."""
        return line.startswith('[CAM:') or line.startswith('[PAN-') or line.startswith('[DOLLY-')
    
    def _is_sfx_note(self, line: str) -> bool:
        """Check if line is an SFX note."""
        return line.startswith('[SFX:')
    
    def _is_dialogue_line(self, line: str) -> bool:
        """Check if line is a dialogue line."""
        return re.match(r'^[MW]\s', line) is not None
    
    def _start_new_segment(self, header_line: str):
        """Start a new segment from header line."""
        # Extract timing and title
        match = re.match(r'^(\d+:\d+)–(\d+:\d+)\s*—\s*(.+)$', header_line)
        if match:
            start_time, end_time, title = match.groups()
            duration = self._calculate_duration(start_time, end_time)
            
            self.current_segment = ScriptSegment(
                title=title,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                dialogue=[],
                camera_notes=[],
                sfx_notes=[]
            )
            self.segments.append(self.current_segment)
    
    def _parse_dialogue_line(self, line: str) -> Optional[DialogueLine]:
        """Parse a dialogue line with tags."""
        # Extract speaker
        speaker_match = re.match(r'^([MW])\s', line)
        if not speaker_match:
            return None
        
        speaker = speaker_match.group(1)
        
        # Extract tags and text
        tags = {}
        text = ""
        
        # Find all tag patterns [TAG:value]
        tag_pattern = r'\[([^:]+):([^\]]+)\]'
        tag_matches = re.findall(tag_pattern, line)
        
        for tag_name, tag_value in tag_matches:
            tags[tag_name] = tag_value
        
        # Extract text (everything after tags)
        text_match = re.search(r'\]:\s*(.+)$', line)
        if text_match:
            text = text_match.group(1).strip()
        else:
            # Fallback: extract text after speaker
            text_match = re.match(r'^[MW]\s+(.+)$', line)
            if text_match:
                text = text_match.group(1).strip()
        
        return DialogueLine(speaker=speaker, text=text, tags=tags)
    
    def _calculate_duration(self, start: str, end: str) -> str:
        """Calculate duration between start and end times."""
        def time_to_seconds(time_str: str) -> int:
            minutes, seconds = map(int, time_str.split(':'))
            return minutes * 60 + seconds
        
        start_seconds = time_to_seconds(start)
        end_seconds = time_to_seconds(end)
        duration_seconds = end_seconds - start_seconds
        
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def export_segments(self, output_dir: str) -> Dict[str, str]:
        """Export segments to individual files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        exported_files = {}
        
        for i, segment in enumerate(self.segments, 1):
            # Create segment file
            segment_file = output_path / f"segment_{i:02d}_{segment.title.replace(' ', '_').replace('—', '_')}.json"
            
            segment_data = {
                "title": segment.title,
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "duration": segment.duration,
                "dialogue": [
                    {
                        "speaker": d.speaker,
                        "text": d.text,
                        "tags": d.tags
                    }
                    for d in segment.dialogue
                ],
                "camera_notes": segment.camera_notes,
                "sfx_notes": segment.sfx_notes
            }
            
            with open(segment_file, 'w') as f:
                json.dump(segment_data, f, indent=2)
            
            exported_files[segment.title] = str(segment_file)
            
            # Create dialogue files for each speaker
            for speaker in ['M', 'W']:
                speaker_lines = [d.text for d in segment.dialogue if d.speaker == speaker]
                if speaker_lines:
                    speaker_file = output_path / f"segment_{i:02d}_{speaker}.txt"
                    with open(speaker_file, 'w') as f:
                        f.write('\n'.join(speaker_lines))
        
        return exported_files
    
    def create_production_script(self, output_dir: str) -> str:
        """Create a production script for the avatar workflow."""
        script_path = Path(output_dir) / "production_script.sh"
        
        script_content = '''#!/bin/bash
# Production script for "Two People, One Decision"
# Generated by ScriptParser

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎬 The Right Perspective - Two People, One Decision Production"
echo "🎭 Dual-host avatar system integration"

# Function to run segment
run_segment() {
    local segment_num="$1"
    local content_type="$2"
    local text="$3"
    local host="$4"
    
    echo "🎬 Segment $segment_num: $content_type"
    if [ "$host" = "custom" ]; then
        ./run_dual_host.sh "$content_type" "$text" "$host"
    else
        ./run_dual_host.sh "$content_type" "$text"
    fi
}

'''
        
        # Add segment calls
        for i, segment in enumerate(self.segments, 1):
            # Determine content type based on segment
            if "COLD OPEN" in segment.title or "HOOK" in segment.title:
                content_type = "breaking_news"
                host = "female"
            elif "PROBLEM" in segment.title or "STAKES" in segment.title:
                content_type = "analysis" 
                host = "male"
            elif "PACT" in segment.title or "FRICTION" in segment.title:
                content_type = "commentary"
                host = "female"
            elif "DEMO" in segment.title or "MAP" in segment.title:
                content_type = "analysis"
                host = "male"
            elif "DIP" in segment.title or "METRIC" in segment.title:
                content_type = "commentary"
                host = "female"
            elif "AUDIENCE" in segment.title or "SEND-OFF" in segment.title:
                content_type = "breaking_news"
                host = "female"
            else:
                content_type = "commentary"
                host = "female"
            
            # Combine all dialogue for this segment
            all_text = " ".join([d.text for d in segment.dialogue])
            # Clean up text
            all_text = re.sub(r'\*\*(.*?)\*\*', r'\1', all_text)  # Remove bold markers
            all_text = re.sub(r'\[.*?\]', '', all_text)  # Remove remaining tags
            all_text = all_text.strip()
            
            script_content += f'''
# Segment {i}: {segment.title}
run_segment {i} "{content_type}" "{all_text}" "{host}"
'''
        
        script_content += '''
echo "🎉 All segments processed!"
echo "📁 Check /tmp/monkeypaw_avatar_workflow/final/ for output videos"
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        return str(script_path)

def main():
    """Main function to parse the script."""
    # The full script content
    script_content = '''
======================================================================
0:00–0:45 — COLD OPEN (HOOK)
======================================================================
[SFX:LAMP-CLICK][CAM:2S][BLOCK:HOLD][POSE:IDLE-NEUTRAL]

W [FACE:SERIOUS][TTS:BASE]: we keep saying "tomorrow." [BEAT:0.3s]
M [FACE:FOCUS][GEST:POINT-FWD]: tomorrow keeps saying "prove it."
W [FACE:SMILE-SOFT]: so—tonight?
M [NOD]: tonight.
W: full send?
M [FACE:SMILE-SOFT]: full send.
W: no rehearsals?
M: this is the rehearsal. this is the show.
W [GEST:OPEN-ARMS]: okay then—what's the rule?
M [FACE:EYEBROW-UP][TTS:SLOW]: one rule: **ship it ugly, fix it live.**
W [FACE:SMILE-BIG]: print that on my forehead. [SFX:WHOOSH-SOFT]

[CAM:WS][PAN-R][BLOCK:SHIFT-R 0.5m]

======================================================================
0:45–2:10 — THE PROBLEM (NAME IT)
======================================================================
M [POSE:THINK]: we've got ideas stacked like dishes in a sink—
W [GEST:CHOP]: —and we keep buying new plates.
M: new apps, new hacks, new "systems."
W [FACE:SERIOUS]: but no finished meals.
M: and the algorithm?
W [FACE:EYEBROW-UP]: doesn't owe us dessert.
M: so what are we actually building?
W [POSE:CONFIDENT]: a habit that makes results unavoidable.
M: uncomfortable truth: it's not talent.
W [GEST:PINCH]: it's teatime with discipline. daily.
M [FACE:FOCUS]: no candles, no vibe lighting.
W: just work that shows up even when **you** don't want to.

[CAM:CU on M][DOLLY-IN]
M [TTS:SLOW]: say it plain.

[CAM:CU on W]
W [FACE:SMILE-SOFT]: okay—**consistency beats charisma when charisma sleeps in.**
M [FACE:SMILE-SOFT]: and our charisma hits the snooze.
W [NOD]: today we fire the snooze. [BEAT:0.5s]

======================================================================
2:10–3:45 — THE STAKES (WHY IT MATTERS)
======================================================================
[CAM:2S][POSE:IDLE-NEUTRAL][BLOCK:HOLD]

M: i don't fear failing publicly.
W: i fear never releasing publicly.
M [GEST:PALMS-UP]: same. the years blur when you keep "preparing."
W [POSE:THINK]: "almost there" is a cul-de-sac with great lighting.
M: comfortable, circular, pretty.
W: but nobody visits.
M: we said we wanted to make something people **use**.
W [FACE:EYEBROW-UP]: not a portfolio for imaginary applause.
M: so the stakes are simple.
W: ship today, change tomorrow.
M: or stall today, repeat yesterday.

======================================================================
3:45–5:15 — THE PACT (RULES OF ENGAGEMENT)
======================================================================
[CAM:MS][PAN-L]
W [POSE:CONFIDENT]: pact time. three rules.
M [GEST:COUNT-3]: **rule one:** output over optics. if it works, keep it—even if it's "ugly."
W: **rule two:** do it scared. we act **before** confidence, not after.
M: **rule three:** one improvement per day is compounding interest.
W [GEST:CHOP]: a refrain to remember—

[CAM:2S]
Together [FACE:SMILE-BIG][TTS:FAST]: **start. ship. study.**
M: start the thing.
W: ship the version.
M: study the feedback.
W: then repeat till boredom looks impressed.

======================================================================
5:15–6:50 — THE FRICTION (EXCUSES RAPID-FIRE)
======================================================================
[CAM:2S][DOLLY-OUT slow][POSE:IDLE-NEUTRAL][LOOP:HEADNOD]

M: "i need the right gear."
W [GEST:CHOP]: the right gear needs the right hands. use yours.
M: "the market is saturated."
W: saturated markets still drink excellence.
M: "someone already did it."
W: no one did it **like you** for **these people** at **this time**.
M: "i'm not ready."
W: readiness is a luxury built by reps.
M: "what if they hate it?"
W: then you'll know what to fix by **friday**.
M: "what if they love it?"
W: then you work harder by **monday**.
Together [FACE:SMILE-SOFT]: either way—**we win.**

======================================================================
6:50–8:30 — THE MAP (14-MINUTE ARC)
======================================================================
[CAM:WS][PAN-L]
W [POSE:CONFIDENT]: here's our plan, and yes—it fits in **fourteen minutes**.
M: minute one was our hook.
W: minute two named the problem.
M: minute three set the stakes.
W: minute four made the pact.
M: minutes five and six cleared excuses.
W: minutes seven through nine? demonstrations.
M: minute ten: the dip—and how to cross it.
W: minute eleven: one metric that actually matters.
M: minute twelve: audience loop and feedback system.
W: minute thirteen: the wall we are absolutely going to hit—
M: —and minute fourteen: the send-off you can't ignore.
W: sound fast?
M: good. speed is a design constraint.
W: speed forces clarity.
M: clarity unlocks action.

======================================================================
8:30–10:30 — THE DEMO (TINY, TANGIBLE WINS)
======================================================================
[CAM:MS][DOLLY-IN]

W [POSE:CONFIDENT][GEST:COUNT-3]: demo one: **the two-minute publish.**
M: pick one idea you shared with a friend this week.
W: open your notes. paste it as a 3-sentence post.
M: add **one** practical step.
W: press publish.
M: time it—two minutes.
W [FACE:SMILE-SOFT][NOD]: done? that was a rep.

[CAM:MS][PAN-R]
M [POSE:THINK]: demo two: **the one-take lesson.**
W: hit record. explain **one** mistake you made today and how you'll avoid it tomorrow.
M: no cuts. 60–90 seconds.
W: title: "i learned this the hard way."
M: upload.
W: that's signal people can use.

[CAM:WS][PAN-L]
M [POSE:CONFIDENT]: demo three: **the feedback form.**
W [GEST:COUNT-3]: three questions:
W: 1) what helped?
W: 2) what confused?
W: 3) what do you want next?
M: link it. pin it. ask for three answers a day.
W [NOD]: now you're not guessing—you're iterating.

======================================================================
10:30–11:40 — THE DIP (YOU WILL HIT IT)
======================================================================
[CAM:CU][POSE:THINK][FACE:SERIOUS]
M: the dip is coming. always.
W: views stall. sales flatline. dopamine takes PTO.
M: the dip is where amateurs pivot to new projects.
W: pros pivot their **process**.
M: how?
W: by shrinking the loop: **start → ship → study** in 24 hours.
M: the daily loop makes the dip shorter than your attention span.
W: and if you can outlast your attention span—
M: you outlast most people.

======================================================================
11:40–12:30 — THE ONE METRIC
======================================================================
[CAM:MS][POSE:CONFIDENT][FACE:SMILE-SOFT]
W: we track one thing this month: **kept promises to yourself.**
M: not likes, not views. **promises kept.**
W: "did i publish the thing i said i'd publish?"
M: "did i improve one step of the pipeline?"
W: if the answer is yes five days a week—
M: compounding begins to feel like cheating.
W: and if it's a no—
M: no self-court, no trial.
W: just a shorter loop tomorrow.

======================================================================
12:30–13:25 — THE AUDIENCE LOOP (GROW PEOPLE, NOT NUMBERS)
======================================================================
[CAM:MS][POSE:THINK]
M: audience isn't a crowd; it's a cohort.
W: cohorts need predictable value.
M: pick your **pillar**: teach, entertain, or enable.
W: pick your **promise**: "every weekday, a 60-second fix" (or your cadence).
M: pick your **path**: newsletter, community, product.
W: then over-deliver **quietly** every tenth post.
M: surprise creates stories.
W: stories create shares.
M: shares create tomorrow's baseline.

======================================================================
13:25–14:00 — THE SEND-OFF (COMMITMENT + CTA)
======================================================================
[CAM:2S][DOLLY-IN]
W: so—we done stalling?
M: i brought the publish button.
W: i brought the timer.
M: three breaths.
W: two words.
Together [FACE:SERIOUS → SMILE-SOFT][TTS:FAST]: **ship it.**
M: then come back here.
W: same time tomorrow.
Together [FACE:SMILE-BIG]: **start. ship. study.**
[SFX:KEYPRESS]
'''
    
    # Parse the script
    parser = ScriptParser()
    segments = parser.parse_script(script_content)
    
    print(f"📝 Parsed {len(segments)} segments:")
    for i, segment in enumerate(segments, 1):
        print(f"  {i}. {segment.title} ({segment.duration})")
        print(f"     {len(segment.dialogue)} dialogue lines")
        print(f"     {len(segment.camera_notes)} camera notes")
        print(f"     {len(segment.sfx_notes)} SFX notes")
    
    # Export segments
    output_dir = "/tmp/two_people_one_decision_production"
    exported_files = parser.export_segments(output_dir)
    
    print(f"\n📁 Exported to: {output_dir}")
    for title, file_path in exported_files.items():
        print(f"  📄 {title}: {file_path}")
    
    # Create production script
    production_script = parser.create_production_script(output_dir)
    print(f"\n🎬 Production script: {production_script}")
    
    print("\n🎉 Script parsing complete!")
    print("🚀 Ready for avatar production workflow!")

if __name__ == "__main__":
    main()
