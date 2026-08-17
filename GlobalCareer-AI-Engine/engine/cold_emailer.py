"""
Cold Email Engine — Auto-generate and send personalized recruiter outreach emails.
"""

import os
import smtplib
import logging
import json
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from config.settings import SMTP_EMAIL, SMTP_APP_PASSWORD, TARGET_EMAIL, CANDIDATE

logger = logging.getLogger("GlobalCareer")

def _generate_cold_email_llm(job):
    """Generate a personalized cold email using LLM."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return _generate_cold_email_template(job)

    title = job.get("title", "Data Engineer")
    company = job.get("company", "your company")
    
    prompt = f"""Write a concise, professional cold email to a recruiter for this job:

Job: {title} at {company}
Location: {job.get('location', 'Remote')}

Candidate: {CANDIDATE['name']}
- 6+ years Senior BI Developer & Data Engineer
- Expertise: Qlik Sense, Databricks, dbt, SQL, Python, AI Agents
- Currently Technical Lead at IFINGlobal (Qlik-to-Databricks migration)
- 100+ production dashboards, 30% performance improvement
- Certified Qlik Data Architect & Databricks practitioner
- Based in Hyderabad, India — open to remote with US/EU overlap

Write exactly 3 paragraphs:
1. Hook (mention the specific role and why you're excited)
2. Value proposition (top 3 quantified achievements)
3. Call to action (suggest a 10-min call)

Keep it under 200 words. Professional but warm. No fluff.
Return ONLY the email body text, no subject line."""

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/pradeepthallapelly369/GlobalCareer-AI-Engine",
        }
        models = ["google/gemma-3-27b-it:free", "meta-llama/llama-3.3-70b-instruct:free"]
        for model in models:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                headers=headers, json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                }, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
    except Exception as e:
        logger.debug(f"LLM cold email failed: {e}")
    
    return _generate_cold_email_template(job)

def _generate_cold_email_template(job):
    """Fallback template-based cold email."""
    title = job.get("title", "Data Engineer")
    company = job.get("company", "your company")
    
    return f"""Hi,

I came across the {title} opening at {company} and was immediately excited — my background in enterprise BI and data engineering aligns perfectly with what you're building.

Quick highlights: I'm a Senior BI Developer & Data Engineer with 6+ years of experience. Currently, I lead the end-to-end Qlik-to-Databricks migration at IFINGlobal, using dbt SQL models and AI-agent-assisted data reconciliation. I've delivered 100+ production Qlik Sense dashboards for UK banking clients, driving a 30% performance improvement and 20% data redundancy reduction. I hold Qlik Sense Data Architect and Databricks certifications.

I'd love a brief 10-minute call to discuss how my experience could contribute to {company}'s data initiatives. My resume and portfolio are at {CANDIDATE['portfolio']}.

Best regards,
{CANDIDATE['name']}
{CANDIDATE['phone']} | {CANDIDATE['email']}
{CANDIDATE['linkedin']}"""

def generate_cold_email(job):
    """Generate a cold email for a job posting."""
    body = _generate_cold_email_llm(job)
    title = job.get("title", "Data Engineer")
    company = job.get("company", "Company")
    
    subject = f"Application: {title} — {CANDIDATE['name']} (Senior BI Developer & Data Engineer, 6+ YoE)"
    
    return {
        "subject": subject,
        "body": body,
        "to": job.get("recruiter_email", ""),
        "job_title": title,
        "company": company,
        "generated_at": datetime.now().isoformat(),
    }

def send_cold_email(email_data, to_address=None):
    """Send a cold email via Gmail SMTP."""
    if not SMTP_EMAIL or not SMTP_APP_PASSWORD:
        logger.warning("SMTP not configured — skipping cold email send")
        return False

    to = to_address or email_data.get("to", "")
    if not to:
        logger.debug(f"No recruiter email for {email_data.get('company', 'unknown')}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = email_data["subject"]
    msg["From"] = SMTP_EMAIL
    msg["To"] = to

    # Plain text
    msg.attach(MIMEText(email_data["body"], "plain"))

    # HTML version
    html_body = email_data["body"].replace("\n", "<br>")
    html = f"""<div style="font-family:'Segoe UI',Arial,sans-serif;font-size:14px;color:#1e293b;line-height:1.6;">
{html_body}
</div>"""
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            smtp.send_message(msg)
        logger.info(f"📧 Cold email sent to {to} for {email_data.get('company', '')}")
        return True
    except Exception as e:
        logger.error(f"Cold email send failed: {e}")
        return False

def batch_generate_cold_emails(matched_jobs, max_emails=20):
    """Generate cold emails for top matched jobs."""
    emails = []
    for job in matched_jobs[:max_emails]:
        email_data = generate_cold_email(job)
        emails.append(email_data)
    logger.info(f"📧 Generated {len(emails)} cold email drafts")
    return emails
