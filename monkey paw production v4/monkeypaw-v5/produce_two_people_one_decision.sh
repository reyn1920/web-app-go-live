#!/bin/bash
# The Right Perspective - "Two People, One Decision" Complete Production
# Full 14-minute duet with dual-host avatar system integration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRODUCTION_DIR="/tmp/two_people_one_decision_production"
FINAL_OUTPUT_DIR="/tmp/right_perspective_final"

echo "🎬 The Right Perspective - Two People, One Decision"
echo "📺 Full 14-minute duet production with dual-host avatars"
echo "🎭 Cast: Sarah Chen (W) & Marcus Johnson (M)"
echo ""

# Check if script parser has been run
if [ ! -d "$PRODUCTION_DIR" ]; then
    echo "📝 Running script parser first..."
    python3 "$SCRIPT_DIR/script_parser.py"
fi

# Create final output directory
mkdir -p "$FINAL_OUTPUT_DIR"/{segments,combined,final}

echo "🎬 Starting production workflow..."

# Function to process segment with avatar system
process_segment() {
    local segment_num="$1"
    local segment_title="$2"
    local content_type="$3"
    local text="$4"
    local host="$5"
    
    echo "🎭 Processing Segment $segment_num: $segment_title"
    echo "📝 Content Type: $content_type"
    echo "👤 Host: $host"
    echo "📄 Text: ${text:0:100}..."
    
    # Run the avatar workflow
    if [ "$host" = "custom" ]; then
        "$SCRIPT_DIR/run_dual_host.sh" "$content_type" "$text" "$host"
    else
        "$SCRIPT_DIR/run_dual_host.sh" "$content_type" "$text"
    fi
    
    # Move output to final directory
    if [ -d "/tmp/monkeypaw_avatar_workflow/final" ]; then
        local output_file=$(find /tmp/monkeypaw_avatar_workflow/final -name "*.mp4" -type f | head -1)
        if [ -f "$output_file" ]; then
            cp "$output_file" "$FINAL_OUTPUT_DIR/segments/segment_${segment_num:02d}_${segment_title// /_}.mp4"
            echo "✅ Segment $segment_num saved"
        else
            echo "⚠️ No output file found for segment $segment_num"
        fi
    fi
    
    echo ""
}

# Process all segments
echo "🚀 Processing 11 segments..."

# Segment 1: Cold Open (Sarah - Breaking News)
process_segment 1 "COLD_OPEN_HOOK" "breaking_news" "We keep saying tomorrow. Tomorrow keeps saying prove it. So—tonight? Full send? No rehearsals? This is the rehearsal. This is the show. Okay then—what's the rule? One rule: ship it ugly, fix it live. Print that on my forehead." "female"

# Segment 2: The Problem (Marcus - Analysis)
process_segment 2 "THE_PROBLEM" "analysis" "We've got ideas stacked like dishes in a sink—and we keep buying new plates. New apps, new hacks, new systems. But no finished meals. And the algorithm? Doesn't owe us dessert. So what are we actually building? A habit that makes results unavoidable. Uncomfortable truth: it's not talent. It's teatime with discipline. Daily. No candles, no vibe lighting. Just work that shows up even when you don't want to. Say it plain. Okay—consistency beats charisma when charisma sleeps in. And our charisma hits the snooze. Today we fire the snooze." "male"

# Segment 3: The Stakes (Sarah - Commentary)
process_segment 3 "THE_STAKES" "commentary" "I don't fear failing publicly. I fear never releasing publicly. Same. The years blur when you keep preparing. Almost there is a cul-de-sac with great lighting. Comfortable, circular, pretty. But nobody visits. We said we wanted to make something people use. Not a portfolio for imaginary applause. So the stakes are simple. Ship today, change tomorrow. Or stall today, repeat yesterday." "female"

# Segment 4: The Pact (Sarah - Commentary)
process_segment 4 "THE_PACT" "commentary" "Pact time. Three rules. Rule one: output over optics. If it works, keep it—even if it's ugly. Rule two: do it scared. We act before confidence, not after. Rule three: one improvement per day is compounding interest. A refrain to remember—start. ship. study. Start the thing. Ship the version. Study the feedback. Then repeat till boredom looks impressed." "female"

