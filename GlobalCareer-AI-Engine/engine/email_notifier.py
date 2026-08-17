"""
Email Notification Engine — Daily digest reports via Gmail SMTP.
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from config.settings import SMTP_EMAIL, SMTP_APP_PASSWORD, TARGET_EMAIL, CANDIDATE

logger = logging.getLogger("GlobalCareer")

def _build_html_digest(matched_jobs, portal_stats, scan_time):
    """Build a stunning HTML email digest."""
    total = len(matched_jobs)
    portals_active = len(portal_stats)
    total_scanned = sum(portal_stats.values()) if portal_stats else 0

    # Job cards HTML
    cards = ""
    for i, job in enumerate(matched_jobs[:30], 1):
        title = job.get('title', 'N/A')
        company = job.get('company', 'N/A')
        loc = job.get('location', 'Remote')
        source = job.get('source', 'N/A')
        url = job.get('url', '#')
        score = job.get('match_score', 0)
        reason = job.get('eval_reason', '')
        salary = job.get('salary', '')
        region = job.get('region', '')

        score_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 60 else "#ef4444"

        cards += f"""
        <div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;
                    padding:20px 24px;margin-bottom:14px;border-left:4px solid {score_color};">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <h3 style="margin:0;font-size:15px;color:#0f172a;">{i}. {title}</h3>
            <span style="background:{score_color};color:white;padding:3px 10px;border-radius:20px;
                         font-size:12px;font-weight:700;">{score}%</span>
          </div>
          <p style="margin:0 0 4px;font-size:13px;color:#64748b;">
            🏢 <strong>{company}</strong> &nbsp;|&nbsp; 📍 {loc} &nbsp;|&nbsp; 🌍 {region}
          </p>
          {"<p style='margin:0 0 4px;font-size:13px;color:#059669;font-weight:600;'>💰 " + salary + "</p>" if salary else ""}
          <p style="margin:0 0 4px;font-size:11px;color:#94a3b8;">Source: {source}</p>
          <p style="margin:0 0 10px;font-size:13px;color:#334155;background:#f1f5f9;
                    padding:8px 12px;border-radius:6px;">🤖 {reason}</p>
          <a href="{url}" style="display:inline-block;background:#1a56db;color:white;
                                  text-decoration:none;padding:7px 16px;border-radius:6px;
                                  font-size:12px;font-weight:600;">Apply Now →</a>
        </div>"""

    # Top portals
    top_portals = sorted(portal_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    portal_rows = ""
    for name, count in top_portals:
        portal_rows += f"<tr><td style='padding:4px 8px;font-size:12px;'>{name}</td><td style='padding:4px 8px;font-size:12px;text-align:right;font-weight:700;'>{count}</td></tr>"

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',Arial,sans-serif;">
  <div style="max-width:680px;margin:0 auto;padding:24px 16px;">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1e40af 0%,#7c3aed 50%,#ec4899 100%);
                border-radius:16px;padding:32px;margin-bottom:20px;color:white;">
      <h1 style="margin:0 0 4px;font-size:26px;">🌍 GlobalCareer AI Engine</h1>
      <p style="margin:0 0 12px;opacity:0.85;font-size:14px;">
        Daily Job Intelligence Report — {scan_time}
      </p>
      <div style="display:flex;gap:16px;flex-wrap:wrap;">
        <div style="background:rgba(255,255,255,0.15);border-radius:10px;padding:12px 18px;">
          <div style="font-size:28px;font-weight:800;">{total}</div>
          <div style="font-size:11px;opacity:0.8;">Matched Jobs</div>
        </div>
        <div style="background:rgba(255,255,255,0.15);border-radius:10px;padding:12px 18px;">
          <div style="font-size:28px;font-weight:800;">{total_scanned}</div>
          <div style="font-size:11px;opacity:0.8;">Total Scanned</div>
        </div>
        <div style="background:rgba(255,255,255,0.15);border-radius:10px;padding:12px 18px;">
          <div style="font-size:28px;font-weight:800;">{portals_active}</div>
          <div style="font-size:11px;opacity:0.8;">Active Portals</div>
        </div>
      </div>
    </div>

    <!-- Jobs -->
    <div style="background:#1e293b;border-radius:14px;padding:20px;margin-bottom:16px;">
      <h2 style="color:white;margin:0 0 16px;font-size:18px;">🎯 Top Matching Jobs</h2>
      {cards if cards else '<p style="color:#94a3b8;text-align:center;padding:30px;">No matches found this scan. Keep hunting! 💪</p>'}
    </div>

    <!-- Portal Stats -->
    <div style="background:#1e293b;border-radius:14px;padding:20px;margin-bottom:16px;">
      <h2 style="color:white;margin:0 0 12px;font-size:16px;">📊 Top Active Portals</h2>
      <table style="width:100%;color:#cbd5e1;border-collapse:collapse;">
        <tr style="border-bottom:1px solid #334155;">
          <th style="padding:6px 8px;text-align:left;font-size:12px;color:#94a3b8;">Portal</th>
          <th style="padding:6px 8px;text-align:right;font-size:12px;color:#94a3b8;">Jobs</th>
        </tr>
        {portal_rows}
      </table>
    </div>

    <!-- Target Profile -->
    <div style="background:#172554;border:1px solid #1e40af;border-radius:12px;
                padding:16px 20px;margin-top:16px;font-size:12px;color:#93c5fd;">
      <strong>🎯 Hunt Profile:</strong><br>
      Target: ~₹1 Cr ({CANDIDATE['target_package_range']}) | Remote Foreign Currency | Visa Sponsorship<br>
      <strong>Skills:</strong> Qlik Sense · Databricks · dbt · SQL · Python · Power BI · Data Migration<br>
      <strong>Coverage:</strong> 300+ portals across 80+ countries
    </div>

    <!-- Footer -->
    <p style="text-align:center;font-size:11px;color:#475569;margin-top:20px;">
      Powered by GlobalCareer AI Engine 🤖<br>
      Scanning 4x daily: 6AM · 12PM · 6PM · 11PM IST
    </p>
  </div>
</body>
</html>"""
    return html

