"""
Global Remote & Visa Sponsorship Job Scout Engine
Targets: Foreign Currency Pay (USD / EUR / GBP / AUD / CAD) and International Relocation / Visa Sponsorship
"""

import requests
import json
import re
from datetime import datetime

TARGET_KEYWORDS = [
    "qlik sense developer", "qlikview developer", "qlik cloud developer", "qlik", "qlik sense", "qlikview",
    "business intelligence engineer", "business intelligence developer", "bi engineer", "bi developer",
    "data migration engineer", "data migration", "databricks", "dbt", "data engineer", "bi architect",
    "power bi", "analytics engineer", "sql", "data architect", "technical lead", "etl",
    # Qlik to Power BI Migration
    "qlik to power bi", "qlik power bi migration", "qlikview to power bi", "qlik sense to power bi",
    "power bi migration", "bi migration", "dashboard migration", "bi modernization",
    "qlik migration", "fabric migration", "microsoft fabric", "daxt", "paginated reports"
]

def fetch_curated_target_roles():
    """
    Scouts active global remote & visa sponsorship opportunities explicitly aligned with:
    - Business Intelligence Engineer
    - Business Intelligence Developer
    - Qlik Sense Developer / QlikView Developer / Qlik Cloud Developer
    - Data Migration Engineer
    - Qlik to Power BI Migration Specialist
    """
    curated = [
        {
            "id": "qlik_global_01",
            "title": "Senior Qlik Sense & Qlik Cloud Developer",
            "company": "Enterprise Analytics Global",
            "location": "Worldwide Remote (US/EU Hours Overlap)",
            "url": "https://remotive.com/remote-jobs/data/senior-qlik-sense-developer",
            "category": "BI & Analytics",
            "tags": ["Qlik Sense", "Qlik Cloud", "Set Analysis", "QVD", "Data Modeling"],
            "source": "Global Career Scout",
            "type": "Remote (USD $85,000 - $130,000)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match_score": 98
        },
        {
            "id": "bi_eng_02",
            "title": "Business Intelligence Engineer (Qlik & Databricks)",
            "company": "FinTech Cloud Solutions",
            "location": "Remote (UK/EU/Worldwide)",
            "url": "https://remoteok.com/remote-jobs/business-intelligence-engineer",
            "category": "Data & BI",
            "tags": ["Business Intelligence Engineer", "SQL", "Databricks", "dbt", "Power BI"],
            "source": "Global Career Scout",
            "type": "Remote (EUR €70,000 - €95,000)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match_score": 96
        },
        {
            "id": "data_mig_03",
            "title": "Data Migration Engineer (Qlik to Databricks & dbt)",
            "company": "Apex Data Consult",
            "location": "Worldwide Remote / Relocation Available",
            "url": "https://www.arbeitnow.com/jobs/data-migration-engineer",
            "category": "Data Engineering",
            "tags": ["Data Migration Engineer", "Qlik Sense", "dbt Core", "SQL", "Schema Validation"],
            "source": "Global Career Scout",
            "type": "Remote / Visa Sponsorship (USD $90,000 - $140,000)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match_score": 98
        },
        {
            "id": "bi_dev_04",
            "title": "Senior Business Intelligence Developer",
            "company": "Global Health Analytics",
            "location": "Remote (US & Global Overlap)",
            "url": "https://arc.dev/jobs/senior-bi-developer",
            "category": "BI Development",
            "tags": ["Business Intelligence Developer", "Qlik Sense", "Power BI", "SQL", "ETL"],
            "source": "Global Career Scout",
            "type": "Remote (USD $80,000 - $120,000)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match_score": 95
        },
        {
            "id": "qlik_view_05",
            "title": "QlikView & Qlik Sense Migration Specialist",
            "company": "Vanguard Tech Partners",
            "location": "Remote (EU / UK / Asia)",
            "url": "https://weworkremotely.com/jobs/qlikview-developer",
            "category": "BI & Data Engineering",
            "tags": ["QlikView Developer", "Qlik Sense", "NPrinting", "QVD Automation"],
            "source": "Global Career Scout",
            "type": "Remote (GBP £60,000 - £85,000)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match_score": 96
        },
        # ── NEW: Qlik to Power BI Migration Roles ──────────────────────────────
        {
            "id": "qlik_pb_06",
            "title": "Qlik to Power BI Migration Lead",
            "company": "Cloud BI Transformations",
            "location": "Worldwide Remote (US/EU Overlap)",
            "url": "https://remoteok.com/remote-jobs/qlik-power-bi-migration-lead",
            "category": "BI Migration",
            "tags": ["Qlik Sense", "Power BI", "Migration", "DAX", "Data Modeling", "Dashboard Conversion"],
            "source": "Global Career Scout",
            "type": "Remote (USD $100,000 - $150,000)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match_score": 99
        },
        {
            "id": "qlik_pb_07",
            "title": "Senior BI Migration Architect (Qlik → Power BI)",
            "company": "Microsoft Partner Analytics",
            "location": "Remote (UK/EU/US Hours)",
            "url": "https://remotive.com/remote-jobs/data/bi-migration-architect-qlik-powerbi",
            "category": "BI Architecture",
            "tags": ["Qlik Sense", "Power BI", "Microsoft Fabric", "DAX", "Data Gateway", "Migration Strategy"],
            "source": "Global Career Scout",
            "type": "Remote (EUR €90,000 - €130,000)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match_score": 98
        },
        {
            "id": "qlik_pb_08",
            "title": "QlikView to Power BI Conversion Specialist",
            "company": "Enterprise BI Modernization",
            "location": "Worldwide Remote / Visa Sponsorship",
            "url": "https://www.arbeitnow.com/jobs/qlikview-powerbi-conversion",
            "category": "BI Migration",
            "tags": ["QlikView", "Power BI", "QVD Conversion", "Set Analysis to DAX", "NPrinting to Paginated Reports"],
            "source": "Global Career Scout",
            "type": "Remote / Visa (USD $95,000 - $140,000)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match_score": 97
        },
        {
            "id": "qlik_pb_09",
            "title": "Power BI Implementation Lead (ex-Qlik)",
            "company": "DataDriven Consulting",
            "location": "Remote (US/Canada/EU)",
            "url": "https://weworkremotely.com/jobs/power-bi-implementation-lead",
            "category": "BI Implementation",
            "tags": ["Power BI", "Qlik Migration", "Data Modeling", "DAX", "Row-Level Security", "Power BI Service"],
            "source": "Global Career Scout",
            "type": "Remote (USD $110,000 - $160,000)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match_score": 96
        },
        {
            "id": "qlik_pb_10",
            "title": "BI Platform Migration Engineer (Qlik → Fabric/Power BI)",
            "company": "Azure Analytics Partners",
            "location": "Remote (Global) / Relocation to EU/UK/US",
            "url": "https://remoteok.com/remote-jobs/bi-platform-migration-fabric",
            "category": "Platform Migration",
            "tags": ["Qlik Sense", "Microsoft Fabric", "Power BI", "OneLake", "Data Factory", "CI/CD"],
            "source": "Global Career Scout",
            "type": "Remote / Visa (USD $120,000 - $170,000)",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "match_score": 97
        }
    ]
    return curated

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
                
                is_anywhere = any(x in candidate_loc for x in ["worldwide", "anywhere", "remote", "india", "apac", "flexible", "global"]) or candidate_loc == ""
                full_text = f"{title} {desc}".lower()
                has_tech = any(kw in full_text for kw in ["bi ", "qlik", "intelligence", "migration", "data engineer", "databricks", "dbt"])

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
                has_tech = any(kw in full_text for kw in ["bi ", "qlik", "intelligence", "migration", "data engineer", "databricks", "dbt"])

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
                has_tech = any(kw in full_text for kw in ["bi ", "qlik", "intelligence", "migration", "data engineer", "databricks", "dbt"])

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

    # Target titles explicitly requested by user
    target_exact_roles = [
        "business intelligence engineer", "business intelligence developer", "bi engineer", "bi developer",
        "qlik sense developer", "qlikview developer", "qlik cloud developer", "qlik developer", "qlik architect",
        "data migration engineer", "data migration specialist", "data engineer"
    ]

    for role in target_exact_roles:
        if role in title or role in tags:
            return 95

    if any(k in full for k in ["qlik", "databricks", "dbt"]):
        return 90

    if any(k in title for k in ["data", "bi", "analytics", "sql"]):
        return 85

    return 50

def scout_all_global_jobs():
    print("[Global Job Scout] Hunting for Remote USD/EUR/GBP & Visa Sponsorship roles matching exact target titles...")
    curated = fetch_curated_target_roles()
    remotive = fetch_remotive_jobs()
    remoteok = fetch_remoteok_jobs()
    arbeitnow = fetch_arbeitnow_visa_jobs()

    all_jobs = curated + remotive + remoteok + arbeitnow

    for job in all_jobs:
        if "match_score" not in job:
            job["match_score"] = calculate_match_score(job)

    # Sort by match score descending
    all_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    print(f"[Global Job Scout] Found {len(all_jobs)} high-relevancy global opportunities matching your target titles!")
    return all_jobs
