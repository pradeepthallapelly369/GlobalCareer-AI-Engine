"""
Central Configuration — GlobalCareer-AI-Engine
All settings, API keys, thresholds, and runtime parameters.
"""
import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# ── API Keys ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# ── Email Configuration ──────────────────────────────────────────────────────
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "depradeep64@gmail.com")
SMTP_APP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD", "")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL", "pradeep.thallapelly369@outlook.com")

# ── Telegram ─────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ── Candidate Profile ────────────────────────────────────────────────────────
CANDIDATE = {
    "name": "Pradeep Thallapelly",
    "title": "Senior BI Developer | Data Engineer | Technical Lead",
    "email": "pradeep.thallapelly369@outlook.com",
    "phone": "+91-8886551138",
    "linkedin": "https://linkedin.com/in/pradeep-thallapelly-890b17312",
    "github": "https://github.com/pradeepthallapelly369",
    "portfolio": "https://pradeepthallapelly369.github.io",
    "location": "Hyderabad, India",
    "availability": "Open to Remote — Global / Overlap with US & EU hours",
    "experience_years": 6,
    "target_package_usd": 35000,  # Min 30L INR
    "target_package_range": "Min 30 Lakhs INR ($35K+ USD)",
}

# ── Job Search Parameters ────────────────────────────────────────────────────
MATCH_THRESHOLD = 70  # Minimum match score to keep a job
MAX_JOBS_PER_SCAN = 500  # Max jobs to process per scan cycle
HOURS_OLD_THRESHOLD = 96  # Look at jobs posted in last 96 hours
JOBSPY_RESULTS_PER_QUERY = 15  # Results per jobspy query

# ── Scheduling ───────────────────────────────────────────────────────────────
SCAN_SCHEDULE_IST = [
    "06:00",  # Morning — catch US evening posts
    "12:00",  # Midday — catch EU morning posts  
    "18:00",  # Evening — catch US morning posts
    "23:00",  # Night — catch AU/NZ/Asia posts
]

# ── Foreign Currency Filter ──────────────────────────────────────────────────
# All major world currencies that convert favorably to INR (1 unit > ~10 INR)
FOREIGN_CURRENCIES = [
    # Major reserve currencies
    "USD", "EUR", "GBP", "AUD", "CAD", "CHF", "SGD", "AED",
    # European currencies (non-Euro)
    "SEK", "NOK", "DKK", "PLN", "CZK", "HUF", "RON", "BGN", "HRK", "ISK",
    # Asia-Pacific
    "JPY", "HKD", "KRW", "TWD", "MYR", "THB", "IDR", "PHP", "VND", "INR",
    # Middle East
    "SAR", "QAR", "BHD", "OMR", "KWD", "JOD", "LBP", "ILS",
    # Americas
    "MXN", "BRL", "ARS", "CLP", "COP", "PEN", "UYU",
    # Others
    "NZD", "ZAR", "TRY", "RUB", "CNY", "MAD", "EGP", "NGN", "KES", "GHS"
]

REJECT_KEYWORDS = [
    "onsite india", "india only",
    "work from office india", "hyderabad onsite", "bangalore onsite",
    "pune onsite", "mumbai onsite", "chennai onsite", "noida onsite",
    "gurgaon onsite", "delhi onsite", "10 lpa", "15 lpa", "20 lpa", "25 lpa",
    "30 lpa", "35 lpa", "5 lpa", "6 lpa", "7 lpa", "8 lpa", "9 lpa",
    "indian rupee", "inr only", "local salary", "india salary", "onsite required"
]

# ── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
DB_PATH = os.path.join(DATA_DIR, "applications.db")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
