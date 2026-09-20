#!/usr/bin/env bash
PORT=8088
PID=$(lsof -ti :$PORT)
if [ -n "$PID" ]; then
    kill -9 $PID
    echo "Stopped Colibrì Studio (PID: $PID)"
else
    echo "Colibrì Studio is not running on port $PORT"
fi
