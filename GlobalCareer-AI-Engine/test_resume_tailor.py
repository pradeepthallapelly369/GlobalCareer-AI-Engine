"""Test resume tailoring for top job match."""
import os, sys, json
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from engine.resume_optimizer import optimize_resume_for_jd

# Top job match
job = {
    "title": "Data Migration Engineer (Qlik to Databricks & dbt)",
    "company": "Apex Data Consult",
    "location": "Worldwide Remote / Relocation Available",
    "url": "https://www.arbeitnow.com/jobs/data-migration-engineer",
    "description": """We are looking for a Senior Data Migration Engineer to lead our Qlik Sense to Databricks migration initiative.

Key Responsibilities:
- Lead end-to-end migration of Qlik Sense load scripts and data models to Databricks SQL and dbt Core
- Design and implement modular dbt models following staging/intermediate/marts architecture
- Build data reconciliation frameworks to ensure 100% data fidelity between legacy and target systems
- Collaborate with stakeholders to define validation criteria and acceptance testing
- Optimize SQL queries and dbt models for performance on Databricks
- Document migration patterns and create reusable templates for future migrations

Required Skills:
- 5+ years experience with Qlik Sense (scripting, data modeling, Set Analysis, QVD creation)
- Strong expertise with Databricks SQL, Delta Lake, and dbt Core
- Deep SQL knowledge (window functions, CTEs, performance tuning)
- Experience with Python, PySpark for data validation
- Data reconciliation and migration methodologies
- Excellent communication for stakeholder management

Preferred:
- Qlik Sense Data Architect certification
- Databricks certification
- Experience with AI-assisted data reconciliation
- Remote work experience with US/EU time zone overlap

Compensation: $90,000 - $140,000 USD (based on experience)
Location: Worldwide Remote / Visa Sponsorship available for EU relocation
Employment Type: Full-time / Contract""",
    "type": "Remote / Visa Sponsorship (USD $90,000 - $140,000)",
    "source": "Global Career Scout",
    "match_score": 100
}

def run_test():
    print("=" * 70)
    print(f"🎯 Testing Resume Tailoring for: {job['title']} @ {job['company']}")
    print("=" * 70)

    result = optimize_resume_for_jd(
        job_title=job["title"],
        company=job["company"],
        jd_text=job["description"],
        country="GLOBAL_REMOTE"
    )

    print(f"\n✅ Status: {result['status']}")
    print(f"Match Score: {result.get('match_score', 'N/A')}")
    print(f"ATS Keywords: {result.get('ats_keywords', [])}")
    print(f"Country: {result.get('country', 'N/A')}")

    # Save outputs
    os.makedirs("data/tailored", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save tailored resume
    resume_path = f"data/tailored/resume_{job['title'].replace(' ', '_').replace('/', '_')}_{timestamp}.md"
    with open(resume_path, "w") as f:
        f.write(result.get("tailored_resume_markdown", ""))
    print(f"\n📄 Tailored Resume saved to: {resume_path}")

    # Save cover letter
    cl_path = f"data/tailored/cover_letter_{job['title'].replace(' ', '_').replace('/', '_')}_{timestamp}.md"
    with open(cl_path, "w") as f:
        f.write(result.get("cover_letter_markdown", ""))
    print(f"📄 Cover Letter saved to: {cl_path}")

    # Save recruiter email
    email_path = f"data/tailored/recruiter_email_{job['title'].replace(' ', '_').replace('/', '_')}_{timestamp}.md"
    with open(email_path, "w") as f:
        f.write(result.get("recruiter_email_pitch", ""))
    print(f"📄 Recruiter Email saved to: {email_path}")

    # Print preview
    print("\n" + "=" * 70)
    print("📋 TAILORED RESUME PREVIEW (first 100 lines):")
    print("=" * 70)
    resume_lines = result.get("tailored_resume_markdown", "").split("\n")
    for line in resume_lines[:100]:
        print(line)
    if len(resume_lines) > 100:
        print(f"... ({len(resume_lines) - 100} more lines)")

    print("\n" + "=" * 70)
    print("📧 RECRUITER EMAIL PREVIEW:")
    print("=" * 70)
    print(result.get("recruiter_email_pitch", "")[:1500])

    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)

if __name__ == "__main__":
    run_test()