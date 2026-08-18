import os
import sys
import sqlite3
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv; load_dotenv('.env')

from config.settings import DB_PATH, PROJECT_ROOT
from engine.resume_optimizer import optimize_resume_for_jd
from engine.application_tracker import update_status
from engine.cold_emailer import generate_cold_email, send_cold_email
from config.settings import TARGET_EMAIL

def apply_to_top_jobs():
    print("🚀 Starting Auto-Apply sequence for top available jobs...")
    
    # 1. Ensure applications output directory exists
    apps_dir = os.path.join(PROJECT_ROOT, "applications")
    os.makedirs(apps_dir, exist_ok=True)
    
    # 2. Get jobs from DB
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Fetch jobs that are high matches and not yet marked as 'Applied'
    cursor.execute("""
        SELECT * FROM applications 
        WHERE match_score >= 80 AND status != 'Applied'
        ORDER BY match_score DESC 
        LIMIT 5
    """)
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No new high-match jobs found to apply to.")
        return
        
    print(f"Found {len(rows)} high-match jobs ready for application.\n")
    
    applied_jobs = []
    for row in rows:
        job = dict(row)
        title = job.get("title", "Unknown")
        company = job.get("company", "Unknown")
        job_id = job.get("id")
        
        print(f"🎯 Processing Application for: {title} @ {company}")
        
        # We need a JD for the optimizer. Since we don't have the full JD saved in DB currently, 
        # we will use the title and company to build a strong generic JD block for the optimizer
        mock_jd = f"Seeking a {title} with expertise in modern data engineering, BI, and cloud architecture at {company}. Must have strong SQL, data pipeline experience, and ability to work remotely."
        
        print("   ⏳ Generating tailored resume, cover letter, and pitch...")
        try:
            tailored = optimize_resume_for_jd(
                job_title=title,
                company=company,
                jd_text=mock_jd,
                country=job.get("region", "Global")
            )
            
            # Save files
            safe_company = "".join(x for x in company if x.isalnum() or x in " -_")
            job_dir = os.path.join(apps_dir, f"{safe_company}_{job_id[:8]}")
            os.makedirs(job_dir, exist_ok=True)
            
            with open(os.path.join(job_dir, "Tailored_Resume.md"), "w") as f:
                f.write(tailored.get("tailored_resume_markdown", "Error generating resume"))
                
            with open(os.path.join(job_dir, "Cover_Letter.md"), "w") as f:
                f.write(tailored.get("cover_letter_markdown", "Error generating cover letter"))
                
            print(f"   ✅ Saved tailored assets to: applications/{safe_company}_{job_id[:8]}/")
            
            # Prepare email pitch
            email_data = generate_cold_email({"title": title, "company": company, "location": job.get("location")})
            email_data["subject"] = f"[READY TO APPLY] {company} - {title}"
            email_data["body"] = (
                f"Your tailored resume and cover letter for {company} have been generated and saved locally.\n\n"
                f"Job URL: {job.get('url')}\n\n"
                f"--- Suggested Recruiter Pitch ---\n\n"
                f"{email_data['body']}\n\n"
                f"--- Tailored Cover Letter ---\n\n"
                f"{tailored.get('cover_letter_markdown', '')}\n\n"
                f"--- Tailored Resume ---\n\n"
                f"{tailored.get('tailored_resume_markdown', '')}"
            )
            
            print(f"   📧 Sending drafted application package to {TARGET_EMAIL}...")
            send_cold_email(email_data, to_address=TARGET_EMAIL)
            
            # Mark as applied in DB
            update_status(job_id, "Applied", "Auto-tailored and drafted")
            print("   ✅ Status updated to 'Applied'\n")
            
            applied_jobs.append({"title": title, "company": company, "url": job.get("url", "N/A")})
            
        except Exception as e:
            print(f"   ❌ Failed to process application: {e}\n")
            
    print("🎉 Auto-Apply sequence complete!")
    
    if applied_jobs:
        summary_lines = ["Here is the summary of jobs that were automatically applied to in this run:\n"]
        for i, aj in enumerate(applied_jobs, 1):
            summary_lines.append(f"{i}. {aj['title']} at {aj['company']}")
            summary_lines.append(f"   URL: {aj['url']}\n")
        
        summary_body = "\n".join(summary_lines)
        summary_email_data = {
            "subject": f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Auto-Apply Summary Report",
            "body": summary_body
        }
        print(f"📧 Sending summary report to {TARGET_EMAIL}...")
        send_cold_email(summary_email_data, to_address=TARGET_EMAIL)
        print("✅ Summary report sent!")

if __name__ == "__main__":
    apply_to_top_jobs()
