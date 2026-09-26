#!/usr/bin/env bash
PORT=3030
PID=$(lsof -ti tcp:$PORT 2>/dev/null || true)
if [ -n "$PID" ]; then
    kill -9 $PID 2>/dev/null || true
    echo "AuraVoice server stopped (PID: $PID)."
else
    echo "AuraVoice server is not running on port $PORT."
fi
