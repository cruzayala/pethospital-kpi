"""
Register HVC center in Railway PostgreSQL database
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Get Railway database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not found in .env file")
    sys.exit(1)

print("=" * 60)
print("REGISTERING HVC CENTER IN RAILWAY")
print("=" * 60)
print()

# Create engine
engine = create_engine(DATABASE_URL)

# Registration SQL - usando el mismo API key que tiene el backend
sql = """
INSERT INTO centers (code, name, country, city, api_key, is_active, registered_at)
VALUES (
  'HVC',
  'Hospital Veterinario Central',
  'República Dominicana',
  'Santo Domingo',
  'codex-kpi-master-key-2025',
  1,
  NOW()
)
ON CONFLICT (code) DO UPDATE SET
  name = EXCLUDED.name,
  country = EXCLUDED.country,
  city = EXCLUDED.city,
  api_key = EXCLUDED.api_key,
  is_active = EXCLUDED.is_active
RETURNING *;
"""

try:
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        conn.commit()
        row = result.fetchone()

        print("[SUCCESS] HVC center registered successfully in Railway!")
        print()
        print(f"Center details:")
        print(f"  ID: {row[0]}")
        print(f"  Code: {row[1]}")
        print(f"  Name: {row[2]}")
        print(f"  City: {row[3]}")
        print(f"  Active: {row[4]}")
        print(f"  Created: {row[5]}")
        print()
        print("=" * 60)
        print("The center is ready to receive KPI events!")
        print("=" * 60)

except Exception as e:
    print(f"[ERROR] Error registering center: {e}")
    sys.exit(1)
