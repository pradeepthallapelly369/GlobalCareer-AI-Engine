#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo " 🌐 Starting AetherMind 70B Local Agent Server..."
echo " Dashboard: http://localhost:7860"
echo "=========================================================="

python3 -m pip install -q -r requirements.txt || true

python3 app.py
