#!/usr/bin/env bash
PORT=8088
URL="http://127.0.0.1:$PORT"
APP_DIR="/home/upc/every_thing_claude/colibri-studio"

# Ensure backend server is running
if ! curl -s --max-time 1 "$URL/api/status" > /dev/null 2>&1; then
    echo "Starting Colibrì Studio backend..."
    "$APP_DIR/start.sh"
    # Wait for server to become ready
    for i in {1..15}; do
        if curl -s --max-time 1 "$URL/api/status" > /dev/null 2>&1; then
            break
        fi
        sleep 0.5
    done
fi

# Launch standalone window via Google Chrome or default browser
if command -v google-chrome > /dev/null 2>&1; then
    exec google-chrome --app="$URL" --user-data-dir="$HOME/.config/colibri-studio-chrome" --class="ColibriStudio" "$@"
elif command -v xdg-open > /dev/null 2>&1; then
    exec xdg-open "$URL"
else
    echo "Please open $URL in your web browser."
fi