# Segment 5: The Friction (Marcus - Analysis)
process_segment 5 "THE_FRICTION" "analysis" "I need the right gear. The right gear needs the right hands. Use yours. The market is saturated. Saturated markets still drink excellence. Someone already did it. No one did it like you for these people at this time. I'm not ready. Readiness is a luxury built by reps. What if they hate it? Then you'll know what to fix by Friday. What if they love it? Then you work harder by Monday. Either way—we win." "male"

# Segment 6: The Map (Sarah - Breaking News)
process_segment 6 "THE_MAP" "breaking_news" "Here's our plan, and yes—it fits in fourteen minutes. Minute one was our hook. Minute two named the problem. Minute three set the stakes. Minute four made the pact. Minutes five and six cleared excuses. Minutes seven through nine? Demonstrations. Minute ten: the dip—and how to cross it. Minute eleven: one metric that actually matters. Minute twelve: audience loop and feedback system. Minute thirteen: the wall we are absolutely going to hit—and minute fourteen: the send-off you can't ignore. Sound fast? Good. Speed is a design constraint. Speed forces clarity. Clarity unlocks action." "female"

# Segment 7: The Demo (Marcus - Analysis)
process_segment 7 "THE_DEMO" "analysis" "Demo one: the two-minute publish. Pick one idea you shared with a friend this week. Open your notes. Paste it as a 3-sentence post. Add one practical step. Press publish. Time it—two minutes. Done? That was a rep. Demo two: the one-take lesson. Hit record. Explain one mistake you made today and how you'll avoid it tomorrow. No cuts. 60–90 seconds. Title: I learned this the hard way. Upload. That's signal people can use. Demo three: the feedback form. Three questions: 1) what helped? 2) what confused? 3) what do you want next? Link it. Pin it. Ask for three answers a day. Now you're not guessing—you're iterating." "male"

# Segment 8: The Dip (Sarah - Commentary)
process_segment 8 "THE_DIP" "commentary" "The dip is coming. Always. Views stall. Sales flatline. Dopamine takes PTO. The dip is where amateurs pivot to new projects. Pros pivot their process. How? By shrinking the loop: start → ship → study in 24 hours. The daily loop makes the dip shorter than your attention span. And if you can outlast your attention span—you outlast most people." "female"

# Segment 9: The One Metric (Marcus - Analysis)
process_segment 9 "THE_ONE_METRIC" "analysis" "We track one thing this month: kept promises to yourself. Not likes, not views. Promises kept. Did I publish the thing I said I'd publish? Did I improve one step of the pipeline? If the answer is yes five days a week—compounding begins to feel like cheating. And if it's a no—no self-court, no trial. Just a shorter loop tomorrow." "male"

# Segment 10: The Audience Loop (Sarah - Commentary)
process_segment 10 "THE_AUDIENCE_LOOP" "commentary" "Audience isn't a crowd; it's a cohort. Cohorts need predictable value. Pick your pillar: teach, entertain, or enable. Pick your promise: every weekday, a 60-second fix (or your cadence). Pick your path: newsletter, community, product. Then over-deliver quietly every tenth post. Surprise creates stories. Stories create shares. Shares create tomorrow's baseline." "female"

# Segment 11: The Send-Off (Sarah - Breaking News)
process_segment 11 "THE_SEND_OFF" "breaking_news" "So—we done stalling? I brought the publish button. I brought the timer. Three breaths. Two words. Ship it. Then come back here. Same time tomorrow. Start. ship. study." "female"

echo "🎉 All segments processed!"
echo "📁 Segments saved in: $FINAL_OUTPUT_DIR/segments/"

# List generated files
echo ""
echo "📄 Generated segment files:"
ls -la "$FINAL_OUTPUT_DIR/segments/" | grep "\.mp4$" || echo "No MP4 files found"

echo ""
echo "🎬 Production workflow complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review individual segments in: $FINAL_OUTPUT_DIR/segments/"
echo "2. Combine segments into final 14-minute video"
echo "3. Add transitions and final polish"
echo "4. Upload to The Right Perspective channel"
echo ""
echo "🎭 The Right Perspective - Two People, One Decision is ready!"
