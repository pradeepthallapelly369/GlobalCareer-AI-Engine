#!/usr/bin/env bash
# ============================================================
#  BharatAlpha AI — One-Click Launcher
#  Starts FastAPI backend (port 8000) + Vite frontend (port 5173)
#  then opens the dashboard in the default browser.
# ============================================================

set -e

PROJECT_DIR="/home/upc/every_thing_claude/bharat_alpha"
VENV_PYTHON="/home/upc/every_thing_claude/venv_bt/bin/python3"
VENV_UVICORN="/home/upc/every_thing_claude/venv_bt/bin/uvicorn"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
LOG_DIR="${PROJECT_DIR}/logs"

mkdir -p "$LOG_DIR"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   BharatAlpha AI — 50-Year Veteran Market Intelligence  ║"
echo "║   Indian Stock Market Investment & Algo-Trading Engine   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── Kill any stale processes on our ports ──────────────────────
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true
sleep 1

# ── 1. Start FastAPI Backend (port 8000) ──────────────────────
echo "🚀 Starting FastAPI backend server on http://localhost:8000 ..."
cd "$PROJECT_DIR"
PYTHONPATH="$PROJECT_DIR" "$VENV_UVICORN" backend.main:app \
    --host 0.0.0.0 --port 8000 \
    > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# ── 2. Start Vite Frontend (port 5173) ────────────────────────
echo "🎨 Starting Vite frontend dashboard on http://localhost:5173 ..."
cd "$FRONTEND_DIR"
npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# ── 3. Wait for servers to be ready ───────────────────────────
echo ""
echo "⏳ Waiting for servers to come online..."
sleep 4

# ── 4. Open browser ───────────────────────────────────────────
echo "🌐 Opening BharatAlpha AI Dashboard in browser..."
xdg-open "http://localhost:5173" 2>/dev/null || \
  sensible-browser "http://localhost:5173" 2>/dev/null || \
  echo "   Open http://localhost:5173 in your browser manually."

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ BharatAlpha AI is LIVE!"
echo "     Dashboard : http://localhost:5173"
echo "     API Docs  : http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to shut down both servers."
echo "════════════════════════════════════════════════════════════"

# ── Trap Ctrl+C to cleanly kill both processes ─────────────────
cleanup() {
    echo ""
    echo "🛑 Shutting down BharatAlpha AI..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    fuser -k 8000/tcp 2>/dev/null || true
    fuser -k 5173/tcp 2>/dev/null || true
    echo "   Goodbye! 👋"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script alive until user presses Ctrl+C
wait
