<div align="center">

# 🌐 GlobalCareer AI Engine: Worldwide Remote & Visa Job AutoOps

### *Autonomous Career Intelligence, JD-Based ATS Resume Optimizer, and Foreign Currency (USD/EUR/GBP) Job Scout Platform*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI%20Optimization-7C3AED?style=for-the-badge)](https://openrouter.ai)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

</div>

---

## 📌 Project Overview

**GlobalCareer-AI-Engine** is an enterprise-grade autonomous job application and career intelligence platform designed specifically for Senior AI Engineers, Data Engineers, and Qlik/Databricks Architects seeking **Worldwide Remote (USD / EUR / GBP / AUD / CAD)** or **International Relocation / Visa Sponsorship** opportunities while based in India.

The platform unites **JD-based ATS Resume Customization**, **Cold Recruiter Email Pitch Generation**, **Live Multi-Portal Job Scouting**, and an **Application Lifecycle Tracker** in a single glassmorphic desktop web application.

---

## ⚡ System Architecture

```mermaid
flowchart TD
    User([🖥️ Candidate Dashboard :5060]) -->|Paste JD| ResOpt[🎯 AI Resume & Pitch Customizer]
    User -->|Stream Stream| JobRadar[📡 Global Remote & Visa Job Radar]
    User -->|Manage Pipeline| Tracker[📊 SQLite Application Lifecycle Tracker]

    subgraph LLM Customization Layer
        ResOpt -->|Query OpenRouter / Groq| LLM[🧠 OpenRouter Free LLMs / Llama 3.3 & Gemma 3]
        LLM -->|Tailored Resume & Email| ResOpt
    end

    subgraph Job Scouting Engine
        JobRadar --> Remotive[🌐 Remotive API / USD Remote]
        JobRadar --> RemoteOK[🚀 RemoteOK API / Global]
        JobRadar --> Arbeitnow[🇪🇺 Arbeitnow API / EU Visa Sponsorship]
    end

    subgraph Storage & Tracking
        ResOpt & JobRadar --> DB[(💾 applications.db / SQLite)]
        DB --> Tracker
    end
```

---

## 🔑 Key Capabilities

1. 🎯 **JD-Based ATS Resume Customizer**:
   - Paste any Job Description to generate ATS-optimized resume bullet points, extracted target keywords, and match score (0-100%).
   - Supports country-specific formatting standards: **US (ATS Focus)**, **UK (CV & Skills Matrix)**, **EU / Germany (Visa Relocation & Europass)**, and **Global Remote (USD)**.
2. ✉️ **Recruiter Pitch & Cover Letter Generator**:
   - Generates personalized recruiter cold emails targeting foreign currency compensation ($60K–$120K+ USD).
3. 📡 **Live Global Job Radar**:
   - Real-time job stream fetching RemoteOK, Remotive, and Arbeitnow EU Visa jobs.
   - Automatically filters out low-pay INR-only local roles.
4. 📊 **Application Lifecycle Kanban & Tracker**:
   - SQLite-backed pipeline tracking status from `Discovered` → `Tailored` → `Applied` → `Interviewing` → `Offered`.
5. 💼 **LinkedIn Profile Optimizer**:
   - Pre-formatted copy-paste headline, executive summary, and experience bullet points for [linkedin.com/in/pradeep-thallapelly-890b17312](https://linkedin.com/in/pradeep-thallapelly-890b17312).

---

## 🛠️ Quickstart Guide

### 1. Clone & Setup Environment

```bash
git clone https://github.com/pradeepthallapelly369/GlobalCareer-AI-Engine.git
cd GlobalCareer-AI-Engine

pip install -r requirements.txt
```

### 2. Launch Dashboard

```bash
chmod +x launch_career_engine.sh
./launch_career_engine.sh
```

- **Dashboard UI**: `http://localhost:5060`

---

## 👤 Author & Maintainer

**Pradeep Thallapelly**  
*Senior AI & Data Engineer / Analytics Engineering Lead*  
- 💼 **LinkedIn**: [linkedin.com/in/pradeep-thallapelly-890b17312](https://linkedin.com/in/pradeep-thallapelly-890b17312)  
- 📧 **Email**: [pradeep.thallapelly369@outlook.com](mailto:pradeep.thallapelly369@outlook.com)  
- 🐙 **GitHub**: [@pradeepthallapelly369](https://github.com/pradeepthallapelly369)
