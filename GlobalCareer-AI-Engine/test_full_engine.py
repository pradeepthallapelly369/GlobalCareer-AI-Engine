"""Test full GlobalCareer engine with curated roles + fast portals."""
import os, sys, time, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("GlobalCareer")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from engine.global_job_scout import scout_all_global_jobs
from engine.ai_evaluator import filter_and_score_jobs
from engine.application_tracker import add_jobs_batch, record_scan, get_stats
from engine.email_notifier import send_digest_email, save_report_markdown

def run_test():
    scan_start = time.time()
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M IST")
    logger.info("=" * 70)
    logger.info(f"🚀 Full Engine Test at {scan_time}")
    logger.info("=" * 70)

    # 1. Scout all jobs (curated + fast portals)
    logger.info("\n📡 Phase 1: Global Job Scouting...")
    all_jobs = scout_all_global_jobs()
    logger.info(f"   Found {len(all_jobs)} total opportunities")

    if not all_jobs:
        logger.warning("No jobs found")
        return

    # 2. Evaluate and score (use heuristic for speed)
    logger.info("\n📊 Phase 2: AI Evaluation & Scoring...")
    matched_jobs = filter_and_score_jobs(all_jobs, threshold=50)
    logger.info(f"   {len(matched_jobs)} jobs passed evaluation (score >= 50)")

    if matched_jobs:
        logger.info("\n🏆 TOP MATCHES:")
        for i, j in enumerate(matched_jobs[:20], 1):
            score = j.get("match_score", "?")
            logger.info(f"  {i}. [{score}] {j.get('title')} @ {j.get('company')}")
            logger.info(f"      Location: {j.get('location')[:60]}")
            logger.info(f"      Type: {j.get('type', j.get('salary', 'N/A'))[:50]}")
            logger.info(f"      Source: {j.get('source')}")
            logger.info(f"      Reason: {j.get('eval_reason', 'N/A')[:100]}")
            logger.info("")

    # 3. Save to database
    logger.info("\n💾 Phase 3: Saving to database...")
    added = add_jobs_batch(matched_jobs)
    logger.info(f"   {added} new jobs saved")

    # 4. Send digest email
    logger.info("\n📨 Phase 4: Sending digest email...")
    portal_stats = {}
    for j in all_jobs:
        src = j.get("source", "Unknown")
        portal_stats[src] = portal_stats.get(src, 0) + 1
    send_digest_email(matched_jobs, portal_stats)

    # 5. Save report
    logger.info("\n📄 Phase 5: Saving local report...")
    save_report_markdown(matched_jobs, portal_stats)

    # Stats
    duration = time.time() - scan_start
    stats = get_stats()
    logger.info(f"\n{'=' * 70}")
    logger.info(f"✅ Full Engine Test Complete in {duration:.1f}s")
    logger.info(f"   📡 Sources: {len(portal_stats)}")
    logger.info(f"   🔍 Total Scanned: {len(all_jobs)}")
    logger.info(f"   🎯 Matched: {len(matched_jobs)}")
    logger.info(f"   💾 New Saved: {added}")
    logger.info(f"   📊 Total in DB: {stats.get('total_jobs', 0)} | Scans: {stats.get('total_scans', 0)}")
    logger.info("=" * 70)
    sys.exit(0)

if __name__ == "__main__":
    run_test()