"""
Application Lifecycle & Job Pipeline Tracker
SQLite-backed database tracking applications, match scores, tailored resumes, and recruiter outreach.
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "applications.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            url TEXT,
            salary TEXT,
            currency TEXT DEFAULT 'USD',
            job_type TEXT,
            match_score INTEGER DEFAULT 75,
            status TEXT DEFAULT 'Discovered',
            applied_date TEXT,
            recruiter_contact TEXT,
            notes TEXT,
            tailored_resume TEXT,
            cover_letter TEXT,
            email_pitch TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_or_update_job(job_dict):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    job_id = job_dict.get("id") or f"job_{hash(job_dict.get('title', '') + job_dict.get('company', ''))}"

    cursor.execute("""
        INSERT INTO applications (
            id, title, company, location, url, salary, currency, job_type, match_score, status, applied_date, recruiter_contact, notes, tailored_resume, cover_letter, email_pitch, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            company=excluded.company,
            location=excluded.location,
            url=excluded.url,
            match_score=excluded.match_score
    """, (
        job_id,
        job_dict.get("title", "Untitled Role"),
        job_dict.get("company", "Unknown Company"),
        job_dict.get("location", "Worldwide Remote"),
        job_dict.get("url", ""),
        job_dict.get("salary", "$60K-$120K USD"),
        job_dict.get("currency", "USD"),
        job_dict.get("type", "Remote (USD/Worldwide)"),
        job_dict.get("match_score", 85),
        job_dict.get("status", "Discovered"),
        job_dict.get("applied_date", ""),
        job_dict.get("recruiter_contact", ""),
        job_dict.get("notes", ""),
        job_dict.get("tailored_resume", ""),
        job_dict.get("cover_letter", ""),
        job_dict.get("email_pitch", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
    return job_id

def update_application_status(job_id, status, applied_date=None, notes=None):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if applied_date is None and status == "Applied":
        applied_date = datetime.now().strftime("%Y-%m-%d")

    query = "UPDATE applications SET status = ?"
    params = [status]
    if applied_date:
        query += ", applied_date = ?"
        params.append(applied_date)
    if notes:
        query += ", notes = ?"
        params.append(notes)
    
    query += " WHERE id = ?"
    params.append(job_id)

    cursor.execute(query, params)
    conn.commit()
    conn.close()

def get_all_applications():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications ORDER BY match_score DESC, created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_application_stats():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
    rows = cursor.fetchall()
    conn.close()

    stats = {
        "Total Discovered": 0,
        "Applied": 0,
        "Screening": 0,
        "Interview": 0,
        "Offer": 0
    }
    for status, count in rows:
        stats[status] = count
    return stats
