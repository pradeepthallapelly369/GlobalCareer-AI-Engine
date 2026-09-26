#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PORT=3030
URL="http://127.0.0.1:$PORT"

if curl -s --max-time 1 "$URL/api/config" >/dev/null 2>&1; then
    echo "AuraVoice backend is already running on $URL"
    exit 0
fi

echo "Starting AuraVoice server on $URL..."
mkdir -p "$DIR/logs"
setsid nohup /usr/bin/node "$DIR/server.js" >> "$DIR/logs/server.log" 2>&1 < /dev/null &
PID=$!

for i in {1..20}; do
    if curl -s --max-time 1 "$URL/api/config" >/dev/null 2>&1; then
        echo "AuraVoice started successfully (PID: $PID) on $URL."
        exit 0
    fi
    sleep 0.25
done

echo "AuraVoice server launched with PID $PID. Logs at $DIR/logs/server.log"
