"""
GlobalCareer AI Engine — Main Entry Point
Autonomous job hunting machine: Scan → Evaluate → Track → Email → Cold Outreach
"""

import os
import sys
import time
import logging
from datetime import datetime

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(LOG_DIR, "scanner.log"), encoding="utf-8"),
    ]
)
logger = logging.getLogger("GlobalCareer")

# Load env
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from engine.job_aggregator import aggregate_all_jobs
from engine.ai_evaluator import filter_and_score_jobs
from engine.application_tracker import add_jobs_batch, record_scan, get_stats, update_status
from engine.email_notifier import send_digest_email, save_report_markdown
from engine.cold_emailer import batch_generate_cold_emails, send_cold_email
try:
    from engine.resume_optimizer import optimize_resume_for_jd
except ImportError:
    optimize_resume_for_jd = None

def run_scan():
    """Execute a single scan cycle."""
    scan_start = time.time()
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M IST")

    logger.info("=" * 70)
    logger.info(f"🚀 GlobalCareer AI Engine — Scan Starting at {scan_time}")
    logger.info("=" * 70)

    # 1. Aggregate jobs from all portals
    logger.info("\n📡 Phase 1: Aggregating jobs from 300+ portals across 80+ countries...")
    all_jobs, portal_stats = aggregate_all_jobs(max_workers=10)
    logger.info(f"   Found {len(all_jobs)} raw jobs from {len(portal_stats)} active portals")

    if not all_jobs:
        logger.warning("No jobs found this scan. Sending empty report.")
        send_digest_email([], portal_stats)
        return

    # 2. Evaluate and score
    logger.info("\n📊 Phase 2: AI Evaluation & Scoring...")
    matched_jobs = filter_and_score_jobs(all_jobs, threshold=50)
    logger.info(f"   {len(matched_jobs)} jobs passed evaluation")

    # 3. Save to database
    logger.info("\n💾 Phase 3: Saving to database...")
    added = add_jobs_batch(matched_jobs)
    logger.info(f"   {added} new jobs saved")

    # 4. Generate cold email drafts
    logger.info("\n📧 Phase 4: Generating cold email drafts & Auto-Tailoring...")
    cold_emails = batch_generate_cold_emails(matched_jobs, max_emails=10)
    
    # Auto-tailor and send drafts to user for top jobs (>80 score)
    tailored_count = 0
    applied_jobs_summary = []
    
    for job, email_data in zip(matched_jobs, cold_emails):
        if job.get("match_score", 0) >= 50:
            tailored = None
            if optimize_resume_for_jd:
                logger.info(f"   Auto-tailoring assets for: {job.get('title')}...")
                try:
                    tailored = optimize_resume_for_jd(
                        job_title=job.get("title", ""),
                        company=job.get("company", ""),
                        jd_text=job.get("description", "")[:2000],
                        country=job.get("region", "Global")
                    )
                    update_status(job.get("id", ""), "Auto-Tailored", "Resume & Cover Letter generated")
                    tailored_count += 1
                except Exception as e:
                    logger.debug(f"Tailoring failed: {e}")
            
            # Send the drafted cold email to the USER so they can easily forward it to recruiters
            from config.settings import TARGET_EMAIL
            email_data["subject"] = "[DRAFT] " + email_data["subject"]
            email_data["body"] = (
                f"Your tailored resume and cover letter for {job.get('company')} have been generated and saved locally.\n\n"
                f"Job URL: {job.get('url')}\n\n"
                f"--- Suggested Recruiter Pitch ---\n\n"
                f"{email_data['body']}\n\n"
                f"--- Tailored Cover Letter ---\n\n"
                f"{tailored.get('cover_letter_markdown', '')}\n\n"
                f"--- Tailored Resume ---\n\n"
                f"{tailored.get('tailored_resume_markdown', '')}"
            ) if tailored else email_data["body"]
            
            success = send_cold_email(email_data, to_address=TARGET_EMAIL)
            if success:
                applied_jobs_summary.append({"title": job.get("title", ""), "company": job.get("company", ""), "url": job.get("url", "N/A")})

    logger.info(f"   {len(cold_emails)} cold emails generated, {tailored_count} resumes tailored")
    
    if applied_jobs_summary:
        summary_lines = ["Here is the summary of jobs that were automatically applied (tailored and drafted) in this scheduled run:\n"]
        for i, aj in enumerate(applied_jobs_summary, 1):
            summary_lines.append(f"{i}. {aj['title']} at {aj['company']}")
            summary_lines.append(f"   URL: {aj['url']}\n")
        
        summary_body = "\n".join(summary_lines)
        summary_email_data = {
            "subject": f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Scheduled Auto-Apply Summary Report",
            "body": summary_body
        }
        logger.info(f"📧 Sending summary report to {TARGET_EMAIL}...")
        send_cold_email(summary_email_data, to_address=TARGET_EMAIL)
        logger.info("✅ Summary report sent!")

    # 5. Send digest email
    logger.info("\n📨 Phase 5: Sending digest email...")
    send_digest_email(matched_jobs, portal_stats)

    # 6. Save local report
    logger.info("\n📄 Phase 6: Saving local report...")
    save_report_markdown(matched_jobs, portal_stats)

    # 7. Record scan stats
    duration = time.time() - scan_start
    total_scanned = sum(portal_stats.values()) if portal_stats else len(all_jobs)
    record_scan(total_scanned, len(matched_jobs), len(portal_stats), portal_stats, duration)

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info(f"✅ Scan Complete in {duration:.1f}s")
    logger.info(f"   📡 Portals Active: {len(portal_stats)}")
    logger.info(f"   🔍 Total Scanned: {total_scanned}")
    logger.info(f"   🎯 Matched: {len(matched_jobs)}")
    logger.info(f"   📧 Cold Emails: {len(cold_emails)}")
    logger.info(f"   💾 Saved: {added}")

    stats = get_stats()
    logger.info(f"   📊 Total in DB: {stats['total_jobs']} | Scans: {stats['total_scans']}")
    logger.info("=" * 70)

    return {
        "matched": len(matched_jobs),
        "total_scanned": total_scanned,
        "portals_active": len(portal_stats),
        "duration": duration,
        "cold_emails": len(cold_emails),
    }

