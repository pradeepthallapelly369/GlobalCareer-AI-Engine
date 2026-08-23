import sqlite3
import os

db_path = os.path.expanduser("~/.omniroute/storage.sqlite")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("UPDATE reasoning_routing_rules SET target_model = 'ollama-local/llama3.1:latest' WHERE id='route_sonnet_to_fable'")
conn.commit()
print("Updated route_sonnet_to_fable target model to ollama-local/llama3.1:latest")
conn.close()
