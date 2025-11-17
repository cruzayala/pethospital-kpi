-- Register Test Center in KPI Database
-- Run this after the KPI service has started (so tables are created)

-- First, generate an API key:
-- In Python: import secrets; print(secrets.token_urlsafe(32))
-- Or use this test key: test-api-key-local-HVC-2025

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
  name = EXCLUDED.name;

SELECT * FROM centers WHERE code = 'HVC';
