"""Quick scan — API/RSS portals only (no slow JobSpy)."""
import os, sys, time, logging
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("GlobalCareer")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Only fast API/RSS portals — skip all JOBSPY
from config.portals import PORTALS
from engine.job_aggregator import _scrape_single_portal, _job_hash
from engine.ai_evaluator import filter_and_score_jobs
from engine.application_tracker import add_jobs_batch, record_scan, get_stats
from engine.email_notifier import send_digest_email, save_report_markdown
import hashlib

QUICK_PORTALS = [p for p in PORTALS if p["type"] in ("API", "RSS")]

def run_quick_scan():
    scan_start = time.time()
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M IST")
    logger.info("=" * 70)
    logger.info(f"🚀 Quick Scan Starting at {scan_time} ({len(QUICK_PORTALS)} fast portals)")
    logger.info("=" * 70)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    all_jobs = []
    seen_hashes = set()
    portal_stats = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(_scrape_single_portal, p): p for p in QUICK_PORTALS}
        for future in as_completed(futures):
            portal = futures[future]
            try:
                jobs = future.result()
                count = 0
                for job in jobs:
                    h = _job_hash(job.get("title", ""), job.get("company", ""), job.get("url", ""))
                    if h not in seen_hashes:
                        seen_hashes.add(h)
                        job["id"] = h
                        all_jobs.append(job)
                        count += 1
                if count > 0:
                    portal_stats[portal["name"]] = count
                    logger.info(f"  ✅ {portal['name']}: {count} jobs")
            except Exception as e:
                logger.debug(f"  ⚠️ {portal['name']}: {e}")

    logger.info(f"\n📡 Raw jobs found: {len(all_jobs)} from {len(portal_stats)} active portals")

    if not all_jobs:
        logger.warning("No jobs found. Sending empty report.")
        send_digest_email([], portal_stats)
        return

    # Score & filter
    logger.info("\n📊 AI Evaluation & Scoring...")
    matched_jobs = filter_and_score_jobs(all_jobs, threshold=50)
    logger.info(f"   {len(matched_jobs)} jobs passed evaluation (score >= 50)")

    if matched_jobs:
        # Print top matches
        logger.info("\n🏆 TOP MATCHES:")
        for i, j in enumerate(matched_jobs[:15], 1):
            score = j.get("match_score", "?")
            logger.info(f"  {i}. [{score}] {j.get('title')} @ {j.get('company')} — {j.get('source', '')}")

    # Save to DB
    added = add_jobs_batch(matched_jobs)
    logger.info(f"\n💾 Saved {added} new jobs to database")

    # Generate email
    logger.info("\n📨 Sending digest email...")
    send_digest_email(matched_jobs, portal_stats)

    # Save report
    save_report_markdown(matched_jobs, portal_stats)

    # Stats
    duration = time.time() - scan_start
    stats = get_stats()
    logger.info(f"\n{'=' * 70}")
    logger.info(f"✅ Quick Scan Complete in {duration:.1f}s")
    logger.info(f"   📡 Active Portals: {len(portal_stats)}")
    logger.info(f"   🔍 Total Found: {len(all_jobs)}")
    logger.info(f"   🎯 Matched (≥50): {len(matched_jobs)}")
    logger.info(f"   💾 New Saved: {added}")
    logger.info(f"   📊 Total in DB: {stats.get('total_jobs', 0)} | Scans: {stats.get('total_scans', 0)}")
    logger.info("=" * 70)

if __name__ == "__main__":
    run_quick_scan()
