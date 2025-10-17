# app/init_db.py
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_PATH = os.getenv("DB_PATH", "nutrition.db")

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# Create tables
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    protein_target INTEGER,
    diet_type TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS meals (
    user_id TEXT,
    date TEXT,
    meal TEXT,
    protein REAL,
    carbs REAL,
    fat REAL
)
""")

conn.commit()
conn.close()

print(f"✅ Database initialized successfully at {DB_PATH}")
