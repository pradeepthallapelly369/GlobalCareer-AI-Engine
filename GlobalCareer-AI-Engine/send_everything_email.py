import os
import sys
import smtplib
import sqlite3
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config.settings import SMTP_EMAIL, SMTP_APP_PASSWORD, TARGET_EMAIL
from config.portals import PORTALS, get_portal_stats

def gather_data():
    portal_stats = get_portal_stats()
    
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "applications.db")
    if not os.path.exists(db_path):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "applications.db")
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    total_apps = cur.execute("SELECT count(*) FROM applications").fetchone()[0]
    
    cur.execute("""
        SELECT title, company, location, match_score, status, source, url, salary, eval_reason 
        FROM applications 
        ORDER BY match_score DESC, id DESC 
        LIMIT 15
    """)
    top_jobs = cur.fetchall()
    
    status_counts = cur.execute("""
        SELECT status, count(*) FROM applications GROUP BY status
    """).fetchall()
    
    conn.close()
    
    return {
        "portal_stats": portal_stats,
        "total_apps": total_apps,
        "status_counts": dict(status_counts),
        "top_jobs": top_jobs,
    }

def build_email_content(data):
    p_stats = data["portal_stats"]
    total_apps = data["total_apps"]
    status_counts = data["status_counts"]
    top_jobs = data["top_jobs"]
    now_str = datetime.now().strftime("%B %d, %Y - %I:%M %p IST")
    
    # Text fallback
    text_content = f"""GLOBAL CAREER & JOB SEARCH SYSTEMS AUDIT & SUMMARY REPORT
Generated: {now_str}
Recipient: {TARGET_EMAIL}

==================================================
1. JOB SEARCH APPS IN YOUR WORKSPACE
==================================================
1. GlobalCareer-AI-Engine (Flagship Autonomous Engine)
   - Status: ACTIVE & RUNNING (systemd: globalcareer.service)
   - Features: 149 portals across 70 regions, AI Match Scoring, ATS Resume Tailoring, Cold Recruiter Emailer, Glassmorphic Dashboard.
2. QlikHunter
   - Purpose: Autonomous BI/Qlik/Data Engineer job hunter across LinkedIn, Remotive, Upwork with daily HTML digest notifications.
3. ai-job-search
   - Purpose: Claude Code CLI-based application workflow (/scrape, /apply, /interview) for end-to-end job prep.
4. linkedin_outreach_bot
   - Purpose: Selenium Chrome automation script for recruiter outreach and connection pitches.

==================================================
2. GLOBAL PORTAL ECOSYSTEM (149 INTEGRATED SOURCES)
==================================================
Total Portals Configured: {p_stats['total_portals']}
Unique Countries/Regions: {p_stats['unique_regions']}
Categories:
- Major Portals (LinkedIn, Indeed, Glassdoor via JobSpy): {p_stats['by_category'].get('major', 0)}
- Regional Job Boards: {p_stats['by_category'].get('regional', 0)}
- Remote-First Platforms: {p_stats['by_category'].get('remote', 0)}
- Tech-Specific Hubs: {p_stats['by_category'].get('tech', 0)}
- Visa Sponsorship Boards: {p_stats['by_category'].get('visa', 0)}
- Data & AI Specialized: {p_stats['by_category'].get('data', 0)}
- Freelance Platforms: {p_stats['by_category'].get('freelance', 0)}
- Government & Startup Portals: {p_stats['by_category'].get('government', 0) + p_stats['by_category'].get('startup', 0)}

==================================================
3. DATABASE TRACKER STATUS ({total_apps} JOBS TRACKED)
==================================================
Application Status Breakdown:
{chr(10).join(f"- {k}: {v}" for k, v in status_counts.items())}

TOP SCOUTED JOBS:
"""
    for i, j in enumerate(top_jobs, 1):
        title, comp, loc, score, status, src, url, sal, reason = j
        text_content += f"{i}. {title} @ {comp} ({score}% Match | Status: {status})\n   Source: {src} | Location: {loc or 'Worldwide Remote'}\n   Apply: {url}\n\n"

    # HTML content
    job_rows = ""
    for i, j in enumerate(top_jobs, 1):
        title, comp, loc, score, status, src, url, sal, reason = j
        score_color = "#10b981" if score >= 90 else "#3b82f6" if score >= 80 else "#f59e0b"
        status_badge_bg = "#22c55e" if status == "Applied" else "#6366f1"
        job_rows += f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:16px 20px; margin-bottom:12px; border-left:4px solid {score_color}; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:6px;">
            <div>
              <h3 style="margin:0 0 4px 0; font-size:15px; color:#0f172a; font-weight:700;">{i}. {title}</h3>
              <p style="margin:0; font-size:13px; color:#475569;"><strong>{comp}</strong> &bull; <span style="color:#64748b;">{loc or 'Worldwide Remote'}</span></p>
            </div>
            <div style="text-align:right;">
              <span style="background:{score_color}; color:#ffffff; font-size:11px; font-weight:700; padding:3px 8px; border-radius:12px; display:inline-block; margin-bottom:4px;">{score}% Match</span><br/>
              <span style="background:{status_badge_bg}; color:#ffffff; font-size:10px; font-weight:600; padding:2px 6px; border-radius:8px; display:inline-block;">{status}</span>
            </div>
          </div>
          <div style="font-size:12px; color:#64748b; margin-bottom:8px;">
            <span>Source: <strong>{src}</strong></span>
            {" &bull; <span style='color:#059669; font-weight:600;'>" + sal + "</span>" if sal else ""}
          </div>
          {f'<div style="font-size:12px; color:#334155; background:#f8fafc; border:1px solid #f1f5f9; padding:8px 12px; border-radius:6px; margin-bottom:10px;">🤖 {reason}</div>' if reason else ''}
          <div>
            <a href="{url}" style="display:inline-block; background:#2563eb; color:#ffffff; text-decoration:none; font-size:12px; font-weight:600; padding:6px 14px; border-radius:6px;">View & Apply &rarr;</a>
          </div>
        </div>
        """

    cat_badges = "".join([
        f'<div style="background:#f1f5f9; border-radius:8px; padding:10px 14px; flex:1; min-width:130px; margin:4px;">'
        f'<div style="font-size:11px; color:#64748b; text-transform:uppercase; font-weight:700;">{k}</div>'
        f'<div style="font-size:18px; color:#0f172a; font-weight:800;">{v}</div>'
        f'</div>'
        for k, v in p_stats['by_category'].items()
    ])

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Job Search Intelligence & Systems Report</title>
</head>
<body style="margin:0; padding:0; background-color:#0f172a; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color:#334155;">
  <div style="max-width:720px; margin:0 auto; padding:28px 16px;">
    
    <!-- Header Banner -->
    <div style="background:linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #7c3aed 100%); border-radius:16px; padding:32px 24px; color:#ffffff; margin-bottom:24px; box-shadow:0 10px 25px -5px rgba(0,0,0,0.3);">
      <div style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; opacity:0.85; margin-bottom:6px;">Autonomous Career Intelligence</div>
      <h1 style="margin:0 0 8px 0; font-size:26px; font-weight:800;">Comprehensive Job Search Report</h1>
      <p style="margin:0; font-size:13px; opacity:0.9;">Dispatched to: <strong>{TARGET_EMAIL}</strong> &bull; {now_str}</p>
    </div>

    <!-- Section 1: Job Search Apps in Workspace -->
    <div style="background:#ffffff; border-radius:14px; padding:24px; margin-bottom:20px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
      <h2 style="margin:0 0 16px 0; font-size:18px; color:#0f172a; display:flex; align-items:center;">
        💻 Job Search Applications in Your Workspace
      </h2>
      
      <table style="width:100%; border-collapse:collapse; font-size:13px;">
        <thead>
          <tr style="background:#f8fafc; border-bottom:2px solid #e2e8f0;">
            <th style="padding:10px; text-align:left; color:#475569;">Application</th>
            <th style="padding:10px; text-align:left; color:#475569;">Stack & Status</th>
            <th style="padding:10px; text-align:left; color:#475569;">Primary Function</th>
          </tr>
        </thead>
        <tbody>
          <tr style="border-bottom:1px solid #f1f5f9;">
            <td style="padding:12px 10px; font-weight:700; color:#1e40af;">GlobalCareer AI Engine</td>
            <td style="padding:12px 10px;"><span style="background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">ACTIVE SERVICE</span><br/><span style="color:#64748b; font-size:11px;">FastAPI &bull; SQLite &bull; OpenRouter</span></td>
            <td style="padding:12px 10px; color:#475569;">Autonomous 149-portal scout, AI JD resume optimization, cold recruiter pitches, application tracker.</td>
          </tr>
          <tr style="border-bottom:1px solid #f1f5f9;">
            <td style="padding:12px 10px; font-weight:700; color:#0f172a;">QlikHunter</td>
            <td style="padding:12px 10px;"><span style="background:#e0e7ff; color:#4338ca; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">CONFIGURED</span><br/><span style="color:#64748b; font-size:11px;">Python &bull; SMTP Alerts</span></td>
            <td style="padding:12px 10px; color:#475569;">Autonomous multi-portal BI/Qlik/Data scout delivering scheduled daily HTML email digests.</td>
          </tr>
          <tr style="border-bottom:1px solid #f1f5f9;">
            <td style="padding:12px 10px; font-weight:700; color:#0f172a;">ai-job-search</td>
            <td style="padding:12px 10px;"><span style="background:#f1f5f9; color:#475569; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">CLI WORKFLOW</span><br/><span style="color:#64748b; font-size:11px;">Claude Code Toolkit</span></td>
            <td style="padding:12px 10px; color:#475569;">Personal career CLI workflow (/scrape, /apply, /interview) for tailoring CVs and interview preparation.</td>
          </tr>
          <tr>
            <td style="padding:12px 10px; font-weight:700; color:#0f172a;">linkedin_outreach_bot</td>
            <td style="padding:12px 10px;"><span style="background:#fef3c7; color:#b45309; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:700;">AUTOMATION</span><br/><span style="color:#64748b; font-size:11px;">Selenium &bull; Chrome</span></td>
            <td style="padding:12px 10px; color:#475569;">Browser automation tool for sending recruiter connection invites and outreach pitch messages.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Section 2: 149 Portals Breakdown -->
    <div style="background:#ffffff; border-radius:14px; padding:24px; margin-bottom:20px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
      <h2 style="margin:0 0 6px 0; font-size:18px; color:#0f172a;">
        🌐 Global Job Portal Network (149 Sources / 70 Regions)
      </h2>
      <p style="margin:0 0 16px 0; font-size:13px; color:#64748b;">
        Automated scrapers configured inside GlobalCareer AI Engine across 70 target countries:
      </p>
      <div style="display:flex; flex-wrap:wrap; margin:-4px; margin-bottom:16px;">
        {cat_badges}
      </div>
      <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px 16px; font-size:12px; color:#475569; line-height:1.5;">
        <strong>Key Hubs Covered:</strong> LinkedIn (JobSpy across 70 countries), Indeed, Glassdoor, RemoteOK, WeWorkRemotely, Remotive, Jobicy, Himalayas, Wellfound, Relocate.me, Bayt, GulfTalent, Upwork, and specialized AI/Data boards.
      </div>
    </div>

    <!-- Section 3: Applications Tracker & Top Scouted Jobs -->
    <div style="background:#ffffff; border-radius:14px; padding:24px; margin-bottom:20px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
        <h2 style="margin:0; font-size:18px; color:#0f172a;">
          🎯 Top Scouted Jobs & Application Tracker
        </h2>
        <span style="background:#3b82f6; color:#ffffff; font-size:12px; font-weight:700; padding:4px 10px; border-radius:12px;">
          {total_apps} Jobs Tracked
        </span>
      </div>
      
      <div style="margin-bottom:16px;">
        {job_rows}
      </div>
    </div>

    <!-- Footer -->
    <div style="text-align:center; padding:16px; font-size:12px; color:#94a3b8;">
      GlobalCareer AI Engine &bull; QlikHunter Career Intelligence<br/>
      Sent automatically via authenticated SMTP to {TARGET_EMAIL}
    </div>

  </div>
</body>
</html>
"""
    return text_content, html_content

def send_mail():
    print(f"Gathering data from applications.db and config...")
    data = gather_data()
    text_content, html_content = build_email_content(data)
    
    subject = f"🌍 GlobalCareer & Job Search Ecosystem Audit — {datetime.now().strftime('%b %d, %Y')}"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"GlobalCareer AI Scout <{SMTP_EMAIL}>"
    msg["To"] = TARGET_EMAIL
    
    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))
    
    print(f"Connecting to Gmail SMTP to deliver email to: {TARGET_EMAIL}")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.send_message(msg)
    print(f"✅ Successfully dispatched complete report to {TARGET_EMAIL}!")

if __name__ == "__main__":
    send_mail()
