"""
Job Aggregator — Scrapes ALL portals, deduplicates, and returns unified job list.
Handles API portals, RSS feeds, and JobSpy (LinkedIn/Indeed/Glassdoor).
"""

import requests
import feedparser
import hashlib
import time
import logging
import traceback
from datetime import datetime, timedelta
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

from config.settings import HOURS_OLD_THRESHOLD, JOBSPY_RESULTS_PER_QUERY, REJECT_KEYWORDS
from config.portals import PORTALS
from config.search_queries import COMPACT_QUERIES, ALL_SEARCH_QUERIES, CORE_SKILLS_KEYWORDS

logger = logging.getLogger("GlobalCareer")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def _job_hash(title, company, url=""):
    """Generate a unique hash for deduplication."""
    raw = f"{title.lower().strip()}|{company.lower().strip()}|{url.strip()}"
    return hashlib.md5(raw.encode()).hexdigest()

def _matches_skills(text):
    """Check if text contains any relevant skill keywords."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in CORE_SKILLS_KEYWORDS)

def _is_rejected(text):
    """Check if text contains INR-only / India-onsite markers."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in REJECT_KEYWORDS)

# ══════════════════════════════════════════════════════════════════════════════
# API SCRAPERS
# ══════════════════════════════════════════════════════════════════════════════

def scrape_remotive(portal):
    """Remotive API — remote tech jobs."""
    jobs = []
    try:
        for category in ["data", "software-dev", "all-others"]:
            url = f"{portal['url']}?category={category}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                continue
            data = resp.json()
            cutoff = datetime.now() - timedelta(hours=HOURS_OLD_THRESHOLD)
            for item in data.get("jobs", []):
                title = item.get("title", "")
                desc = item.get("description", "")
                full_text = f"{title} {desc}"
                if not _matches_skills(full_text):
                    continue
                if _is_rejected(full_text):
                    continue
                pub_str = item.get("publication_date", "")
                if pub_str:
                    try:
                        pub_date = datetime.strptime(pub_str[:19], "%Y-%m-%dT%H:%M:%S")
                        if pub_date < cutoff:
                            continue
                    except Exception:
                        pass
                loc = item.get("candidate_required_location", "Worldwide Remote")
                jobs.append({
                    "title": title,
                    "company": item.get("company_name", "N/A"),
                    "location": loc if loc else "Worldwide Remote",
                    "url": item.get("url", ""),
                    "description": desc[:2000],
                    "salary": item.get("salary", ""),
                    "source": f"Remotive",
                    "region": portal.get("region", "Global"),
                    "date": pub_str[:10] if pub_str else datetime.now().strftime("%Y-%m-%d"),
                    "tags": item.get("tags", []),
                })
    except Exception as e:
        logger.warning(f"[Remotive] Error: {e}")
    return jobs

def scrape_remoteok(portal):
    """RemoteOK API — remote jobs."""
    jobs = []
    try:
        resp = requests.get(portal["url"], headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return jobs
        data = resp.json()
        for item in data:
            if not isinstance(item, dict):
                continue
            title = item.get("position", "")
            company = item.get("company", "")
            tags = item.get("tags", [])
            desc = item.get("description", "")
            full_text = f"{title} {' '.join(tags)} {desc}"
            if not _matches_skills(full_text):
                continue
            if _is_rejected(full_text):
                continue
            if title:
                salary = item.get("salary_min", "")
                sal_str = ""
                if salary:
                    sal_max = item.get("salary_max", "")
                    sal_str = f"${salary}" + (f" - ${sal_max}" if sal_max else "")
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": item.get("location", "Worldwide Remote"),
                    "url": item.get("url", f"https://remoteok.com/remote-jobs/{item.get('id', '')}"),
                    "description": desc[:2000],
                    "salary": sal_str,
                    "source": "RemoteOK",
                    "region": portal.get("region", "Global"),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "tags": tags,
                })
    except Exception as e:
        logger.warning(f"[RemoteOK] Error: {e}")
    return jobs

