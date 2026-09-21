#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PORT=8088
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 || nc -z 127.0.0.1 $PORT >/dev/null 2>&1; then
    echo "Colibrì Studio is already running on http://127.0.0.1:$PORT"
    exit 0
fi

echo "Starting Colibrì Studio on http://127.0.0.1:$PORT..."
nohup /home/upc/every_thing_claude/venv_bt/bin/python3 "$DIR/server/app.py" > "$DIR/server.log" 2>&1 &
PID=$!
disown
echo "Colibrì Studio started with PID $PID."
echo "Access the dashboard at: http://127.0.0.1:$PORT"
