import sqlite3
import os

db_path = os.path.expanduser("~/.omniroute/storage.sqlite")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("UPDATE reasoning_routing_rules SET target_model = 'ollama-local/llama3.1:latest' WHERE id='route_opus_5'")
conn.commit()
print("Updated route_opus_5 target model to ollama-local/llama3.1:latest")
conn.close()
