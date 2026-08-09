"""
AI Resume & Cover Letter Customizer Engine
Tailors ATS resumes and cold recruiter emails based on Job Description (JD) & Target Country.
"""
import os
import json
try:
    import yaml
except ImportError:
    yaml = None

import requests
from engine.country_standards import get_country_guidelines

# Load Master Dossier
DOSSIER_PATH = os.path.join(os.path.dirname(__file__), "..", "profile", "pradeep_master_dossier.yaml")

def load_master_dossier():
    if yaml is not None and os.path.exists(DOSSIER_PATH):
        try:
            with open(DOSSIER_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception:
            pass
    return {
        "candidate": {
            "name": "Pradeep Thallapelly",
            "title": "Senior AI & Data Engineer / Analytics Engineering Lead",
            "email": "pradeep.thallapelly369@outlook.com",
            "linkedin": "https://linkedin.com/in/pradeep-thallapelly-890b17312",
            "github": "https://github.com/pradeepthallapelly369",
            "location": "Hyderabad, India (Open to Worldwide Remote & Visa Sponsorship)"
        }
    }

def call_openrouter_llm(prompt: str, system_prompt: str = "You are an elite executive career strategist and ATS resume optimization expert.") -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/pradeepthallapelly369/GlobalCareer-AI-Engine",
        "X-Title": "GlobalCareer-AI-Engine"
    }

    models_to_try = [
        "google/gemma-3-27b-it:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen-2.5-72b-instruct:free"
    ]

    last_error = None
    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
            elif resp.status_code in (429, 503):
                last_error = f"HTTP {resp.status_code} rate limit"
                continue
            else:
                last_error = f"HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            last_error = str(e)

    raise RuntimeError(f"All LLM models failed. Last error: {last_error}")

def optimize_resume_for_jd(job_title: str, company: str, jd_text: str, country: str = "GLOBAL_REMOTE") -> dict:
    """
    Generates a tailored ATS resume, cover letter, and recruiter pitch email for a specific JD.
    """
    dossier = load_master_dossier()
    country_info = get_country_guidelines(country)

    dossier_str = yaml.dump(dossier, default_flow_style=False) if yaml is not None else json.dumps(dossier, indent=2)
    prompt = f"""
CANDIDATE MASTER DOSSIER:
{dossier_str}

TARGET COUNTRY / FORMATTING GUIDELINES:
{json.dumps(country_info, indent=2)}

TARGET JOB:
Job Title: {job_title}
Company: {company}
Country Target: {country}
Job Description (JD):
{jd_text[:4000]}

TASK:
1. Extract top 10 ATS keywords from the JD.
2. Tailor a high-impact, ATS-optimized markdown resume for candidate Pradeep Thallapelly, highlighting matching skills (dbt, Databricks, Qlik Sense, Python, FastAPI, AI Agents, SQL) and metrics ($/latency/% accuracy).
3. Create a compelling, professional Cover Letter.
4. Create a concise 3-paragraph Recruiter Cold Pitch Email targeting foreign currency pay ({country_info.get('target_currency', 'USD')}) or Visa Sponsorship.

Respond strictly in valid JSON with key names:
"ats_keywords": ["kw1", "kw2", ...],
"match_score": 85,
"tailored_resume_markdown": "Full Markdown Resume Here...",
"cover_letter_markdown": "Full Markdown Cover Letter Here...",
"recruiter_email_pitch": "Full Email Pitch Here..."
"""

    try:
        raw_response = call_openrouter_llm(prompt)
        # Clean markdown codeblocks if wrapped
        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()

        parsed = json.loads(clean_json)
        return {
            "status": "success",
            "job_title": job_title,
            "company": company,
            "country": country,
            "ats_keywords": parsed.get("ats_keywords", []),
            "match_score": parsed.get("match_score", 85),
            "tailored_resume_markdown": parsed.get("tailored_resume_markdown", ""),
            "cover_letter_markdown": parsed.get("cover_letter_markdown", ""),
            "recruiter_email_pitch": parsed.get("recruiter_email_pitch", "")
        }
    except Exception as e:
        # Fallback generator if LLM fails or is rate limited
        return generate_heuristic_resume(job_title, company, jd_text, country_info, dossier, str(e))

