import sqlite3
import os

db_path = 'd:/SuraSmart_Project/backend/data/db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

relevant_tables = [
    'facial_recognition_missingperson',
    'facial_recognition_facialrecognitionimage'
]

for table in relevant_tables:
    if table in tables:
        print(f"\n--- Schema for {table} ---")
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"{col[1]} ({col[2]})")
    else:
        print(f"\nTable {table} NOT found.")

# Also list all tables starting with 'facial' or 'users'
print("\n--- Relevant tables ---")
for t in sorted(tables):
    if t.startswith(('facial', 'users')):
        print(t)

conn.close()
