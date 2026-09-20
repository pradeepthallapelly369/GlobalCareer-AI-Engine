#!/usr/bin/env bash
PORT=8088
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "✓ Colibrì Studio is RUNNING on http://127.0.0.1:$PORT"
    curl -s http://127.0.0.1:$PORT/api/status | grep -o '"is_ready":true' && echo "✓ Engine Binaries Ready"
else
    echo "✗ Colibrì Studio is STOPPED"
fi
