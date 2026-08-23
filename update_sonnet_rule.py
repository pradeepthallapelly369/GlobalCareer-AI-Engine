import sqlite3
import os
from datetime import datetime

db_path = os.path.expanduser("~/.omniroute/storage.sqlite")
now = datetime.now().isoformat()

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reasoning_routing_rules 
        (id, name, scope, model_pattern, target_kind, target_model, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, ('route_sonnet_to_fable', 'Route sonnet to fable', 'model', 'claude-3-5-sonnet-20241022', 'model', 'openrouter/anthropic/claude-fable-5', now, now))
    conn.commit()
    print("Routing rule for sonnet to fable added.")
except Exception as e:
    print("Error:", e)
finally:
    if 'conn' in locals():
        conn.close()
