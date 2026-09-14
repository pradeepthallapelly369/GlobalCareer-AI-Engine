"""Debug scrape — sequential, no threading."""
import os, sys, time, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("GlobalCareer")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from config.portals import PORTALS
from engine.job_aggregator import _scrape_single_portal, _job_hash

# Just first 3 fast portals
QUICK_PORTALS = [p for p in PORTALS if p["type"] in ("API", "RSS")][:3]

def run_test():
    scan_start = time.time()
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M IST")
    logger.info("=" * 70)
    logger.info(f"🚀 Debug Scrape at {scan_time} ({len(QUICK_PORTALS)} portals)")
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
            else:
                logger.info(f"  ⚪ {portal['name']}: 0 jobs")
        except Exception as e:
            logger.info(f"  ❌ {portal['name']}: {e}")
            import traceback
            traceback.print_exc()

    logger.info(f"\n📡 Raw jobs found: {len(all_jobs)} from {len(portal_stats)} active portals")

    if all_jobs:
        logger.info("\n📋 ALL JOBS:")
        for i, j in enumerate(all_jobs, 1):
            logger.info(f"  {i}. {j.get('title')} @ {j.get('company')}")
            logger.info(f"      Location: {j.get('location')[:50]}")
            logger.info(f"      Salary: {j.get('salary', 'N/A')[:30]}")
            logger.info(f"      Source: {j.get('source')}")
            logger.info(f"      URL: {j.get('url')[:80]}")
            logger.info("")

    duration = time.time() - scan_start
    logger.info(f"\n{'=' * 70}")
    logger.info(f"✅ Debug Scrape Complete in {duration:.1f}s")
    logger.info("=" * 70)
    sys.exit(0)

if __name__ == "__main__":
    run_test()