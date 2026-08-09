"""
GlobalCareer-AI-Engine — Dashboard Server
FastAPI Backend & Interactive Web UI running on port 5060
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json

from engine.resume_optimizer import optimize_resume_for_jd, load_master_dossier
from engine.global_job_scout import scout_all_global_jobs
from engine.application_tracker import (
    add_or_update_job, get_all_applications, get_application_stats, update_application_status
)
from engine.country_standards import COUNTRY_FORMATS

app = FastAPI(title="GlobalCareer-AI-Engine 🌐", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class OptimizeReq(BaseModel):
    job_title: str
    company: str
    jd_text: str
    country: str = "GLOBAL_REMOTE"

class TrackReq(BaseModel):
    id: str = ""
    title: str
    company: str
    location: str = "Worldwide Remote"
    url: str = ""
    salary: str = "$60K-$120K USD"
    type: str = "Remote (USD/Worldwide)"
    match_score: int = 85
    status: str = "Discovered"

# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/dossier")
def get_dossier():
    return load_master_dossier()

@app.get("/api/country-formats")
def get_country_formats():
    return COUNTRY_FORMATS

@app.post("/api/optimize-resume")
def api_optimize_resume(req: OptimizeReq):
    result = optimize_resume_for_jd(req.job_title, req.company, req.jd_text, req.country)
    # Save to application db
    add_or_update_job({
        "id": f"opt_{hash(req.job_title + req.company)}",
        "title": req.job_title,
        "company": req.company,
        "location": f"{req.country} Target",
        "match_score": result.get("match_score", 85),
        "status": "Tailored",
        "tailored_resume": result.get("tailored_resume_markdown", ""),
        "cover_letter": result.get("cover_letter_markdown", ""),
        "email_pitch": result.get("recruiter_email_pitch", "")
    })
    return result

@app.get("/api/jobs/scout")
def api_scout_jobs():
    jobs = scout_all_global_jobs()
    # Save top matches into DB
    for j in jobs[:20]:
        add_or_update_job(j)
    return {"status": "success", "count": len(jobs), "jobs": jobs}

@app.get("/api/applications")
def api_get_applications():
    apps = get_all_applications()
    stats = get_application_stats()
    return {"status": "success", "stats": stats, "applications": apps}

@app.post("/api/applications/track")
def api_track_job(req: TrackReq):
    job_id = add_or_update_job(req.dict())
    return {"status": "success", "job_id": job_id}

class StatusReq(BaseModel):
    job_id: str
    status: str

@app.post("/api/applications/status")
def api_update_status(req: StatusReq):
    update_application_status(req.job_id, req.status)
    return {"status": "success"}

# ── Web UI Dashboard ──────────────────────────────────────────────────────────

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GlobalCareer AI 🌐 — Remote USD & Visa Job Engine</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --accent-blue: #38bdf8;
            --accent-purple: #a855f7;
            --accent-green: #34d399;
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: var(--bg-gradient); color: var(--text-main); min-height: 100vh; padding: 24px; }
        header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid var(--card-border); margin-bottom: 24px; }
        .logo { font-size: 22px; font-weight: 700; background: linear-gradient(90deg, #38bdf8, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .nav-tabs { display: flex; gap: 12px; }
        .tab-btn { background: rgba(255, 255, 255, 0.05); border: 1px solid var(--card-border); color: var(--text-sub); padding: 10px 18px; border-radius: 8px; font-size: 14px; cursor: pointer; transition: all 0.2s; font-weight: 500; }
        .tab-btn.active, .tab-btn:hover { background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); border-color: var(--accent-blue); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .glass-card { background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--card-border); border-radius: 12px; padding: 24px; margin-bottom: 24px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
        label { font-size: 13px; font-weight: 600; color: var(--text-sub); display: block; margin-bottom: 6px; }
        input, select, textarea { width: 100%; background: rgba(15, 23, 42, 0.6); border: 1px solid var(--card-border); color: var(--text-main); padding: 12px; border-radius: 8px; font-size: 14px; margin-bottom: 16px; outline: none; }
        input:focus, textarea:focus, select:focus { border-color: var(--accent-blue); }
        .btn-primary { background: linear-gradient(90deg, #0284c7, #7c3aed); color: #fff; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
        .btn-primary:hover { opacity: 0.9; }
        .job-card { background: rgba(15, 23, 42, 0.5); border: 1px solid var(--card-border); padding: 16px; border-radius: 10px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; }
        .badge { background: rgba(52, 211, 153, 0.15); color: var(--accent-green); padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }
        .badge-usd { background: rgba(56, 189, 248, 0.15); color: var(--accent-blue); }
        pre { background: #090d16; padding: 16px; border-radius: 8px; font-size: 13px; overflow-x: auto; white-space: pre-wrap; color: #cbd5e1; border: 1px solid var(--card-border); }
    </style>
</head>
<body>
    <header>
        <div class="logo">🌐 GlobalCareer AI Engine</div>
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('optimizer')">🎯 Resume & Pitch Tailor</button>
            <button class="tab-btn" onclick="switchTab('scout')">📡 Live Global Job Radar</button>
            <button class="tab-btn" onclick="switchTab('tracker')">📊 Application Tracker</button>
            <button class="tab-btn" onclick="switchTab('linkedin')">💼 LinkedIn Optimizer</button>
        </div>
    </header>

    <!-- TAB 1: RESUME OPTIMIZER -->
    <div id="optimizer" class="tab-content active">
        <div class="glass-card">
            <h2>🎯 ATS Resume, Cover Letter & Pitch Generator</h2>
            <p style="color:var(--text-sub); margin-bottom:20px; font-size:14px;">Paste any Job Description to generate an ATS-tailored resume, Cover Letter, and Recruiter Email Pitch for USD/EUR remote or visa roles.</p>
            
            <div class="grid-2">
                <div>
                    <label>Job Title</label>
                    <input type="text" id="job_title" placeholder="e.g. Senior Data Engineer / BI Architect">
                    
                    <label>Company Name</label>
                    <input type="text" id="company" placeholder="e.g. Snowflake / Remotive Global">
                    
                    <label>Target Country Standard & Currency</label>
                    <select id="country">
                        <option value="GLOBAL_REMOTE">Global Remote (Worldwide USD Pay)</option>
                        <option value="US">United States (ATS Single/Dual Page)</option>
                        <option value="UK">United Kingdom (CV & Skills Matrix)</option>
                        <option value="EU">European Union / Germany (Visa Sponsorship / EUR)</option>
                    </select>

                    <label>Job Description (JD)</label>
                    <textarea id="jd_text" rows="8" placeholder="Paste full Job Description text here..."></textarea>

                    <button class="btn-primary" onclick="generateTailoredResume()">🚀 Generate Tailored ATS Resume & Pitch</button>
                </div>

                <div>
                    <div id="opt_loading" style="display:none; text-align:center; padding:40px; color:var(--accent-blue);">
                        🧠 Analyzing JD keywords & customizing resume...
                    </div>
                    <div id="opt_results" style="display:none;">
                        <h3 style="color:var(--accent-green); margin-bottom:12px;">✅ Tailored Outputs (Match Score: <span id="res_score">88</span>%)</h3>
                        
                        <label>Extracted ATS Keywords</label>
                        <div id="res_keywords" style="margin-bottom:16px;"></div>

                        <label>Recruiter Cold Email Pitch</label>
                        <pre id="res_email"></pre>

                        <label>Tailored Resume Markdown</label>
                        <pre id="res_resume" style="max-height:300px;"></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 2: LIVE JOB SCOUT -->
    <div id="scout" class="tab-content">
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <div>
                    <h2>📡 Live Global Remote & Visa Sponsorship Job Radar</h2>
                    <p style="color:var(--text-sub); font-size:14px;">Streaming worldwide USD/EUR/GBP remote jobs & visa relocation roles for India-based candidates.</p>
                </div>
                <button class="btn-primary" onclick="scoutJobs()">🔄 Refresh Global Stream</button>
            </div>

            <div id="scout_loading" style="display:none; color:var(--accent-blue); padding:20px;">📡 Querying RemoteOK, Remotive & Arbeitnow Visa portals...</div>
            <div id="job_stream"></div>
        </div>
    </div>

    <!-- TAB 3: APPLICATION TRACKER -->
    <div id="tracker" class="tab-content">
        <div class="glass-card">
            <h2>📊 Application Lifecycle & Recruiter Outreach Tracker</h2>
            <div id="app_stats" style="display:flex; gap:16px; margin:20px 0;"></div>
            <div id="app_list"></div>
        </div>
    </div>

    <!-- TAB 4: LINKEDIN OPTIMIZER -->
    <div id="linkedin" class="tab-content">
        <div class="glass-card">
            <h2>💼 Copy-Paste Optimized LinkedIn Profile Content</h2>
            <p style="color:var(--text-sub); margin-bottom:16px;">Direct copy-paste sections tailored for linkedin.com/in/pradeep-thallapelly-890b17312 to boost inbound recruiter messages.</p>
            
            <label>Optimized Headline (Copy to LinkedIn Headline)</label>
            <pre>Senior AI & Data Engineer | Qlik Sense & Databricks Architect | dbt Core & LLM Systems Lead | Open to Worldwide Remote (USD/EUR) & Visa Sponsorship</pre>

            <label>Optimized About / Summary Section</label>
            <pre>Experienced Senior AI & Data Engineer with 6+ years of expertise designing enterprise data lakehouses, institutional BI dashboard architectures, and autonomous AI agent systems. Certified Qlik Sense Data Architect & Databricks practitioner with a proven track record of migrating complex legacy reporting systems (Qlik/Intellicus) to high-performance dbt Core + Databricks Delta Lake pipelines.

Key Technical Specializations:
• Data Engineering & Analytics: dbt Core (Staging → Marts), Databricks Delta Lake, Snowflake, SQL, PySpark, Data Warehousing.
• Business Intelligence: Qlik Sense (Data Modeling, Set Analysis, NPrinting, QVD Optimization), Power BI, Executive KPI Dashboards.
• AI Engineering & LLM Systems: Autonomous Multi-Agent Swarms, AirLLM 70B layer-wise local inference engines (DeepSeek-R1 70B), FastAPI REST backends, SSE streaming.
• Quantitative Systems: Black-Scholes Options Greeks Engine, Fyers/Zerodha Live Broker OAuth Integration.

Currently seeking Worldwide Remote (USD/EUR/GBP) roles or International Visa Sponsorship opportunities.
Email: pradeep.thallapelly369@outlook.com | GitHub: github.com/pradeepthallapelly369</pre>
        </div>
    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');

            if(tabId === 'scout') scoutJobs();
            if(tabId === 'tracker') loadApplications();
        }

        async function generateTailoredResume() {
            const title = document.getElementById('job_title').value;
            const company = document.getElementById('company').value;
            const country = document.getElementById('country').value;
            const jd = document.getElementById('jd_text').value;

            if(!title || !jd) { alert("Please provide at least a Job Title and Job Description."); return; }

            document.getElementById('opt_loading').style.display = 'block';
            document.getElementById('opt_results').style.display = 'none';

            try {
                const resp = await fetch('/api/optimize-resume', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ job_title: title, company: company, country: country, jd_text: jd })
                });
                const data = await resp.json();

                document.getElementById('opt_loading').style.display = 'none';
                document.getElementById('opt_results').style.display = 'block';

                document.getElementById('res_score').innerText = data.match_score || 88;
                document.getElementById('res_keywords').innerHTML = (data.ats_keywords || []).map(k => `<span class="badge">${k}</span>`).join(' ');
                document.getElementById('res_email').innerText = data.recruiter_email_pitch || '';
                document.getElementById('res_resume').innerText = data.tailored_resume_markdown || '';
            } catch(e) {
                alert("Error optimizing resume: " + e);
                document.getElementById('opt_loading').style.display = 'none';
            }
        }

        async function scoutJobs() {
            document.getElementById('scout_loading').style.display = 'block';
            try {
                const resp = await fetch('/api/jobs/scout');
                const data = await resp.json();
                document.getElementById('scout_loading').style.display = 'none';

                const container = document.getElementById('job_stream');
                container.innerHTML = data.jobs.map(j => `
                    <div class="job-card">
                        <div>
                            <div style="font-weight:700; font-size:16px;">${j.title}</div>
                            <div style="color:var(--text-sub); font-size:13px; margin:4px 0;">${j.company} &bull; 📍 ${j.location} &bull; Source: ${j.source}</div>
                            <div><span class="badge badge-usd">${j.type}</span></div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:18px; font-weight:700; color:var(--accent-green);">${j.match_score}% Match</div>
                            <a href="${j.url}" target="_blank" class="btn-primary" style="display:inline-block; padding:8px 14px; text-decoration:none; margin-top:8px; font-size:12px;">Apply Direct ↗</a>
                        </div>
                    </div>
                `).join('');
            } catch(e) {
                document.getElementById('scout_loading').innerText = "Error fetching jobs: " + e;
            }
        }

        async function loadApplications() {
            try {
                const resp = await fetch('/api/applications');
                const data = await resp.json();

                const statsDiv = document.getElementById('app_stats');
                statsDiv.innerHTML = Object.entries(data.stats).map(([k, v]) => `
                    <div style="background:rgba(255,255,255,0.05); padding:12px 20px; border-radius:8px; border:1px solid var(--card-border);">
                        <div style="font-size:12px; color:var(--text-sub);">${k}</div>
                        <div style="font-size:20px; font-weight:700; color:var(--accent-blue);">${v}</div>
                    </div>
                `).join('');

                const listDiv = document.getElementById('app_list');
                listDiv.innerHTML = data.applications.map(a => `
                    <div class="job-card">
                        <div>
                            <div style="font-weight:700;">${a.title} @ ${a.company}</div>
                            <div style="font-size:12px; color:var(--text-sub);">Status: ${a.status} | Match: ${a.match_score}% | Date: ${a.created_at}</div>
                        </div>
                        <div>
                            <select onchange="updateStatus('${a.id}', this.value)" style="margin:0; padding:6px 12px; width:auto;">
                                <option value="Discovered" ${a.status==='Discovered'?'selected':''}>Discovered</option>
                                <option value="Tailored" ${a.status==='Tailored'?'selected':''}>Tailored</option>
                                <option value="Applied" ${a.status==='Applied'?'selected':''}>Applied</option>
                                <option value="Interview" ${a.status==='Interview'?'selected':''}>Interviewing</option>
                                <option value="Offer" ${a.status==='Offer'?'selected':''}>Offered</option>
                            </select>
                        </div>
                    </div>
                `).join('');
            } catch(e) { console.error(e); }
        }

        async function updateStatus(jobId, newStatus) {
            await fetch('/api/applications/status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ job_id: jobId, status: newStatus })
            });
            loadApplications();
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index_page():
    return HTML_DASHBOARD

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5070)
