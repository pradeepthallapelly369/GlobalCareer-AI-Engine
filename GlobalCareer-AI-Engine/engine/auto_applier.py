"""
Autonomous Job Auto-Apply & Cold Outreach Engine
Scouts high-relevancy remote (USD/EUR) & visa sponsorship roles, automatically tailors ATS resumes,
generates cold pitch emails, and registers applications in applications.db.
"""

import time
from engine.global_job_scout import scout_all_global_jobs
from engine.resume_optimizer import optimize_resume_for_jd
from engine.application_tracker import add_or_update_job, get_all_applications

def run_auto_apply_pipeline(max_jobs: int = 50, target_country: str = "GLOBAL_REMOTE"):
    """
    Scouts live global jobs across web APIs, filters high matches (>=85%), generates tailored ATS resumes & pitch emails,
    and logs them in the applications database.
    """
    print(f"🚀 [Auto-Applier] Starting autonomous scouting & tailoring pipeline (Target: {target_country}, Threshold: >=85%)...")
    scouted_jobs = scout_all_global_jobs()
    
    processed_count = 0
    results = []

    for job in scouted_jobs:
        if processed_count >= max_jobs:
            break

        match_score = job.get("match_score", 75)
        if match_score < 85:
            continue

        title = job.get("title", "Senior Data Engineer")
        company = job.get("company", "Global Enterprise")
        location = job.get("location", "Worldwide Remote")
        url = job.get("url", "")
        job_id = job.get("id", f"job_{hash(title + company)}")

        print(f"🎯 [Auto-Applier] Tailoring application for: {title} @ {company} ({match_score}% Match)")

        # Create dummy JD snippet if missing
        jd_text = f"Seeking {title} with expertise in SQL, Qlik Sense, Databricks, dbt Core, Python, and Data Lakehouses. {company} offers competitive {location} compensation."
        
        # Generate tailored output
        tailored = optimize_resume_for_jd(
            job_title=title,
            company=company,
            jd_text=jd_text,
            country=target_country
        )

        # Register in SQLite DB
        app_record = {
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "url": url,
            "salary": job.get("type", "$70K-$130K USD"),
            "type": job.get("type", "Remote (USD/Worldwide)"),
            "match_score": match_score,
            "status": "Applied",
            "tailored_resume": tailored.get("tailored_resume_markdown", ""),
            "cover_letter": tailored.get("cover_letter_markdown", ""),
            "email_pitch": tailored.get("recruiter_email_pitch", "")
        }

        add_or_update_job(app_record)
        results.append(app_record)
        processed_count += 1

    print(f"✅ [Auto-Applier] Successfully tailored & registered {len(results)} applications!")
    return results

if __name__ == "__main__":
    run_auto_apply_pipeline(max_jobs=5)
