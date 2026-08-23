import sqlite3
import os

db_path = os.path.expanduser("~/.omniroute/storage.sqlite")
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Check if table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_capabilities'")
    if cur.fetchone():
        print("Updating model capabilities...")
        cur.execute("UPDATE model_capabilities SET supports_thinking = 1")
        conn.commit()
        print("Updated successfully!")
    else:
        print("Table model_capabilities not found.")
except Exception as e:
    print(f"Error: {e}")
