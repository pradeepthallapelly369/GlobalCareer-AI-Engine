"""
Application Tracker — SQLite-backed job pipeline tracker.
"""

import sqlite3
import os
import logging
from datetime import datetime

from config.settings import DB_PATH

logger = logging.getLogger("GlobalCareer")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            region TEXT,
            url TEXT,
            salary TEXT,
            currency TEXT DEFAULT 'USD',
            job_type TEXT,
            match_score INTEGER DEFAULT 75,
            eval_reason TEXT,
            status TEXT DEFAULT 'Discovered',
            source TEXT,
            applied_date TEXT,
            recruiter_contact TEXT,
            cold_email_sent INTEGER DEFAULT 0,
            cold_email_text TEXT,
            notes TEXT,
            tags TEXT,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_time TEXT NOT NULL,
            total_scanned INTEGER,
            total_matched INTEGER,
            portals_active INTEGER,
            portal_stats TEXT,
            duration_seconds REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cold_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT,
            to_email TEXT,
            subject TEXT,
            body TEXT,
            sent_at TEXT,
            status TEXT DEFAULT 'drafted'
        )
    """)
    conn.commit()
    conn.close()

def add_job(job_dict):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    job_id = job_dict.get("id", "")

    cursor.execute("""
        INSERT OR IGNORE INTO applications (
            id, title, company, location, region, url, salary, currency, job_type,
            match_score, eval_reason, status, source, tags, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job_id,
        job_dict.get("title", ""),
        job_dict.get("company", ""),
        job_dict.get("location", ""),
        job_dict.get("region", ""),
        job_dict.get("url", ""),
        job_dict.get("salary", ""),
        "USD",
        job_dict.get("type", "Remote"),
        job_dict.get("match_score", 75),
        job_dict.get("eval_reason", ""),
        "Discovered",
        job_dict.get("source", ""),
        str(job_dict.get("tags", [])),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    ))
    conn.commit()
    conn.close()
    return job_id

def add_jobs_batch(jobs_list):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    added = 0
    for job in jobs_list:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO applications (
                    id, title, company, location, region, url, salary, currency, job_type,
                    match_score, eval_reason, status, source, tags, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.get("id", ""),
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("region", ""),
                job.get("url", ""),
                job.get("salary", ""),
                "USD",
                job.get("type", "Remote"),
                job.get("match_score", 75),
                job.get("eval_reason", ""),
                "Discovered",
                job.get("source", ""),
                str(job.get("tags", [])),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            added += 1
        except Exception:
            pass
    conn.commit()
    conn.close()
    logger.info(f"💾 Saved {added} jobs to database")
    return added

def record_scan(total_scanned, total_matched, portals_active, portal_stats, duration):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    import json
    cursor.execute("""
        INSERT INTO scan_history (scan_time, total_scanned, total_matched, portals_active, portal_stats, duration_seconds)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_scanned,
        total_matched,
        portals_active,
        json.dumps(portal_stats),
        duration,
    ))
    conn.commit()
    conn.close()

def update_status(job_id, status, notes=None):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if status == "Applied":
        cursor.execute("UPDATE applications SET status=?, applied_date=?, notes=? WHERE id=?",
                       (status, datetime.now().strftime("%Y-%m-%d"), notes or "", job_id))
    else:
        cursor.execute("UPDATE applications SET status=?, notes=? WHERE id=?",
                       (status, notes or "", job_id))
    conn.commit()
    conn.close()

def get_all_applications(limit=500):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications ORDER BY match_score DESC, created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT status, COUNT(*) FROM applications GROUP BY status")
    by_status = dict(cursor.fetchall())
    cursor.execute("SELECT region, COUNT(*) FROM applications GROUP BY region ORDER BY COUNT(*) DESC LIMIT 20")
    by_region = dict(cursor.fetchall())
    cursor.execute("SELECT source, COUNT(*) FROM applications GROUP BY source ORDER BY COUNT(*) DESC LIMIT 20")
    by_source = dict(cursor.fetchall())
    cursor.execute("SELECT AVG(match_score) FROM applications")
    avg_score = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM scan_history")
    total_scans = cursor.fetchone()[0]

    conn.close()
    return {
        "total_jobs": total,
        "by_status": by_status,
        "by_region": by_region,
        "by_source": by_source,
        "avg_match_score": round(avg_score, 1),
        "total_scans": total_scans,
    }

def get_scan_history(limit=20):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scan_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
