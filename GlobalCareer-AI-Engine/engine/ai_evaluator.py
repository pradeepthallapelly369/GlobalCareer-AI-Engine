"""
AI Job Evaluator — LLM + Heuristic scoring for job matching.
Uses OpenRouter (free) → Groq fallback → Heuristic fallback.
"""

import os
import json
import requests
import logging
from pydantic import BaseModel

from config.settings import CANDIDATE, REJECT_KEYWORDS, FOREIGN_CURRENCIES
from config.search_queries import PREMIUM_MATCH_KEYWORDS, CORE_SKILLS_KEYWORDS

logger = logging.getLogger("GlobalCareer")

class EvalResult(BaseModel):
    is_match: bool
    score: int
    reason: str

# ── Candidate Profile for LLM ────────────────────────────────────────────────
CANDIDATE_PROFILE = f"""
Candidate: {CANDIDATE['name']}
Location: {CANDIDATE['location']}
Experience: {CANDIDATE['experience_years']}+ years
Target Compensation: {CANDIDATE['target_package_range']}

Core Skills:
- Qlik Sense (Dashboard Design, Data Modeling, Set Analysis, QVD Creation, Security Rules, Performance Optimization, NPrinting)
- QlikView development
- Power BI (migration target platform)
- SQL, MS SQL Server, Oracle, Hadoop, Hive, Snowflake, Star Schema, Fact & Dimension Tables
- Databricks, dbt (modular modeling, schema tests, data quality checks)
- ETL/ELT Pipeline Design, Incremental Loads, Data Warehousing
- Data Migration & Reconciliation (AI-assisted)
- Python, PySpark, FastAPI, AI Agents, MCP Servers
- Git, GitHub, JIRA, Confluence, Agile (Scrum/Kanban)

Certifications:
- Qlik Sense Data Architect Qualification (2025)
- Qlik Sense Business Analyst Qualification (2025)
- Databricks Fundamentals
- Generative AI & AI Agent Fundamentals

MANDATORY Requirements (must meet AT LEAST ONE):
1. Fully Remote (Work From Home / Work From Anywhere) — with pay at least 30L INR or in foreign currency (USD, GBP, EUR, AUD, CAD, SGD, AED, etc.)
2. Offers Visa Sponsorship to relocate internationally

REJECT if:
- India onsite with salary strictly less than 30 Lakhs INR
- No remote option (no work from anywhere) and no visa sponsorship
"""

# ── OpenRouter Free Models ───────────────────────────────────────────────────
_free_models_cache = None

def _get_free_models():
    global _free_models_cache
    if _free_models_cache is not None:
        return _free_models_cache
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return []
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            free_list = []
            for m in data.get("data", []):
                pricing = m.get("pricing", {})
                if str(pricing.get("prompt")) == "0" and str(pricing.get("completion")) == "0":
                    model_id = m.get("id", "")
                    if any(x in model_id.lower() for x in ["lyria", "clip", "imagen", "flux", "audio"]):
                        continue
                    free_list.append(model_id)
            priority = ["google", "meta-llama", "qwen", "mistralai"]
            def sort_key(mid):
                prefix = mid.split('/')[0]
                try:
                    return priority.index(prefix)
                except ValueError:
                    return len(priority)
            free_list.sort(key=sort_key)
            _free_models_cache = free_list
            return free_list
    except Exception:
        pass
    return []

# ── LLM Evaluation ──────────────────────────────────────────────────────────
_use_heuristic_only = False

def _evaluate_via_llm(prompt):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("No API key")

    models = _get_free_models()
    fallback = ["google/gemma-3-27b-it:free", "meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen-2.5-72b-instruct:free"]
    models_to_try = models[:5] if models else fallback

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/pradeepthallapelly369/GlobalCareer-AI-Engine",
        "X-Title": "GlobalCareer-AI-Engine",
    }
    for model in models_to_try:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }
        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                    if content:
                        parsed = json.loads(content)
                        return EvalResult(
                            is_match=parsed.get("is_match", False),
                            score=parsed.get("score", 50),
                            reason=parsed.get("reason", "No reason.")
                        )
            elif resp.status_code in (429, 503):
                continue
        except Exception:
            continue
    raise RuntimeError("All LLM models failed")

