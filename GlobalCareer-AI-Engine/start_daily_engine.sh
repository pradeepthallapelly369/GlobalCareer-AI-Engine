#!/bin/bash
# Script to launch the GlobalCareer-AI-Engine in the background on a 2x daily schedule

cd "$(dirname "$0")"

echo "🚀 Starting the GlobalCareer AI Engine Scheduler (2x daily)..."

# Ensure venv exists and activate
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Kill any existing scheduled instances of main.py to prevent duplicates
pkill -f "main.py --schedule" || true

# Run it in the background so it survives terminal closure
nohup python main.py --schedule > logs/scheduler_output.log 2>&1 &

echo "✅ Engine is now running in the background!"
echo "It will automatically scrape, evaluate, tailor resumes, and email you drafts twice a day (9:30 AM & 9:30 PM IST)."
echo "You can view the live logs anytime by running: tail -f $(pwd)/logs/scheduler_output.log"
