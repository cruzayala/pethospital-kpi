"""
Quick script to register HVC test center in pethospital_kpi database
"""
import os
import sys
from sqlalchemy import create_engine, text

# Database URL
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/pethospital_kpi"

# Create engine
engine = create_engine(DATABASE_URL)

# Registration SQL
sql = """
INSERT INTO centers (code, name, country, city, api_key, is_active, registered_at)
VALUES (
  'HVC',
  'Hospital Veterinario Central',
  'Republica Dominicana',
  'Santo Domingo',
  'test-api-key-local-HVC-2025',
  1,
  NOW()
)
ON CONFLICT (code) DO UPDATE SET
  api_key = EXCLUDED.api_key,
  name = EXCLUDED.name
RETURNING *;
"""

try:
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        conn.commit()
        row = result.fetchone()
        print("\n[SUCCESS] HVC center registered successfully!")
        print(f"\nCenter details:")
        print(f"  ID: {row[0]}")
        print(f"  Code: {row[1]}")
        print(f"  Name: {row[2]}")
        print(f"  Country: {row[3]}")
        print(f"  City: {row[4]}")
        print(f"  API Key: {row[5]}")
        print(f"  Active: {row[6]}")
        print(f"  Registered: {row[7]}\n")
except Exception as e:
    print(f"\n[ERROR] Error registering center: {e}\n")
    sys.exit(1)
