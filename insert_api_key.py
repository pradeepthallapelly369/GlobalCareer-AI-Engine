import sqlite3
import os
import uuid
import hashlib
from datetime import datetime

db_path = os.path.expanduser("~/.omniroute/storage.sqlite")
key = "sk-ant-api03-dummy-key-for-local-routing-to-work-properly-with-omniroute-AAAAAAAAAAAAAAAAAAAAAAA"
key_id = "key_" + uuid.uuid4().hex[:12]
now = datetime.now().isoformat()
key_hash = hashlib.sha256(key.encode()).hexdigest()

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO api_keys (id, name, key, key_hash, created_at) VALUES (?, ?, ?, ?, ?)", 
                (key_id, "Local Dummy Key", key, key_hash, now))
    conn.commit()
    print("API Key inserted.")
except Exception as e:
    print("Error:", e)
finally:
    if 'conn' in locals():
        conn.close()
