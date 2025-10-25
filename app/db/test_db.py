# test_db.py
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:d?8p25?DPVJav6g@db.fspykrgstdvyswdnipzg.supabase.co:5432/postgres"
engine = create_engine(DATABASE_URL)

try:
    conn = engine.connect()
    print("✅ Connected to PostgreSQL successfully!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
