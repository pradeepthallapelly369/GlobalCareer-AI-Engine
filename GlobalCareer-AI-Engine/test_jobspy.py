"""Test JobSpy LinkedIn scraping for key countries."""
import os, sys, time, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("GlobalCareer")

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from config.portals import PORTALS
from engine.job_aggregator import scrape_jobspy_portal, _job_hash
from config.search_queries import COMPACT_QUERIES

# Target countries for LinkedIn JobSpy (from priority list in job_aggregator.py)
TARGET_COUNTRIES = ["US", "UK", "Germany", "Canada", "Australia", "Netherlands", "Singapore", "UAE"]

def run_test():
    scan_start = time.time()
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M IST")
    logger.info("=" * 70)
    logger.info(f"🔍 LinkedIn JobSpy Test at {scan_time}")
    logger.info("=" * 70)

    # Get LinkedIn portals for target countries
    linkedin_portals = [p for p in PORTALS if p["type"] == "JOBSPY" and p["site"] == "linkedin" and p.get("region") in TARGET_COUNTRIES]

    logger.info(f"Testing {len(linkedin_portals)} LinkedIn portals: {[p['name'] for p in linkedin_portals]}")

    all_jobs = []
    seen_hashes = set()
    portal_stats = {}

    for portal in linkedin_portals:
        logger.info(f"  🔍 Scraping {portal['name']} (queries: {COMPACT_QUERIES[:3]})...")
        try:
            jobs = scrape_jobspy_portal(portal, COMPACT_QUERIES[:3])
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
                logger.info(f"    ✅ {portal['name']}: {count} jobs")
            else:
                logger.info(f"    ⚪ {portal['name']}: 0 jobs")
        except Exception as e:
            logger.info(f"    ❌ {portal['name']}: {e}")

        time.sleep(2)  # Rate limit

    logger.info(f"\n📡 Total raw jobs: {len(all_jobs)} from {len(portal_stats)} portals")

    if all_jobs:
        logger.info("\n📋 FIRST 15 JOBS:")
        for i, j in enumerate(all_jobs[:15], 1):
            logger.info(f"  {i}. {j.get('title')} @ {j.get('company')}")
            logger.info(f"      Location: {j.get('location')[:50]}")
            logger.info(f"      Salary: {j.get('salary', 'N/A')[:30]}")
            logger.info(f"      Source: {j.get('source')}")
            logger.info(f"      URL: {j.get('url')[:80]}")
            logger.info("")

    duration = time.time() - scan_start
    logger.info(f"\n{'=' * 70}")
    logger.info(f"✅ JobSpy Test Complete in {duration:.1f}s")
    logger.info("=" * 70)
    sys.exit(0)

if __name__ == "__main__":
    run_test()