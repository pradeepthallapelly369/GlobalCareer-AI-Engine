"""Test heuristic evaluation only (no LLM calls)."""
import os, sys, time, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("GlobalCareer")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from config.portals import PORTALS
from engine.job_aggregator import _scrape_single_portal, _job_hash

# First 5 fast portals
QUICK_PORTALS = [p for p in PORTALS if p["type"] in ("API", "RSS")][:5]

# Import heuristic evaluator directly
from engine.ai_evaluator import _evaluate_heuristic, EvalResult

def run_test():
    scan_start = time.time()
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M IST")
    logger.info("=" * 70)
    logger.info(f"🚀 Heuristic Test Eval at {scan_time} ({len(QUICK_PORTALS)} portals)")
    logger.info("=" * 70)

    all_jobs = []
    seen_hashes = set()
    portal_stats = {}

    for portal in QUICK_PORTALS:
        logger.info(f"  🔍 Scraping {portal['name']}...")
        try:
            jobs = _scrape_single_portal(portal)
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
            logger.info(f"  ❌ {portal['name']}: {e}")

    logger.info(f"\n📡 Raw jobs found: {len(all_jobs)} from {len(portal_stats)} active portals")

    if not all_jobs:
        logger.warning("No jobs to evaluate")
        return

    # Heuristic evaluation only
    logger.info("\n📊 Running Heuristic Evaluation (no LLM)...")
    matched = []
    for idx, job in enumerate(all_jobs):
        result = _evaluate_heuristic(job)
        if result.is_match and result.score >= 50:
            job["match_score"] = result.score
            job["eval_reason"] = result.reason
            matched.append(job)

    # Sort by score descending
    matched.sort(key=lambda x: x.get("match_score", 0), reverse=True)

    if matched:
        logger.info(f"\n🏆 MATCHED JOBS ({len(matched)}):")
        for i, j in enumerate(matched, 1):
            logger.info(f"  {i}. [{j.get('match_score')}] {j.get('title')} @ {j.get('company')}")
            logger.info(f"      Location: {j.get('location')[:50]}")
            logger.info(f"      Salary: {j.get('salary', 'N/A')[:30]}")
            logger.info(f"      Source: {j.get('source')}")
            logger.info(f"      Reason: {j.get('eval_reason')}")
            logger.info(f"      URL: {j.get('url')[:80]}")
            logger.info("")
    else:
        logger.info("\n❌ No jobs matched your criteria (threshold 50)")

    duration = time.time() - scan_start
    logger.info(f"\n{'=' * 70}")
    logger.info(f"✅ Heuristic Test Eval Complete in {duration:.1f}s")
    logger.info("=" * 70)
    sys.exit(0)

if __name__ == "__main__":
    run_test()