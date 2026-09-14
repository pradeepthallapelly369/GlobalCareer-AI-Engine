"""Test resume tailoring for second job match."""
import os, sys, json
from datetime import datetime

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from engine.resume_optimizer import optimize_resume_for_jd

# Second job match
job = {
    "title": "Senior Qlik Sense & Qlik Cloud Developer",
    "company": "Enterprise Analytics Global",
    "location": "Worldwide Remote (US/EU Hours Overlap)",
    "url": "https://remotive.com/remote-jobs/data/senior-qlik-sense-developer",
    "description": """We are seeking a Senior Qlik Sense & Qlik Cloud Developer to join our global analytics team.

Key Responsibilities:
- Design, develop, and maintain enterprise Qlik Sense applications and dashboards
- Build and optimize Qlik Sense data models using star schema, QVD layering, and incremental loads
- Implement advanced Set Analysis expressions and complex chart calculations
- Migrate and modernize legacy QlikView applications to Qlik Sense Cloud
- Collaborate with business stakeholders to gather requirements and translate into BI solutions
- Implement Qlik NPrinting for automated report distribution
- Performance tuning and optimization of Qlik applications
- Establish governance, security rules, and best practices for Qlik Sense environment

Required Skills:
- 5+ years hands-on Qlik Sense development (Desktop and Cloud)
- Expert in Qlik Sense scripting, data modeling, Set Analysis, QVD creation
- Qlik Sense Cloud deployment and management experience
- NPrinting report development and scheduling
- QlikView to Qlik Sense migration experience
- Strong SQL skills (window functions, CTEs, performance tuning)
- Data warehousing concepts (star schema, snowflake, fact/dimension tables)
- Agile/Scrum delivery experience

Preferred:
- Qlik Sense Data Architect / Business Analyst certifications
- Experience with Qlik Cloud automation and APIs
- Python/PySpark for data validation
- Remote work experience with US/EU time zone overlap

Compensation: $85,000 - $130,000 USD (based on experience)
Location: Worldwide Remote (must overlap US/EU business hours)
Employment Type: Full-time / Contract""",
    "type": "Remote (USD $85,000 - $130,000)",
    "source": "Global Career Scout",
    "match_score": 80
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

    safe_title = job['title'].replace(' ', '_').replace('/', '_').replace('&', 'and')

    # Save tailored resume
    resume_path = f"data/tailored/resume_{safe_title}_{timestamp}.md"
    with open(resume_path, "w") as f:
        f.write(result.get("tailored_resume_markdown", ""))
    print(f"\n📄 Tailored Resume saved to: {resume_path}")

    # Save cover letter
    cl_path = f"data/tailored/cover_letter_{safe_title}_{timestamp}.md"
    with open(cl_path, "w") as f:
        f.write(result.get("cover_letter_markdown", ""))
    print(f"📄 Cover Letter saved to: {cl_path}")

    # Save recruiter email
    email_path = f"data/tailored/recruiter_email_{safe_title}_{timestamp}.md"
    with open(email_path, "w") as f:
        f.write(result.get("recruiter_email_pitch", ""))
    print(f"📄 Recruiter Email saved to: {email_path}")

    # Print preview
    print("\n" + "=" * 70)
    print("📧 RECRUITER EMAIL PREVIEW:")
    print("=" * 70)
    print(result.get("recruiter_email_pitch", "")[:1500])

    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)

if __name__ == "__main__":
    run_test()