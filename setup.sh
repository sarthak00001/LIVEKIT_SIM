#!/bin/bash
echo "======================================"
echo "  Setup — Simulation Auto-Creator"
echo "======================================"

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found."
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# Install packages
echo ""
echo "📦 Installing packages..."
pip3 install playwright requests

# Install Chromium
echo ""
echo "🌐 Installing Chromium..."
python3 -m playwright install chromium

# Make scripts executable
chmod +x schedule.sh stop.sh

# Create logs folder
mkdir -p logs

echo ""
echo "======================================"
echo "✅ Setup done!"
echo ""
echo "NEXT STEPS:"
echo "  1. python3 run_simulation.py   ← run once, log in with Google"
echo "  2. bash schedule.sh            ← activate all 12 time slots"
echo "  3. bash stop.sh                ← to turn it all off"
echo "======================================"
