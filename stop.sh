#!/bin/bash
# Removes all simulation scheduler jobs from Mac launchd

SLOTS=("1157" "1227" "1257" "1327" "1357" "1427" "1457" "1527" "1557" "1627" "1657" "1727")

for KEY in "${SLOTS[@]}"; do
    PLIST_NAME="com.tfu.simulation.$KEY"
    PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"
    if [ -f "$PLIST_PATH" ]; then
        launchctl unload "$PLIST_PATH" 2>/dev/null
        rm "$PLIST_PATH"
        echo "🗑️  Removed $PLIST_NAME"
    fi
done

echo ""
echo "✅ All simulation schedules removed."