def send_digest_email(matched_jobs, portal_stats=None):
    """Send daily digest email."""
    if not SMTP_EMAIL or not SMTP_APP_PASSWORD:
        logger.warning("SMTP not configured — skipping email")
        return False

    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M IST")
    total = len(matched_jobs)

    subject = f"🌍 GlobalCareer: {total} Job{'s' if total != 1 else ''} Found — {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    if total == 0:
        subject = f"🌍 GlobalCareer: No Matches This Scan — {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    html_body = _build_html_digest(matched_jobs, portal_stats or {}, scan_time)

    # Plain text fallback
    plain = f"GlobalCareer Report {scan_time}\n\nFound {total} matching jobs.\n\n"
    for i, job in enumerate(matched_jobs[:20], 1):
        plain += f"{i}. {job.get('title')} @ {job.get('company')} ({job.get('match_score', 0)}%)\n"
        plain += f"   {job.get('url')}\n"
        plain += f"   {job.get('eval_reason', '')}\n\n"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = TARGET_EMAIL
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            smtp.send_message(msg)
        logger.info(f"📨 Digest email sent to {TARGET_EMAIL} ({total} jobs)")
        return True
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False

def save_report_markdown(matched_jobs, portal_stats=None):
    """Save a local markdown report."""
    from config.settings import PROJECT_ROOT
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    filepath = os.path.join(PROJECT_ROOT, "data", f"report_{date_str}.md")

    with open(filepath, "w") as f:
        f.write(f"# 🌍 GlobalCareer AI Report — {date_str}\n\n")
        f.write(f"**{len(matched_jobs)} matching jobs** found.\n\n")
        if portal_stats:
            f.write(f"**{sum(portal_stats.values())} total scanned** from **{len(portal_stats)} portals**\n\n")
        f.write("---\n\n")
        for i, job in enumerate(matched_jobs, 1):
            f.write(f"## {i}. {job.get('title')} — {job.get('company')}\n")
            f.write(f"- **Score:** {job.get('match_score', 0)}%\n")
            f.write(f"- **Location:** {job.get('location', 'N/A')}\n")
            f.write(f"- **Region:** {job.get('region', 'N/A')}\n")
            f.write(f"- **Source:** {job.get('source', 'N/A')}\n")
            if job.get('salary'):
                f.write(f"- **Salary:** {job.get('salary')}\n")
            f.write(f"- **Apply:** [{job.get('url', '#')}]({job.get('url', '#')})\n")
            f.write(f"- **AI Reason:** {job.get('eval_reason', 'N/A')}\n\n")

    logger.info(f"📄 Report saved: {filepath}")
    return filepath
