"""Minimal test — just scrape and print raw jobs from fast portals."""
import os, sys, time, logging
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("GlobalCareer")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from config.portals import PORTALS
from engine.job_aggregator import _scrape_single_portal, _job_hash

# Only fast API/RSS portals — skip all JOBSPY
QUICK_PORTALS = [p for p in PORTALS if p["type"] in ("API", "RSS")]

def run_test():
    scan_start = time.time()
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M IST")
    logger.info("=" * 70)
    logger.info(f"🚀 Test Scrape Starting at {scan_time} ({len(QUICK_PORTALS)} fast portals)")
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

    if all_jobs:
        logger.info("\n📋 ALL RAW JOBS (first 30):")
        for i, j in enumerate(all_jobs[:30], 1):
            loc = j.get('location', 'N/A')[:50]
            sal = j.get('salary', 'N/A')[:30]
            logger.info(f"  {i}. {j.get('title')} @ {j.get('company')}")
            logger.info(f"      Location: {loc} | Salary: {sal} | Source: {j.get('source')}")
            logger.info(f"      URL: {j.get('url')[:80]}")
            logger.info(f"      Desc: {j.get('description', '')[:150]}...")
            logger.info("")

    duration = time.time() - scan_start
    logger.info(f"\n{'=' * 70}")
    logger.info(f"✅ Test Scrape Complete in {duration:.1f}s")
    logger.info("=" * 70)

if __name__ == "__main__":
    run_test()