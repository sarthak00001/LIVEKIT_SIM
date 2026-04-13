#!/bin/bash
# ─────────────────────────────────────────────
# Schedule — fires at EXACT times on Mac
# 11:57, 12:27, 12:57, 13:27, 13:57, 14:27,
# 14:57, 15:27, 15:57, 16:27, 16:57, 17:27
# ─────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_PATH="$(which python3)"

echo "📁 Script dir: $SCRIPT_DIR"
echo "🐍 Python:     $PYTHON_PATH"

# Each slot gets its own plist (launchd fires at exact clock times)
declare -A SLOTS=(
    ["1157"]="11 57"
    ["1227"]="12 27"
    ["1257"]="12 57"
    ["1327"]="13 27"
    ["1357"]="13 57"
    ["1427"]="14 27"
    ["1457"]="14 57"
    ["1527"]="15 27"
    ["1557"]="15 57"
    ["1627"]="16 27"
    ["1657"]="16 57"
    ["1727"]="17 27"
)

for KEY in "${!SLOTS[@]}"; do
    TIMES=(${SLOTS[$KEY]})
    HOUR=${TIMES[0]}
    MIN=${TIMES[1]}
    PLIST_NAME="com.tfu.simulation.$KEY"
    PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"

    cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SCRIPT_DIR/run_simulation.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>$HOUR</integer>
        <key>Minute</key>
        <integer>$MIN</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/logs/simulation_$KEY.log</string>

    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/logs/simulation_$KEY.log</string>
</dict>
</plist>
EOF

    launchctl unload "$PLIST_PATH" 2>/dev/null
    launchctl load "$PLIST_PATH"
    echo "✅ Scheduled $HOUR:$MIN"
done

mkdir -p "$SCRIPT_DIR/logs"

echo ""
echo "══════════════════════════════════════"
echo "✅ All 12 slots scheduled!"
echo ""
echo "Slots: 11:57 12:27 12:57 13:27 13:57"
echo "       14:27 14:57 15:27 15:57 16:27"
echo "       16:57 17:27"
echo ""
echo "Logs:  $SCRIPT_DIR/logs/"
echo ""
echo "To stop ALL:  bash stop.sh"
echo "To run now:   python3 $SCRIPT_DIR/run_simulation.py"
echo "══════════════════════════════════════"
