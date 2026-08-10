"""
Overnight Background Job Scout & Auto-Applier Daemon
Runs continuously in the background to scout global remote Data Engineering & BI roles (>=85% match),
generating tailored ATS resumes and cover letters while you sleep.
"""

import time
import sys
from engine.auto_applier import run_auto_apply_pipeline

def start_overnight_daemon():
    print("🌙 [Overnight Daemon] Active! Scouting worldwide remote Data & BI roles paying USD/EUR...")
    interval_seconds = 1800  # Run every 30 minutes
    
    while True:
        try:
            print("\n🔍 [Overnight Daemon] Executing scheduled scouting sweep...")
            run_auto_apply_pipeline(max_jobs=20, target_country="GLOBAL_REMOTE")
        except Exception as e:
            print(f"⚠️ [Overnight Daemon] Error during sweep: {e}")
        
        print(f"💤 [Overnight Daemon] Sleeping for 30 minutes until next sweep...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    start_overnight_daemon()
