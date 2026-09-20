"""
Web Dashboard — FastAPI-powered job tracking dashboard.
"""

import os
import sys
import json
import logging
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.application_tracker import get_all_applications, get_stats, get_scan_history, update_status
from config.portals import get_portal_stats

logger = logging.getLogger("GlobalCareer")

app = FastAPI(title="GlobalCareer AI Engine", version="2.0")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    stats = get_stats()
    applications = get_all_applications(limit=200)
    scan_history = get_scan_history(limit=10)
    portal_info = get_portal_stats()

    # Build job rows
    now = datetime.now()
    job_rows = ""
    apps_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "applications")
    for job in applications:
        created_str = job.get("created_at") or ""
        days_old = 0
        formatted_date = "Recent"
        if created_str:
            try:
                c_date = datetime.strptime(created_str[:10], "%Y-%m-%d")
                days_old = (now - c_date).days
                if days_old == 0:
                    formatted_date = "Today"
                elif days_old == 1:
                    formatted_date = "Yesterday"
                else:
                    formatted_date = f"{c_date.strftime('%b %d')} ({days_old}d ago)"
            except Exception:
                formatted_date = created_str[:10]

        if days_old > 45:
            continue

        score = job.get("match_score", 0)
        score_class = "high" if score >= 80 else "medium" if score >= 60 else "low"
        status = job.get("status", "Discovered")
        status_class = status.lower().replace(" ", "-")
        date_class = "date-fresh" if days_old <= 7 else "date-recent" if days_old <= 30 else "date-older"

        tailored_link = ""
        job_id = job.get("id", "")
        company = job.get("company", "")
        if os.path.exists(apps_dir):
            for d in os.listdir(apps_dir):
                if (job_id and job_id[:8] in d) or (company and len(company) > 2 and company.lower() in d.lower()):
                    tailored_link = f""" <a href="/api/tailored/{job_id or d}" target="_blank" class="apply-btn" style="background:var(--accent-purple);margin-left:4px;">View CV 📄</a>"""
                    break

        job_rows += f"""
        <tr class="job-row" data-score="{score}" data-status="{status}" data-days="{days_old}">
            <td><span class="score-badge {score_class}">{score}%</span></td>
            <td>
                <div class="job-title">{job.get('title', 'N/A')}</div>
                <div class="job-company">{job.get('company', 'N/A')}</div>
            </td>
            <td><span class="date-tag {date_class}">{formatted_date}</span></td>
            <td>{job.get('location', 'Remote')}</td>
            <td>{job.get('region', 'Global')}</td>
            <td>{job.get('salary', '-') or '-'}</td>
            <td><span class="source-tag">{job.get('source', 'N/A')}</span></td>
            <td><span class="status-badge {status_class}">{status}</span></td>
            <td>
                <a href="{job.get('url', '#')}" target="_blank" class="apply-btn">Apply →</a>{tailored_link}
            </td>
        </tr>"""

    # Scan history rows
    scan_rows = ""
    for scan in scan_history:
        scan_rows += f"""
        <tr>
            <td>{scan.get('scan_time', '')}</td>
            <td>{scan.get('total_scanned', 0)}</td>
            <td>{scan.get('total_matched', 0)}</td>
            <td>{scan.get('portals_active', 0)}</td>
            <td>{scan.get('duration_seconds', 0):.1f}s</td>
        </tr>"""

    # Region distribution for chart
    regions = stats.get("by_region", {})
    region_labels = json.dumps(list(regions.keys())[:15])
    region_data = json.dumps(list(regions.values())[:15])

    # Pre-compute values for f-string (avoid dict-in-fstring issues)
    applied_count = stats.get('by_status', {}).get('Applied', 0)
    portal_category_html = "".join(
        f'<div class="portal-stat"><div class="portal-stat-value">{v}</div><div class="portal-stat-label">{k}</div></div>'
        for k, v in portal_info.get('by_category', {}).items()
    )
    regions_list_html = "  ·  ".join(portal_info.get('regions', []))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GlobalCareer AI Engine — Dashboard</title>
    <meta name="description" content="AI-powered global job search engine tracking 300+ portals across 80+ countries">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0e1a;
            --bg-secondary: #111827;
            --bg-card: #1a1f35;
            --bg-card-hover: #1e2444;
            --border-color: #2d3555;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
            --accent-pink: #ec4899;
            --accent-green: #22c55e;
            --accent-amber: #f59e0b;
            --accent-red: #ef4444;
            --accent-cyan: #06b6d4;
            --gradient-main: linear-gradient(135deg, #1e40af, #7c3aed, #ec4899);
            --gradient-card: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.05));
            --shadow-glow: 0 0 40px rgba(59,130,246,0.15);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }}

        /* Animated background */
        body::before {{
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background:
                radial-gradient(circle at 20% 20%, rgba(59,130,246,0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(139,92,246,0.06) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(236,72,153,0.04) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }}

        .container {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 24px;
            position: relative;
            z-index: 1;
        }}

        /* Header */
        .header {{
            background: var(--gradient-main);
            border-radius: 20px;
            padding: 36px 40px;
            margin-bottom: 28px;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-glow);
        }}
        .header::after {{
            content: '';
            position: absolute;
            top: -50%; right: -20%;
            width: 60%; height: 200%;
            background: radial-gradient(ellipse, rgba(255,255,255,0.1) 0%, transparent 70%);
            pointer-events: none;
        }}
        .header h1 {{
            font-size: 32px;
            font-weight: 900;
            letter-spacing: -0.5px;
            margin-bottom: 4px;
        }}
        .header p {{
            opacity: 0.85;
            font-size: 14px;
            font-weight: 400;
        }}
        .header-actions {{
            display: flex;
            gap: 12px;
            margin-top: 16px;
        }}
        .header-btn {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
        }}
        .header-btn:hover {{
            background: rgba(255,255,255,0.25);
            transform: translateY(-2px);
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }}
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s;
        }}
        .stat-card:hover {{
            border-color: var(--accent-blue);
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(59,130,246,0.15);
        }}
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--gradient-main);
            border-radius: 16px 16px 0 0;
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: 900;
            background: var(--gradient-main);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .stat-label {{
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
        }}

        /* Tab system */
        .tabs {{
            display: flex;
            gap: 4px;
            margin-bottom: 20px;
            background: var(--bg-secondary);
            padding: 4px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }}
        .tab {{
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            color: var(--text-secondary);
            border: none;
            background: none;
        }}
        .tab.active {{
            background: var(--accent-blue);
            color: white;
        }}
        .tab:hover:not(.active) {{
            color: var(--text-primary);
            background: var(--bg-card);
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        /* Table */
        .table-container {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            overflow: hidden;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            text-align: left;
            padding: 14px 16px;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
        }}
        td {{
            padding: 14px 16px;
            font-size: 13px;
            border-bottom: 1px solid rgba(45,53,85,0.5);
            vertical-align: middle;
        }}
        .job-row {{
            transition: background 0.2s;
        }}
        .job-row:hover {{
            background: var(--bg-card-hover);
        }}
        .job-title {{
            font-weight: 600;
            color: var(--text-primary);
            font-size: 14px;
        }}
        .job-company {{
            color: var(--text-secondary);
            font-size: 12px;
            margin-top: 2px;
        }}

        /* Badges */
        .score-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 48px;
            height: 28px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
        }}
        .score-badge.high {{ background: rgba(34,197,94,0.15); color: var(--accent-green); }}
        .score-badge.medium {{ background: rgba(245,158,11,0.15); color: var(--accent-amber); }}
        .score-badge.low {{ background: rgba(239,68,68,0.15); color: var(--accent-red); }}

        .status-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }}
        .status-badge.discovered {{ background: rgba(59,130,246,0.15); color: var(--accent-blue); }}
        .status-badge.applied {{ background: rgba(34,197,94,0.15); color: var(--accent-green); }}
        .status-badge.interview {{ background: rgba(139,92,246,0.15); color: var(--accent-purple); }}
        .status-badge.rejected {{ background: rgba(239,68,68,0.15); color: var(--accent-red); }}

        .source-tag {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 500;
            background: rgba(6,182,212,0.1);
            color: var(--accent-cyan);
            max-width: 140px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}

        .apply-btn {{
            display: inline-block;
            padding: 6px 14px;
            background: var(--accent-blue);
            color: white;
            border-radius: 6px;
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .apply-btn:hover {{
            background: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59,130,246,0.3);
        }}

        /* Search & Filter */
        .controls {{
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }}
        .search-input {{
            flex: 1;
            min-width: 200px;
            padding: 10px 16px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-size: 13px;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-input:focus {{
            border-color: var(--accent-blue);
        }}
        .filter-select {{
            padding: 10px 16px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-size: 13px;
            outline: none;
            cursor: pointer;
        }}

        /* Portal coverage */
        .portal-info {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
        }}
        .portal-info h3 {{
            font-size: 16px;
            margin-bottom: 12px;
            color: var(--text-primary);
        }}
        .portal-stats {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}
        .portal-stat {{
            text-align: center;
        }}
        .portal-stat-value {{
            font-size: 24px;
            font-weight: 800;
            color: var(--accent-cyan);
        }}
        .portal-stat-label {{
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .container {{ padding: 12px; }}
            .header {{ padding: 24px; }}
            .header h1 {{ font-size: 22px; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .table-container {{ overflow-x: auto; }}
            table {{ min-width: 800px; }}
        }}

        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .stat-card, .table-container, .portal-info {{
            animation: fadeIn 0.5s ease-out forwards;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🌍 GlobalCareer AI Engine</h1>
            <p>Autonomous Job Intelligence — {portal_info['total_portals']} Portals · {portal_info['unique_regions']} Regions · Scanning 4x Daily</p>
            <div class="header-actions">
                <button onclick="triggerScan()" class="header-btn" id="scan-btn" style="cursor:pointer;border:none;">🔍 Run Scan Now</button>
                <a href="/api/stats" class="header-btn">📊 API Stats</a>
                <a href="/api/jobs" class="header-btn">📋 Jobs API</a>
            </div>
        </div>

        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_jobs', 0)}</div>
                <div class="stat-label">Total Jobs Tracked</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('avg_match_score', 0):.0f}%</div>
                <div class="stat-label">Avg Match Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('total_scans', 0)}</div>
                <div class="stat-label">Total Scans</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{portal_info['total_portals']}</div>
                <div class="stat-label">Portals Configured</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{portal_info['unique_regions']}</div>
                <div class="stat-label">Countries/Regions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{applied_count}</div>
                <div class="stat-label">Applied</div>
            </div>
        </div>

        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="showTab('jobs')">🎯 Jobs ({stats.get('total_jobs', 0)})</button>
            <button class="tab" onclick="showTab('scans')">📡 Scan History</button>
            <button class="tab" onclick="showTab('portals')">🌐 Portal Coverage</button>
        </div>

        <!-- Jobs Tab -->
        <div id="tab-jobs" class="tab-content active">
            <div class="controls">
                <input type="text" class="search-input" id="search" placeholder="Search jobs by title, company, or location..." oninput="filterJobs()">
                <select class="filter-select" id="date-filter" onchange="filterJobs()">
                    <option value="45">📅 Max 45 Days</option>
                    <option value="30">📅 Past 30 Days</option>
                    <option value="14">📅 Past 14 Days</option>
                    <option value="7">📅 Past 7 Days (Fresh)</option>
                    <option value="all">All Loaded</option>
                </select>
                <select class="filter-select" id="score-filter" onchange="filterJobs()">
                    <option value="all">All Scores</option>
                    <option value="80">80%+ Only</option>
                    <option value="60">60%+ Only</option>
                </select>
                <select class="filter-select" id="status-filter" onchange="filterJobs()">
                    <option value="all">All Status</option>
                    <option value="Discovered">Discovered</option>
                    <option value="Applied">Applied</option>
                    <option value="Interview">Interview</option>
                </select>
            </div>
            <div class="table-container">
                <table id="jobs-table">
                    <thead>
                        <tr>
                            <th>Score</th>
                            <th>Job</th>
                            <th>Date</th>
                            <th>Location</th>
                            <th>Region</th>
                            <th>Salary</th>
                            <th>Source</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>{job_rows}</tbody>
                </table>
            </div>
        </div>

        <!-- Scans Tab -->
        <div id="tab-scans" class="tab-content">
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Scan Time</th>
                            <th>Scanned</th>
                            <th>Matched</th>
                            <th>Portals</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody>{scan_rows}</tbody>
                </table>
            </div>
        </div>

        <!-- Portals Tab -->
        <div id="tab-portals" class="tab-content">
            <div class="portal-info">
                <h3>🌐 Portal Coverage Overview</h3>
                <div class="portal-stats">
                    {portal_category_html}
                </div>
            </div>
            <div class="portal-info">
                <h3>🗺️ Regions Covered</h3>
                <p style="color:var(--text-secondary);font-size:13px;line-height:2;">
                    {regions_list_html}
                </p>
            </div>
        </div>
    </div>

    <script>
        function showTab(name) {{
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById('tab-' + name).classList.add('active');
            event.target.classList.add('active');
        }}

        async function triggerScan() {{
            const btn = document.getElementById('scan-btn');
            btn.innerText = '⏳ Scanning...';
            btn.style.opacity = '0.7';
            btn.disabled = true;
            try {{
                const res = await fetch('/api/trigger-scan');
                const data = await res.json();
                alert("Scan triggered in background! 149 portals are being evaluated. New matches will be emailed to pradeep.thallapelly369@outlook.com.");
            }} catch(e) {{
                alert("Error triggering scan: " + e);
            }} finally {{
                btn.innerText = '🔍 Run Scan Now';
                btn.style.opacity = '1';
                btn.disabled = false;
            }}
        }}

        function filterJobs() {{
            const search = document.getElementById('search').value.toLowerCase();
            const scoreFilter = document.getElementById('score-filter').value;
            const statusFilter = document.getElementById('status-filter').value;
            const dateFilter = document.getElementById('date-filter') ? document.getElementById('date-filter').value : 'all';

            document.querySelectorAll('.job-row').forEach(row => {{
                const text = row.textContent.toLowerCase();
                const score = parseInt(row.dataset.score) || 0;
                const status = row.dataset.status || '';
                const days = parseInt(row.dataset.days) || 0;

                let show = text.includes(search);
                if (scoreFilter !== 'all') show = show && score >= parseInt(scoreFilter);
                if (statusFilter !== 'all') show = show && status === statusFilter;
                if (dateFilter !== 'all') show = show && days <= parseInt(dateFilter);

                row.style.display = show ? '' : 'none';
            }});
        }}
    </script>
</body>
</html>"""
    return html

@app.get("/api/stats")
async def api_stats():
    return get_stats()

@app.get("/api/jobs")
async def api_jobs(limit: int = 100):
    return get_all_applications(limit=limit)

@app.get("/api/scans")
async def api_scans():
    return get_scan_history()

@app.get("/api/portals")
async def api_portals():
    return get_portal_stats()

@app.post("/api/status/{job_id}")
async def api_update_status(job_id: str, request: Request):
    data = await request.json()
    update_status(job_id, data.get("status", "Applied"), data.get("notes", ""))
    return {"ok": True}

@app.get("/api/trigger-scan")
async def api_trigger_scan():
    """Trigger a manual scan (runs in background)."""
    import threading
    def _scan():
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from main import run_scan
        run_scan()
    thread = threading.Thread(target=_scan, daemon=True)
    thread.start()
    return {"status": "Scan triggered", "message": "Check email for results in ~5 minutes"}

@app.get("/api/tailored/{job_id}", response_class=HTMLResponse)
async def view_tailored_job(job_id: str):
    apps_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "applications")
    target_dir = None
    if os.path.exists(apps_dir):
        for d in os.listdir(apps_dir):
            if (job_id and job_id[:8] in d) or job_id == d:
                target_dir = os.path.join(apps_dir, d)
                break
    
    resume_content = "No tailored resume found for this job yet."
    cover_content = "No tailored cover letter found."
    company_name = "Application"
    if target_dir:
        company_name = os.path.basename(target_dir).split("_")[0]
        res_path = os.path.join(target_dir, "Tailored_Resume.md")
        if os.path.exists(res_path):
            with open(res_path, "r", encoding="utf-8") as f:
                resume_content = f.read()
        cov_path = os.path.join(target_dir, "Cover_Letter.md")
        if os.path.exists(cov_path):
            with open(cov_path, "r", encoding="utf-8") as f:
                cover_content = f.read()
                
    import markdown
    try:
        resume_html = markdown.markdown(resume_content, extensions=['tables', 'fenced_code'])
        cover_html = markdown.markdown(cover_content, extensions=['tables', 'fenced_code'])
    except Exception:
        resume_html = f"<pre>{resume_content}</pre>"
        cover_html = f"<pre>{cover_content}</pre>"
        
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{company_name} — Tailored Application Package</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', -apple-system, sans-serif; background: #0a0e1a; color: #f1f5f9; padding: 40px 20px; max-width: 900px; margin: 0 auto; line-height: 1.6; }}
            .top-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }}
            .btn {{ background: #2563eb; color: white; text-decoration: none; padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; display: inline-block; }}
            .card {{ background: #1a1f35; border: 1px solid #2d3555; border-radius: 12px; padding: 28px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
            h1, h2, h3 {{ color: #38bdf8; margin-top: 0; }}
            hr {{ border: none; border-top: 1px solid #2d3555; margin: 20px 0; }}
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 6px; }}
            pre, code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; color: #38bdf8; }}
        </style>
    </head>
    <body>
        <div class="top-bar">
            <a href="/" class="btn">&larr; Back to Dashboard</a>
            <span style="color: #94a3b8; font-size: 13px;">Target: {company_name}</span>
        </div>
        <div class="card">
            <h2>📄 Tailored ATS Resume</h2>
            <hr>
            <div>{resume_html}</div>
        </div>
        <div class="card">
            <h2 style="color:#a78bfa;">✉️ Tailored Cover Letter</h2>
            <hr>
            <div>{cover_html}</div>
        </div>
    </body>
    </html>"""
    return html

def start_dashboard(host="0.0.0.0", port=None):
    """Start the dashboard server."""
    if port is None:
        port = int(os.environ.get("PORT", 8888))
    
    if port == 8888:
        import threading
        def _serve_8888():
            try:
                uvicorn.run(app, host=host, port=5070, log_level="warning")
            except Exception as e:
                logger.debug(f"Port 8888 listener: {e}")
        threading.Thread(target=_serve_8888, daemon=True).start()

    print(f"🌍 GlobalCareer Dashboard starting at http://localhost:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_dashboard()
