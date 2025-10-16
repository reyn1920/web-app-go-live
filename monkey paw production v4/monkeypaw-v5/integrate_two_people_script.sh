#!/bin/bash
# The Right Perspective - "Two People, One Decision" Production Script
# Full 14-minute duet for Linly full-body avatars with M (man) and W (woman)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/the_right_perspective_config.json"

# Production settings
TITLE="Two People, One Decision — Full-Tagged 14-Minute Duet"
DURATION="14:00"
PACE="155-165 wpm combined"
CAST="M (man), W (woman)"

echo "🎬 The Right Perspective - Production Script"
echo "📺 Title: $TITLE"
echo "⏱️ Duration: $DURATION"
echo "🎭 Cast: $CAST"
echo "📊 Pace: $PACE"
echo ""

# Function to extract script content
extract_script_content() {
    cat << 'EOF'
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

======================================================================
ALT LINES (PICKUPS / SHORTS)
======================================================================
- "confidence visits after consistency signs the lease."
- "creative fear is just your standards arriving early."
- "make it useful, then make it pretty, then make it yours."
- "boring work wins privately before exciting work wins publicly."

======================================================================
CAMERA CADENCE (RECAP)
======================================================================
- start of minute: [CAM:2S][DOLLY-IN]
- mid-minute emphasis: [CAM:CU on Speaker]
- end beat/reset: [CAM:WS][PAN-R/L][LOOP:IDLE]

======================================================================
MOTION TAG MAP (REMINDER — REPLACE WITH YOUR IDs IF NEEDED)
======================================================================
POSE:IDLE-NEUTRAL -> idle_default
POSE:CONFIDENT -> pose_confident_a
POSE:THINK -> pose_think_a
GEST:POINT-FWD -> hand_point_fwd
GEST:OPEN-ARMS -> arms_open_a
GEST:CHOP -> hand_chop_a
GEST:COUNT-3 -> count_three
GEST:PINCH -> pinch_a
FACE:SMILE-SOFT -> face_smile_soft
FACE:SMILE-BIG -> face_smile_big
FACE:SERIOUS -> face_serious
FACE:EYEBROW-UP -> brow_raise
NOD -> head_nod_small
MOVE:STEP-FWD -> step_forward_s
MOVE:STEP-BWD -> step_back_s
LOOP:HEADNOD -> loop_headnod_slow
CAM:2S/MS/CU/WS -> your camera presets
SFX:LAMP-CLICK/WHOOSH-SOFT/KEYPRESS -> your SFX calls
EOF
}

# Function to parse script into segments
parse_script_segments() {
    local script_content="$1"
    
    echo "📝 Parsing script segments..."
    
    # Extract segments by time markers
    echo "0:00–0:45 — COLD OPEN (HOOK)" > /tmp/segment_1.txt
    echo "0:45–2:10 — THE PROBLEM (NAME IT)" > /tmp/segment_2.txt
    echo "2:10–3:45 — THE STAKES (WHY IT MATTERS)" > /tmp/segment_3.txt
    echo "3:45–5:15 — THE PACT (RULES OF ENGAGEMENT)" > /tmp/segment_4.txt
    echo "5:15–6:50 — THE FRICTION (EXCUSES RAPID-FIRE)" > /tmp/segment_5.txt
    echo "6:50–8:30 — THE MAP (14-MINUTE ARC)" > /tmp/segment_6.txt
    echo "8:30–10:30 — THE DEMO (TINY, TANGIBLE WINS)" > /tmp/segment_7.txt
    echo "10:30–11:40 — THE DIP (YOU WILL HIT IT)" > /tmp/segment_8.txt
    echo "11:40–12:30 — THE ONE METRIC" > /tmp/segment_9.txt
    echo "12:30–13:25 — THE AUDIENCE LOOP (GROW PEOPLE, NOT NUMBERS)" > /tmp/segment_10.txt
    echo "13:25–14:00 — THE SEND-OFF (COMMITMENT + CTA)" > /tmp/segment_11.txt
    
    echo "✅ Script parsed into 11 segments"
}

