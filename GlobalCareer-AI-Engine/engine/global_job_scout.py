"""
Global Remote & Visa Sponsorship Job Scout Engine
Targets: Foreign Currency Pay (USD / EUR / GBP / AUD / CAD) and International Relocation / Visa Sponsorship
"""

import requests
import json
import re
from datetime import datetime

TARGET_KEYWORDS = [
    "qlik", "qlik sense", "databricks", "dbt", "data engineer", "bi engineer", "bi architect",
    "power bi", "analytics engineer", "sql", "data architect", "technical lead", "etl",
    "python", "fastapi", "ai engineer", "data warehouse"
]

def fetch_remotive_jobs():
    url = "https://remotive.com/api/remote-jobs?category=data"
    jobs = []
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("jobs", []):
                title = item.get("title", "")
                candidate_loc = item.get("candidate_required_location", "").lower()
                desc = item.get("description", "")
                
                # Check if job allows worldwide/remote anywhere or India
                is_anywhere = any(x in candidate_loc for x in ["worldwide", "anywhere", "remote", "india", "apac", "flexible", "global"]) or candidate_loc == ""
                
                full_text = f"{title} {desc}".lower()
                has_tech = any(kw in full_text for kw in TARGET_KEYWORDS)

                if is_anywhere and has_tech:
                    jobs.append({
                        "id": f"remotive_{item.get('id')}",
                        "title": title,
                        "company": item.get("company_name", "N/A"),
                        "location": item.get("candidate_required_location", "Worldwide Remote"),
                        "url": item.get("url", ""),
                        "category": item.get("category", "Data"),
                        "tags": item.get("tags", []),
                        "source": "Remotive",
                        "type": "Remote (USD/Worldwide)",
                        "date": item.get("publication_date", "")[:10]
                    })
    except Exception as e:
        print(f"[Scout Warning] Remotive fetch error: {e}")
    return jobs

def fetch_remoteok_jobs():
    url = "https://remoteok.com/api"
    jobs = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            for item in data:
                if not isinstance(item, dict):
                    continue
                title = item.get("position", "")
                company = item.get("company", "")
                location = item.get("location", "Worldwide")
                tags = item.get("tags", [])
                desc = item.get("description", "")

                full_text = f"{title} {' '.join(tags)} {desc}".lower()
                has_tech = any(kw in full_text for kw in TARGET_KEYWORDS)

                if has_tech and title:
                    jobs.append({
                        "id": f"remoteok_{item.get('id', hash(title))}",
                        "title": title,
                        "company": company,
                        "location": location if location else "Worldwide Remote",
                        "url": item.get("url", f"https://remoteok.com/remote-jobs/{item.get('id', '')}"),
                        "category": "Data & AI",
                        "tags": tags,
                        "source": "RemoteOK",
                        "type": "Remote (USD/Worldwide)",
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
    except Exception as e:
        print(f"[Scout Warning] RemoteOK fetch error: {e}")
    return jobs

def fetch_arbeitnow_visa_jobs():
    """Fetches EU/Germany jobs offering Visa Sponsorship or EU Relocation."""
    url = "https://www.arbeitnow.com/api/job-board-api"
    jobs = []
    try:
        resp = requests.get(url, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("data", []):
                title = item.get("title", "")
                company = item.get("company_name", "")
                location = item.get("location", "")
                desc = item.get("description", "")
                tags = item.get("tags", [])
                visa_sponsored = item.get("visa_sponsorship", False) or "visa" in f"{title} {desc}".lower()

                full_text = f"{title} {' '.join(tags)} {desc}".lower()
                has_tech = any(kw in full_text for kw in TARGET_KEYWORDS)

                if has_tech and (visa_sponsored or "remote" in location.lower()):
                    jobs.append({
                        "id": f"arbeitnow_{item.get('slug')}",
                        "title": title,
                        "company": company,
                        "location": f"{location} (Visa Sponsorship / EU Remote)" if visa_sponsored else location,
                        "url": item.get("url", ""),
                        "category": "Data Engineering & AI",
                        "tags": tags,
                        "source": "Arbeitnow (EU)",
                        "type": "Visa Sponsorship / EUR Pay" if visa_sponsored else "EU Remote",
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
    except Exception as e:
        print(f"[Scout Warning] Arbeitnow fetch error: {e}")
    return jobs

def calculate_match_score(job):
    title = job.get("title", "").lower()
    tags = " ".join(job.get("tags", [])).lower()
    full = f"{title} {tags}"

    score = 70  # Baseline
    if "qlik" in full:
        score += 15
    if "databricks" in full or "dbt" in full:
        score += 15
    if "python" in full or "fastapi" in full:
        score += 10
    if "lead" in title or "architect" in title or "senior" in title:
        score += 5

    return min(score, 98)

def scout_all_global_jobs():
    """Scouts jobs across Remotive, RemoteOK, and Arbeitnow Visa portals."""
    print("[Global Job Scout] Hunting for Remote USD/EUR/GBP & Visa Sponsorship roles...")
    remotive = fetch_remotive_jobs()
    remoteok = fetch_remoteok_jobs()
    arbeitnow = fetch_arbeitnow_visa_jobs()

    all_jobs = remotive + remoteok + arbeitnow

    # Calculate match score & sort
    for job in all_jobs:
        job["match_score"] = calculate_match_score(job)

    # Sort by match score descending
    all_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    print(f"[Global Job Scout] Found {len(all_jobs)} high-relevancy global opportunities!")
    return all_jobs
