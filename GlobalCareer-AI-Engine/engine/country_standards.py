"""
Country-Specific Resume Standards & Formatting Guidelines
Supports: US, UK, EU/Germany, Global Remote
"""

COUNTRY_FORMATS = {
    "GLOBAL_REMOTE": {
        "name": "Global Remote (USD / Worldwide)",
        "target_currency": "USD",
        "length_pages": "1-2 Pages",
        "focus_areas": [
            "Worldwide Remote Delivery & Async Communication",
            "Quantifiable Business Impact ($ Revenue, % Performance Boost)",
            "AI & Data Engineering Core Technical Stack",
            "Self-Directed Execution & System Architecture"
        ],
        "ats_rules": [
            "No graphics, columns, or non-standard tables",
            "Standard headings: Summary, Core Competencies, Experience, Projects, Certifications",
            "Include GitHub & LinkedIn URIs in header"
        ],
        "intro_tag": "Senior AI & Data Engineer specializing in Databricks, dbt, Qlik Sense, and AI Agent systems, seeking Worldwide Remote roles paid in USD."
    },
    "US": {
        "name": "United States (ATS Optimized)",
        "target_currency": "USD",
        "length_pages": "1-2 Pages",
        "focus_areas": [
            "Action-Verb Bullet Points (Architected, Engineered, Optimized, Migrated)",
            "Metric-Driven Outcomes (% Latency Reduction, Data Accuracy, Scale)",
            "Core Technologies Matched Strictly to JD Keywords"
        ],
        "ats_rules": [
            "Exclude Photo, Marital Status, Date of Birth, Full Street Address",
            "Clean single-column ATS layout",
            "Keywords matching Job Description exact phrases"
        ],
        "intro_tag": "Senior Data & AI Engineer with 6+ years of expertise in Databricks, dbt Core, Qlik Sense, and Python LLM infrastructure."
    },
    "UK": {
        "name": "United Kingdom (CV Format)",
        "target_currency": "GBP",
        "length_pages": "2 Pages",
        "focus_areas": [
            "Professional Summary Profile",
            "Key Technical Competencies & Technical Skills Matrix",
            "Commercial Experience & Key Achievements",
            "Education & Professional Qualifications"
        ],
        "ats_rules": [
            "Clear chronological structure",
            "Highlight UK time zone availability (GMT/BST overlap)"
        ],
        "intro_tag": "Accomplished BI & Data Architect with extensive experience delivering enterprise analytics, dbt transformations, and Databricks solutions."
    },
    "EU": {
        "name": "European Union / Germany (Visa Relocation & EU Remote)",
        "target_currency": "EUR",
        "length_pages": "2 Pages",
        "focus_areas": [
            "Structured Technical Skills Matrix",
            "Languages & Professional Qualifications",
            "Visa / Relocation Readiness (Open to EU Blue Card / Relocation)",
            "System Architecture & Engineering Accomplishments"
        ],
        "ats_rules": [
            "Formal and structured formatting",
            "Include work eligibility & relocation status"
        ],
        "intro_tag": "Senior Data & AI Engineer seeking EU Remote or Relocation (EU Blue Card Eligible) with expertise in Databricks, Qlik, and Python AI Systems."
    }
}

def get_country_guidelines(country_code: str = "GLOBAL_REMOTE") -> dict:
    code = country_code.upper()
    return COUNTRY_FORMATS.get(code, COUNTRY_FORMATS["GLOBAL_REMOTE"])