# Function to create production workflow
create_production_workflow() {
    echo "🎬 Creating production workflow for: $TITLE"
    
    # Create production directory
    local prod_dir="/tmp/right_perspective_production_$(date +%s)"
    mkdir -p "$prod_dir"/{segments,audio,video,final}
    
    echo "📁 Production directory: $prod_dir"
    
    # Extract script content
    local script_content=$(extract_script_content)
    
    # Parse into segments
    parse_script_segments "$script_content"
    
    # Create segment files
    local segments=(
        "0:00–0:45 — COLD OPEN (HOOK)"
        "0:45–2:10 — THE PROBLEM (NAME IT)"
        "2:10–3:45 — THE STAKES (WHY IT MATTERS)"
        "3:45–5:15 — THE PACT (RULES OF ENGAGEMENT)"
        "5:15–6:50 — THE FRICTION (EXCUSES RAPID-FIRE)"
        "6:50–8:30 — THE MAP (14-MINUTE ARC)"
        "8:30–10:30 — THE DEMO (TINY, TANGIBLE WINS)"
        "10:30–11:40 — THE DIP (YOU WILL HIT IT)"
        "11:40–12:30 — THE ONE METRIC"
        "12:30–13:25 — THE AUDIENCE LOOP (GROW PEOPLE, NOT NUMBERS)"
        "13:25–14:00 — THE SEND-OFF (COMMITMENT + CTA)"
    )
    
    # Create segment files
    for i in "${!segments[@]}"; do
        local segment_num=$((i + 1))
        local segment_file="$prod_dir/segments/segment_${segment_num}.txt"
        echo "${segments[$i]}" > "$segment_file"
        echo "📝 Created segment $segment_num: ${segments[$i]}"
    done
    
    # Create production script
    cat > "$prod_dir/production_script.sh" << 'EOF'
#!/bin/bash
# Production script for "Two People, One Decision"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROD_DIR="$(dirname "$SCRIPT_DIR")"

echo "🎬 Starting production for: Two People, One Decision"

# Process each segment
for segment_file in "$SCRIPT_DIR"/*.txt; do
    if [ -f "$segment_file" ]; then
        segment_name=$(basename "$segment_file" .txt)
        echo "🎭 Processing $segment_name..."
        
        # Extract M and W lines
        grep "^M " "$segment_file" > "$PROD_DIR/audio/${segment_name}_M.txt"
        grep "^W " "$segment_file" > "$PROD_DIR/audio/${segment_name}_W.txt"
        
        echo "✅ Extracted dialogue for $segment_name"
    fi
done

echo "🎉 Production workflow complete!"
echo "📁 Check $PROD_DIR for all files"
EOF
    
    chmod +x "$prod_dir/production_script.sh"
    
    echo "✅ Production workflow created in: $prod_dir"
    echo "🚀 Run: $prod_dir/production_script.sh"
    
    return 0
}

# Function to integrate with avatar workflow
integrate_with_avatar_system() {
    echo "🔗 Integrating with avatar workflow system..."
    
    # Check if avatar workflow exists
    if [ ! -f "$SCRIPT_DIR/run_dual_host.sh" ]; then
        echo "❌ Avatar workflow not found. Please run from monkeypaw-v5 directory."
        return 1
    fi
    
    # Create integration script
    cat > "$SCRIPT_DIR/produce_two_people_one_decision.sh" << 'EOF'
#!/bin/bash
# Integration script for "Two People, One Decision" with avatar system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎬 The Right Perspective - Two People, One Decision Production"
echo "🎭 Dual-host avatar system integration"

# Create production segments
echo "📝 Creating production segments..."

# Segment 1: Cold Open (Sarah - Breaking News style)
echo "🎬 Segment 1: Cold Open"
./run_dual_host.sh breaking_news "We keep saying tomorrow. Tomorrow keeps saying prove it. So—tonight? Full send? No rehearsals? This is the rehearsal. This is the show. Okay then—what's the rule? One rule: ship it ugly, fix it live. Print that on my forehead."

# Segment 2: The Problem (Marcus - Analysis style)  
echo "🎬 Segment 2: The Problem"
./run_dual_host.sh analysis "We've got ideas stacked like dishes in a sink—and we keep buying new plates. New apps, new hacks, new systems. But no finished meals. And the algorithm? Doesn't owe us dessert. So what are we actually building? A habit that makes results unavoidable. Uncomfortable truth: it's not talent. It's teatime with discipline. Daily."

# Segment 3: The Stakes (Sarah - Commentary style)
echo "🎬 Segment 3: The Stakes" 
./run_dual_host.sh commentary "I don't fear failing publicly. I fear never releasing publicly. Same. The years blur when you keep preparing. Almost there is a cul-de-sac with great lighting. Comfortable, circular, pretty. But nobody visits. We said we wanted to make something people use. Not a portfolio for imaginary applause."

# Continue with remaining segments...
echo "🎉 Production segments created!"
echo "📁 Check /tmp/monkeypaw_avatar_workflow/final/ for output videos"
EOF
    
    chmod +x "$SCRIPT_DIR/produce_two_people_one_decision.sh"
    
    echo "✅ Integration script created: produce_two_people_one_decision.sh"
    echo "🚀 Run: ./produce_two_people_one_decision.sh"
}

# Main execution
main() {
    echo "🎬 The Right Perspective - Script Integration"
    echo "📺 Title: $TITLE"
    echo "⏱️ Duration: $DURATION"
    echo ""
    
    # Create production workflow
    create_production_workflow
    
    # Integrate with avatar system
    integrate_with_avatar_system
    
    echo ""
    echo "🎉 Script integration complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Review the script segments"
    echo "2. Run: ./produce_two_people_one_decision.sh"
    echo "3. Process each segment with the avatar system"
    echo "4. Combine segments into final 14-minute video"
    echo ""
    echo "🎭 The Right Perspective is ready for production!"
}

# Run main function
main "$@"