def run_scheduler():
    """Run the scan on schedule (4x daily)."""
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.error("APScheduler not installed. Run: pip install apscheduler")
        logger.info("Running single scan instead...")
        run_scan()
        return

    scheduler = BlockingScheduler()

    # 4 daily scans (IST = UTC+5:30, so convert to UTC)
    # 06:00 IST = 00:30 UTC
    # 12:00 IST = 06:30 UTC
    # 18:00 IST = 12:30 UTC
    # 23:00 IST = 17:30 UTC
    scheduler.add_job(run_scan, CronTrigger(hour=0, minute=30), id="scan_morning")
    scheduler.add_job(run_scan, CronTrigger(hour=6, minute=30), id="scan_midday")
    scheduler.add_job(run_scan, CronTrigger(hour=12, minute=30), id="scan_evening")
    scheduler.add_job(run_scan, CronTrigger(hour=17, minute=30), id="scan_night")

    logger.info("⏰ Scheduler started — scanning 4x daily (6AM, 12PM, 6PM, 11PM IST)")
    logger.info("   Running initial scan now...")
    run_scan()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GlobalCareer AI Engine")
    parser.add_argument("--scan", action="store_true", help="Run a single scan")
    parser.add_argument("--schedule", action="store_true", help="Start scheduler (4x daily)")
    parser.add_argument("--dashboard", action="store_true", help="Start web dashboard")
    parser.add_argument("--stats", action="store_true", help="Show current stats")
    args = parser.parse_args()

    if args.dashboard:
        from dashboard.app import start_dashboard
        start_dashboard()
    elif args.schedule:
        run_scheduler()
    elif args.stats:
        stats = get_stats()
        print("\n📊 GlobalCareer AI Engine — Stats")
        print("=" * 40)
        for k, v in stats.items():
            print(f"  {k}: {v}")
    else:
        # Default: single scan
        run_scan()
