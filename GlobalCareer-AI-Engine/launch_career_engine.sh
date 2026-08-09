#!/usr/bin/env bash
# ============================================================
# GlobalCareer AI Engine — Automated Dashboard Launcher
# Starts FastAPI server on port :5060 and opens browser UI
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=5070
URL="http://127.0.0.1:$PORT"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      GLOBAL CAREER AI ENGINE — PRADEEP THALLAPELLY            ║"
echo "║  🎯 Senior BI Developer | Data Engineer | Technical Lead      ║"
echo "║  🌐 Target: Remote Foreign Currency (USD/EUR) & Visa Relocation║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Clean port 5060 if occupied
fuser -k $PORT/tcp 2>/dev/null || true
sleep 1

# Detect Python and uvicorn executable
if [ -f "$SCRIPT_DIR/../venv_bt/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/../venv_bt/bin/python"
    UVICORN_CMD="$SCRIPT_DIR/../venv_bt/bin/python -m uvicorn"
elif command -v uvicorn > /dev/null 2>&1; then
    PYTHON_CMD="python3"
    UVICORN_CMD="uvicorn"
else
    PYTHON_CMD="python3"
    UVICORN_CMD="python3 -m uvicorn"
fi

# Auto-ensure dependencies in venv
$PYTHON_CMD -m pip install pyyaml fastapi uvicorn requests python-multipart > /dev/null 2>&1 || true

echo "🚀 Starting GlobalCareer AI Server on port $PORT..."
cd "$SCRIPT_DIR"
PYTHONPATH="$SCRIPT_DIR" $UVICORN_CMD dashboard.app:app --host 0.0.0.0 --port $PORT > /tmp/global_career.log 2>&1 &
SERVER_PID=$!

sleep 3

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ Server failed to start! Error details below:"
    cat /tmp/global_career.log
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ GlobalCareer AI Dashboard is LIVE!"
echo ""
echo "  🌐 Dashboard URL: $URL"
echo ""
echo "  Features Active:"
echo "  • 🎯 JD-Based ATS Resume & Recruiter Pitch Generator"
echo "  • 📡 Live USD/EUR Remote & Visa Sponsorship Job Stream"
echo "  • 📊 Application Lifecycle Tracker"
echo "  • 💼 Copy-Paste Optimized LinkedIn Sections"
echo ""
echo "  Press Ctrl+C to stop the server."
echo "════════════════════════════════════════════════════════════════"

# Launch web browser
if command -v google-chrome &> /dev/null; then
    google-chrome --app="$URL" > /dev/null 2>&1 &
elif command -v xdg-open &> /dev/null; then
    xdg-open "$URL" > /dev/null 2>&1 &
else
    python3 -m webbrowser "$URL" > /dev/null 2>&1 &
fi

cleanup() {
    echo ""
    echo "🛑 Shutting down GlobalCareer AI Server..."
    kill $SERVER_PID 2>/dev/null || true
    fuser -k $PORT/tcp 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

wait