def scrape_arbeitnow(portal):
    """Arbeitnow API — EU visa sponsorship jobs."""
    jobs = []
    try:
        resp = requests.get(portal["url"], headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return jobs
        data = resp.json()
        for item in data.get("data", []):
            title = item.get("title", "")
            desc = item.get("description", "")
            tags = item.get("tags", [])
            full_text = f"{title} {' '.join(tags)} {desc}"
            if not _matches_skills(full_text):
                continue
            if _is_rejected(full_text):
                continue
            visa = item.get("visa_sponsorship", False) or "visa" in full_text.lower()
            remote = "remote" in item.get("location", "").lower() or item.get("remote", False)
            if visa or remote:
                jobs.append({
                    "title": title,
                    "company": item.get("company_name", "N/A"),
                    "location": item.get("location", "EU"),
                    "url": item.get("url", ""),
                    "description": desc[:2000],
                    "salary": "",
                    "source": f"Arbeitnow ({'Visa' if visa else 'Remote'})",
                    "region": portal.get("region", "EU"),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "tags": tags,
                    "visa_sponsorship": visa,
                })
    except Exception as e:
        logger.warning(f"[Arbeitnow] Error: {e}")
    return jobs

def scrape_himalayas(portal):
    """Himalayas API — remote jobs."""
    jobs = []
    try:
        for offset in [0, 50]:
            url = f"{portal['url']}?limit=50&offset={offset}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                continue
            data = resp.json()
            for item in data.get("jobs", []):
                title = item.get("title", "")
                desc = item.get("description", "")
                full_text = f"{title} {desc}"
                if not _matches_skills(full_text):
                    continue
                if _is_rejected(full_text):
                    continue
                jobs.append({
                    "title": title,
                    "company": item.get("companyName", "N/A"),
                    "location": "Remote",
                    "url": item.get("applicationLink", item.get("url", "")),
                    "description": desc[:2000],
                    "salary": item.get("salaryCurrency", "") + " " + str(item.get("minSalary", "")) if item.get("minSalary") else "",
                    "source": "Himalayas",
                    "region": "Global",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "tags": item.get("categories", []),
                })
    except Exception as e:
        logger.warning(f"[Himalayas] Error: {e}")
    return jobs

def scrape_jobicy(portal):
    """Jobicy API — remote jobs."""
    jobs = []
    try:
        url = f"{portal['url']}?count=50&tag=data+engineer,qlik,business+intelligence,databricks,dbt"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return jobs
        data = resp.json()
        for item in data.get("jobs", []):
            title = item.get("jobTitle", "")
            desc = item.get("jobDescription", "")
            full_text = f"{title} {desc}"
            if not _matches_skills(full_text):
                continue
            jobs.append({
                "title": title,
                "company": item.get("companyName", "N/A"),
                "location": item.get("jobGeo", "Remote"),
                "url": item.get("url", ""),
                "description": desc[:2000],
                "salary": "",
                "source": "Jobicy",
                "region": "Global",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "tags": [],
            })
    except Exception as e:
        logger.warning(f"[Jobicy] Error: {e}")
    return jobs

def scrape_generic_api(portal):
    """Generic API scraper for other API portals."""
    jobs = []
    try:
        resp = requests.get(portal["url"], headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return jobs
        data = resp.json()
        items = data if isinstance(data, list) else data.get("jobs", data.get("data", data.get("results", [])))
        if not isinstance(items, list):
            return jobs
        for item in items[:100]:
            if not isinstance(item, dict):
                continue
            title = item.get("title", item.get("position", item.get("jobTitle", "")))
            desc = item.get("description", item.get("jobDescription", ""))
            full_text = f"{title} {desc}"
            if not _matches_skills(full_text):
                continue
            if _is_rejected(full_text):
                continue
            company = item.get("company", item.get("company_name", item.get("companyName", "N/A")))
            url_val = item.get("url", item.get("link", item.get("applicationLink", "")))
            jobs.append({
                "title": title,
                "company": company,
                "location": item.get("location", item.get("jobGeo", "Remote")),
                "url": url_val,
                "description": desc[:2000],
                "salary": item.get("salary", ""),
                "source": portal["name"],
                "region": portal.get("region", "Global"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "tags": item.get("tags", []),
            })
    except Exception as e:
        logger.debug(f"[{portal['name']}] API Error: {e}")
    return jobs

# ══════════════════════════════════════════════════════════════════════════════
# RSS SCRAPERS
# ══════════════════════════════════════════════════════════════════════════════

def scrape_rss_portal(portal, query=""):
    """Generic RSS feed scraper."""
    jobs = []
    try:
        url = portal["url"]
        if "{query}" in url and query:
            url = url.replace("{query}", quote(query))
        elif "{query}" in url:
            url = url.replace("{query}", quote("data engineer"))

        feed = feedparser.parse(url)
        for entry in feed.entries[:30]:
            title = getattr(entry, "title", "")
            desc = getattr(entry, "summary", getattr(entry, "description", ""))
            full_text = f"{title} {desc}"
            if not _matches_skills(full_text):
                continue
            if _is_rejected(full_text):
                continue
            jobs.append({
                "title": title,
                "company": getattr(entry, "author", portal["name"]),
                "location": portal.get("region", "Remote"),
                "url": getattr(entry, "link", "#"),
                "description": desc[:2000],
                "salary": "",
                "source": portal["name"],
                "region": portal.get("region", "Global"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "tags": [],
            })
    except Exception as e:
        logger.debug(f"[{portal['name']}] RSS Error: {e}")
    return jobs

# ══════════════════════════════════════════════════════════════════════════════
# JOBSPY SCRAPERS (LinkedIn, Indeed, Glassdoor, ZipRecruiter)
# ══════════════════════════════════════════════════════════════════════════════

def scrape_jobspy_portal(portal, queries=None):
    """Scrape via JobSpy library (LinkedIn, Indeed, Glassdoor)."""
    jobs = []
    if queries is None:
        queries = COMPACT_QUERIES[:6]
    try:
        from jobspy import scrape_jobs
    except ImportError:
        logger.warning("[JobSpy] jobspy not installed. Skipping.")
        return jobs

    site = portal.get("site", "linkedin")
    country = portal.get("country_linkedin", "usa")
    region = portal.get("region", "Global")

    for query in queries:
        try:
            kwargs = {
                "site_name": [site],
                "search_term": query,
                "location": "Remote",
                "results_wanted": JOBSPY_RESULTS_PER_QUERY,
                "hours_old": HOURS_OLD_THRESHOLD,
            }
            if site == "linkedin":
                kwargs["country_linkedin"] = country
                kwargs["linkedin_fetch_description"] = True

            results = scrape_jobs(**kwargs)
            if results is not None and not results.empty:
                results = results.fillna("")
                for _, row in results.iterrows():
                    title = str(row.get("title", ""))
                    desc = str(row.get("description", ""))
                    full_text = f"{title} {desc}"
                    if _is_rejected(full_text):
                        continue
                    url_val = str(row.get("job_url", row.get("link", "")))
                    salary = str(row.get("min_amount", ""))
                    if salary and salary != "":
                        max_sal = str(row.get("max_amount", ""))
                        currency = str(row.get("currency", "USD"))
                        salary = f"{currency} {salary}" + (f" - {max_sal}" if max_sal else "")
                    jobs.append({
                        "title": title,
                        "company": str(row.get("company", "N/A")),
                        "location": str(row.get("location", "Remote")),
                        "url": url_val,
                        "description": desc[:2000],
                        "salary": salary,
                        "source": f"JobSpy-{site.title()} ({region})",
                        "region": region,
                        "date": str(row.get("date_posted", datetime.now().strftime("%Y-%m-%d"))),
                        "tags": [],
                    })
            time.sleep(2)  # Rate limiting between queries
        except Exception as e:
            logger.debug(f"[JobSpy-{site}] Query '{query}' error: {e}")
            time.sleep(3)
    return jobs

# ══════════════════════════════════════════════════════════════════════════════
# MAIN AGGREGATOR
# ══════════════════════════════════════════════════════════════════════════════

def _scrape_single_portal(portal):
    """Dispatch to the right scraper based on portal type."""
    portal_name = portal["name"]
    portal_type = portal["type"]
    try:
        if portal_type == "JOBSPY":
            return scrape_jobspy_portal(portal, COMPACT_QUERIES[:4])
        elif portal_type == "RSS":
            all_jobs = []
            for q in COMPACT_QUERIES[:3]:
                all_jobs.extend(scrape_rss_portal(portal, q))
            return all_jobs
        elif portal_type == "API":
            # Dispatch to specialized API scrapers
            if "remotive" in portal_name.lower():
                return scrape_remotive(portal)
            elif "remoteok" in portal_name.lower():
                return scrape_remoteok(portal)
            elif "arbeitnow" in portal_name.lower():
                return scrape_arbeitnow(portal)
            elif "himalayas" in portal_name.lower():
                return scrape_himalayas(portal)
            elif "jobicy" in portal_name.lower():
                return scrape_jobicy(portal)
            else:
                return scrape_generic_api(portal)
        else:
            return scrape_generic_api(portal)
    except Exception as e:
        logger.debug(f"[{portal_name}] Scraper failed: {e}")
        return []

def aggregate_all_jobs(max_workers=10):
    """
    Master aggregation function. Scrapes ALL portals in parallel,
    deduplicates, and returns a unified job list.
    """
    logger.info(f"🌍 Starting global job scan across {len(PORTALS)} portals...")
    all_jobs = []
    seen_hashes = set()
    portal_stats = {}
    errors = []

    # Separate JOBSPY portals (rate-limited, run sequentially in smaller batches)
    jobspy_portals = [p for p in PORTALS if p["type"] == "JOBSPY"]
    other_portals = [p for p in PORTALS if p["type"] != "JOBSPY"]

    # Scrape non-JOBSPY portals in parallel
    logger.info(f"  📡 Scraping {len(other_portals)} API/RSS portals in parallel...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_scrape_single_portal, p): p for p in other_portals}
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
                    logger.info(f"    ✅ {portal['name']}: {count} jobs")
            except Exception as e:
                errors.append(f"{portal['name']}: {e}")

    # Scrape JOBSPY portals (sequentially to avoid bans, limit to top countries)
    priority_jobspy = [p for p in jobspy_portals if p.get("region") in [
        "US", "UK", "Germany", "Canada", "Australia", "Netherlands",
        "Singapore", "UAE", "Ireland", "Sweden", "Switzerland", "Global"
    ]]
    logger.info(f"  🔍 Scraping {len(priority_jobspy)} priority JobSpy portals...")
    for portal in priority_jobspy[:20]:  # Limit to top 20 to avoid rate limits
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
            time.sleep(3)  # Rate limit between portals
        except Exception as e:
            errors.append(f"{portal['name']}: {e}")

    logger.info(f"🎯 Scan complete! {len(all_jobs)} unique jobs from {len(portal_stats)} active portals")
    if errors:
        logger.debug(f"  ⚠️ {len(errors)} portal errors (non-critical)")

    return all_jobs, portal_stats
