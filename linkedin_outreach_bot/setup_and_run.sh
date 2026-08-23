#!/bin/bash
# Script to install dependencies and run the LinkedIn Outreach Bot

cd "$(dirname "$0")"

echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing Playwright..."
pip install -r requirements.txt

echo "🌐 Installing Playwright Chromium browsers (if missing)..."
python -m playwright install chromium

echo "🧹 Cleaning up any orphaned browser processes..."
pkill -f "chrome_data" || true
pkill -f "chromium" || true
sleep 1

echo "🚀 Starting LinkedIn Outreach Bot..."
python outreach.py
