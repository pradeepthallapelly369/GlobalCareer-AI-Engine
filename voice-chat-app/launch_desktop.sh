#!/usr/bin/env bash
PORT=3030
URL="http://127.0.0.1:$PORT"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure backend server is running
if ! curl -s --max-time 1 "$URL/api/config" > /dev/null 2>&1; then
    echo "Starting AuraVoice server..."
    "$APP_DIR/start.sh"
fi

# Chrome / Chromium app-mode flags for clean standalone native desktop window
CHROME_FLAGS="--app=$URL --user-data-dir=$HOME/.config/auravoice-chrome --class=AuraVoice --name=AuraVoice --window-size=1200,850"

if command -v google-chrome > /dev/null 2>&1; then
    exec google-chrome $CHROME_FLAGS "$@"
elif command -v brave-browser > /dev/null 2>&1; then
    exec brave-browser $CHROME_FLAGS "$@"
elif command -v xdg-open > /dev/null 2>&1; then
    exec xdg-open "$URL"
else
    echo "Please open $URL in your web browser."
fi
