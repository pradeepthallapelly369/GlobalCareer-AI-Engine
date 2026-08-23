import sqlite3
import os
import uuid
from datetime import datetime

db_path = os.path.expanduser("~/.omniroute/storage.sqlite")
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Check if rule exists
    cur.execute("SELECT id FROM reasoning_routing_rules WHERE id='route_fable'")
    if not cur.fetchone():
        now = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO reasoning_routing_rules 
            (id, name, scope, model_pattern, target_kind, target_model, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ('route_fable', 'Route fable to openrouter', 'model', 'claude-fable-5', 'model', 'openrouter/anthropic/claude-fable-5', now, now))
        conn.commit()
        print("Routing rule for fable added.")
    else:
        print("Routing rule already exists.")
except Exception as e:
    print("Error:", e)
finally:
    if 'conn' in locals():
        conn.close()
