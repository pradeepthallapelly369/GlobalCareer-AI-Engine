#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
# GlobalCareer AI Engine — Launch Script
# ══════════════════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  🌍 GlobalCareer AI Engine v2.0                      ${NC}"
echo -e "${CYAN}  Autonomous Job Hunting Machine                       ${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"

# Create venv if needed
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Install deps
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -q -r requirements.txt 2>/dev/null

# Create directories
mkdir -p data logs

case "${1:-scan}" in
    scan)
        echo -e "${GREEN}🔍 Running single scan...${NC}"
        python main.py --scan
        ;;
    schedule)
        echo -e "${GREEN}⏰ Starting scheduler (4x daily)...${NC}"
        python main.py --schedule
        ;;
    dashboard)
        echo -e "${GREEN}🌐 Starting dashboard at http://localhost:8888${NC}"
        python main.py --dashboard
        ;;
    both)
        echo -e "${GREEN}🚀 Starting dashboard + scheduler...${NC}"
        python main.py --dashboard &
        DASHBOARD_PID=$!
        sleep 2
        python main.py --schedule &
        SCHEDULER_PID=$!
        echo -e "${GREEN}Dashboard PID: $DASHBOARD_PID | Scheduler PID: $SCHEDULER_PID${NC}"
        wait
        ;;
    stats)
        echo -e "${GREEN}📊 Current Stats${NC}"
        python main.py --stats
        ;;
    *)
        echo "Usage: $0 {scan|schedule|dashboard|both|stats}"
        exit 1
        ;;
esac
