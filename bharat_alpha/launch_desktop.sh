#!/usr/bin/env bash
# ============================================================
# BharatAlpha Desktop App Launcher
# Ensures backend (port 8000) and frontend (port 5173) are running,
# then launches the Chrome Desktop Web App.
# ============================================================

set -e

PROJECT_DIR="/home/upc/every_thing_claude/bharat_alpha"
VENV_UVICORN="/home/upc/every_thing_claude/venv_bt/bin/uvicorn"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
LOG_DIR="${PROJECT_DIR}/logs"
URL="http://localhost:5173"

mkdir -p "$LOG_DIR"

# Check if port 5173 is listening
if ! nc -z 127.0.0.1 5173 >/dev/null 2>&1 && ! lsof -i :5173 >/dev/null 2>&1; then
    echo "Starting BharatAlpha backend (:8000)..."
    cd "$PROJECT_DIR"
    nohup env PYTHONPATH="$PROJECT_DIR" "$VENV_UVICORN" backend.main:app \
        --host 0.0.0.0 --port 8000 \
        > "$LOG_DIR/backend.log" 2>&1 &
    disown

    echo "Starting BharatAlpha frontend (:5173)..."
    cd "$FRONTEND_DIR"
    nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
    disown

    # Wait up to 10 seconds for frontend to become ready
    for i in {1..20}; do
        if nc -z 127.0.0.1 5173 >/dev/null 2>&1 || curl -s --max-time 1 "$URL" >/dev/null 2>&1; then
            break
        fi
        sleep 0.5
    done
fi

# Launch in Chrome app mode
if command -v google-chrome >/dev/null 2>&1; then
    exec google-chrome --app="$URL" "$@"
elif command -v brave-browser >/dev/null 2>&1; then
    exec brave-browser --app="$URL" "$@"
else
    exec xdg-open "$URL"
fi