# ── Heuristic Evaluation ────────────────────────────────────────────────────
def _evaluate_heuristic(job_dict):
    title = str(job_dict.get("title", "")).lower()
    company = str(job_dict.get("company", "")).lower()
    location = str(job_dict.get("location", "")).lower()
    desc = str(job_dict.get("description", "")).lower()
    salary = str(job_dict.get("salary", "")).lower()
    full_text = f"{title} {company} {location} {desc} {salary}"

    # Score components
    score = 0
    reasons = []

    # Skill matching
    premium_match = sum(1 for kw in PREMIUM_MATCH_KEYWORDS if kw in full_text)
    skill_match = sum(1 for kw in CORE_SKILLS_KEYWORDS if kw in full_text)

    if premium_match >= 2:
        score += 40
        reasons.append(f"{premium_match} premium skills matched")
    elif premium_match == 1:
        score += 25
        reasons.append(f"1 premium skill matched")
    elif skill_match >= 3:
        score += 20
        reasons.append(f"{skill_match} core skills matched")
    elif skill_match >= 1:
        score += 10
        reasons.append(f"{skill_match} skill(s) matched")
    else:
        return EvalResult(is_match=False, score=5, reason="No relevant skills found in job posting.")

    # Remote/Visa check
    is_remote = any(kw in full_text for kw in ["remote", "work from home", "wfh", "anywhere", "worldwide", "distributed", "work from anywhere"])
    is_visa = any(kw in full_text for kw in ["visa sponsorship", "relocation", "h1b", "sponsor", "work permit", "visa"])
    has_foreign_pay = any(c.lower() in full_text for c in FOREIGN_CURRENCIES) or any(s in full_text for s in ["$", "£", "€", "usd", "eur", "gbp"])

    if is_remote:
        score += 25
        reasons.append("Remote position")
    if is_visa:
        score += 20
        reasons.append("Visa sponsorship")
    if has_foreign_pay:
        score += 15
        reasons.append("Foreign currency pay")

    # Title relevance boost
    title_keywords = ["data engineer", "bi developer", "business intelligence", "qlik", "databricks",
                       "dbt", "analytics engineer", "data migration", "bi engineer", "etl",
                       "data architect", "technical lead", "senior"]
    title_matches = sum(1 for kw in title_keywords if kw in title)
    if title_matches >= 2:
        score += 15
        reasons.append(f"Strong title match ({title_matches} keywords)")
    elif title_matches == 1:
        score += 8
        reasons.append("Partial title match")

    # Rejection check
    if _is_rejected_text(full_text):
        if not is_remote and not is_visa:
            return EvalResult(is_match=False, score=10, reason="India-only/INR role without remote or visa.")

    is_match = score >= 50
    reason = "; ".join(reasons) if reasons else "Low relevance."
    return EvalResult(is_match=is_match, score=min(score, 100), reason=reason)

def _is_rejected_text(text):
    return any(kw in text for kw in REJECT_KEYWORDS)

# ── Main Evaluator ───────────────────────────────────────────────────────────
def evaluate_job(job_dict):
    global _use_heuristic_only
    title = job_dict.get("title", "")
    desc = job_dict.get("description", "")[:3000]

    # Fast heuristic if LLM disabled or no description
    if _use_heuristic_only or not desc or len(desc) < 50:
        return _evaluate_heuristic(job_dict)

    prompt = f"""You are an expert technical recruiter. Evaluate this job for candidate:

{CANDIDATE_PROFILE}

JOB POSTING:
Title: {title}
Company: {job_dict.get('company', '')}
Location: {job_dict.get('location', '')}
Salary: {job_dict.get('salary', 'Not specified')}
Description:
{desc}

TASK: Rate match quality (0-100) and decide if this is a good match.
A job PASSES if:
1. It involves Data Engineering, BI, Qlik, Databricks, dbt, SQL, ETL, Analytics, or Data Migration skills
2. It is remote (Work From Anywhere) paying at least 30L INR / foreign currency OR offers visa sponsorship/relocation

Respond in JSON: {{"is_match": true/false, "score": 0-100, "reason": "one sentence"}}"""

    try:
        return _evaluate_via_llm(prompt)
    except Exception as e:
        logger.debug(f"LLM eval failed ({e}), using heuristics")
        _use_heuristic_only = True
        return _evaluate_heuristic(job_dict)

def filter_and_score_jobs(jobs_list, threshold=50):
    """Filter and score all jobs. Returns (matched, total_evaluated)."""
    matched = []
    total = len(jobs_list)
    logger.info(f"📊 Evaluating {total} jobs...")

    for idx, job in enumerate(jobs_list):
        if (idx + 1) % 50 == 0:
            logger.info(f"  Progress: {idx+1}/{total}")
        result = evaluate_job(job)
        if result.is_match and result.score >= threshold:
            job["match_score"] = result.score
            job["eval_reason"] = result.reason
            matched.append(job)

    # Sort by score descending
    matched.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    logger.info(f"✅ {len(matched)}/{total} jobs passed (threshold: {threshold})")
    return matched