def generate_heuristic_resume(job_title, company, jd_text, country_info, dossier, error_msg=""):
    name = dossier["candidate"].get("name", "Pradeep Thallapelly")
    email = dossier["candidate"].get("email", "pradeep.thallapelly369@outlook.com")
    phone = dossier["candidate"].get("phone", "+91-8886551138")
    linkedin = dossier["candidate"].get("linkedin", "https://linkedin.com/in/pradeep-thallapelly-890b17312")
    github = dossier["candidate"].get("github", "https://github.com/pradeepthallapelly369")

    resume_md = f"""# {name}
**Senior BI Developer | Data Engineer | Technical Lead — Remote / Distributed Teams**
{phone} | {email} | {linkedin} | {github} | Hyderabad, India (Open to Remote — Global / Overlap with US & EU hours)

---

## 🎯 Professional Summary
Senior BI Developer and Data Engineer with 6+ years delivering enterprise analytics solutions for banking, insurance and service clients — including a UK banking client — using Qlik Sense, SQL, dbt, GitHub and Databricks. Currently Technical Lead on an end-to-end Qlik-to-Power BI/Databricks migration, owning validation through dbt tests and AI-agent-assisted data reconciliation. Delivered 100+ production dashboards, ~30% performance improvement, and 20% data redundancy reduction. Experienced working across distributed, cross-time-zone teams.

---

## 🛠️ Core Skills
- **BI Development**: Qlik Sense (Dashboard Design, Data Modeling, Scripting, Set Analysis, QVD Creation, Security Rules, Performance Optimization), NPrinting, Ad-hoc Reporting, KPI Dashboards, Figma-to-BI UX Implementation, Power BI (migration target platform).
- **Data Engineering & ETL**: SQL, Databricks, dbt (modular modeling, schema tests, data quality checks), ETL/ELT Pipeline Design, Incremental Loads, Data Transformations, Data Warehousing, Agentic AI, MCP Servers, Data Reconciliation & Governance.
- **Databases & Big Data**: MS SQL Server, Oracle, Hadoop, Hive — Star Schema, Snowflake Schema, Fact & Dimension Tables.
- **Delivery & Collaboration**: Stakeholder Requirements Gathering, Solution Design, BRD & FRS Documentation, Git, GitHub, VS Code, JIRA, Confluence, ServiceNow, Agile (Scrum/Kanban).

---

## 💼 Professional Experience

### Technical Lead | Data Engineer — IFINGlobal Group *(Sep 2025 – Present)*
- Own the end-to-end Qlik Sense to Databricks SQL migration, converting load scripts and business logic into modular dbt SQL models validated through dbt tests, AI Agents and data reconciliation.
- Built reusable dbt models in VS Code following staging/intermediate/marts layering, and integrated AI agents/MCP servers to auto-detect data mismatches — accelerating reconciliation cycles.
- Managed Git/GitHub version control, code reviews, and Agile sprint delivery with full migration documentation for stakeholder governance.

### Business Intelligence Engineer — Exponentia.ai *(Jan 2025 – Sep 2025)*
- **Migration to Qlik Sense (Mar-Sep 2025)**: Migrated 20+ legacy dashboards to Qlik Sense, partnering with stakeholders to define KPIs and translating Figma designs into production-ready applications.
- **Insurance Data Insights (Jan-Feb 2025)**: Built multi-source dashboards tracking insurance policy performance and claims metrics, automating manual Excel-based reporting workflows.

### Consultant — BI Developer — VRJ Technologies Pvt. Ltd. *(Jun 2020 – Sep 2024)*
- **Financial Data Reporting & Analysis — UK Banking Client**: Designed and developed 100+ enterprise Qlik Sense dashboards, improving application performance by ~30% and supporting governance across banking analytics.
- Reduced data redundancy by 20% through schema redesign, improving compliance and report accuracy across loan portfolio analytics; implemented NPrinting for automated report scheduling.
- Acted as Business Analyst leading stakeholder requirements gathering and BRD/FRS documentation; mentored junior developers with hands-on Hadoop/Hive/Impala exposure.

---

## 🎓 Certifications & Education
- Qlik Sense Data Architect Qualification (2025)
- Qlik Sense Business Analyst Qualification (2025)
- Databricks Fundamentals — Academy Accreditation
- Generative AI & AI Agent Fundamentals — Academy Accreditation
- Applied AI Tooling for Engineering Workflows (Claude Code)
- **Bachelor of Arts in Economics** — Kakatiya University
"""

    cover_letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the **{job_title}** role at **{company}**. With over 6 years of experience as a Senior BI Developer and Data Engineer, I have built and optimized 100+ enterprise analytics dashboards for UK banking, insurance, and service clients, while leading major migrations from legacy BI to modern dbt Core + Databricks lakehouse architectures.

Currently as Technical Lead at IFINGlobal Group, I own the end-to-end migration of Qlik Sense load scripts into modular dbt SQL models on Databricks, incorporating AI-agent-assisted data reconciliation (via MCP servers) to ensure 100% data fidelity. My work has delivered a 30% performance boost and a 20% reduction in data redundancy across enterprise reporting systems.

I thrive in remote, cross-time-zone environments with overlap in US/EU working hours, and I am excited to bring my analytics engineering and AI agent expertise to your team.

Thank you for your consideration.

Sincerely,
Pradeep Thallapelly
{phone} | {email}
{linkedin}
"""

    email_pitch = f"""Subject: Application: {job_title} — Pradeep Thallapelly (Senior BI Developer & Data Engineer)

Hi Hiring Team at {company},

I am reaching out regarding the {job_title} opening. 

I am a Senior BI Developer & Data Engineer with 6+ years of experience delivering enterprise analytics for banking and financial clients (including a major UK banking client).

Key Highlights from my background:
1. Technical Lead on Qlik-to-Databricks/Power BI migrations using dbt SQL models, schema tests, and AI-agent data reconciliation.
2. Built 100+ production Qlik Sense dashboards, improving performance by ~30% and reducing redundancy by 20%.
3. Certified Qlik Sense Data Architect (2025) & Databricks practitioner with expertise in SQL, PySpark, Python, and Agentic AI.

Resume & GitHub Portfolio: https://github.com/pradeepthallapelly369
LinkedIn: {linkedin}

I am open to full-time remote ({country_info.get('target_currency', 'USD')}) or contract engagements with international teams. I would welcome a brief 10-minute introduction call.

Best regards,
Pradeep Thallapelly
{phone} | {email}
"""

    return {
        "status": "success_fallback",
        "job_title": job_title,
        "company": company,
        "country": country_info.get("name", "Global Remote"),
        "ats_keywords": ["dbt Core", "Databricks", "Qlik Sense", "Python", "SQL", "FastAPI", "Data Lakehouse"],
        "match_score": 88,
        "tailored_resume_markdown": resume_md,
        "cover_letter_markdown": cover_letter,
        "recruiter_email_pitch": email_pitch,
        "note": f"Generated via structured engine. ({error_msg})" if error_msg else ""
    }
