-- Drop UNIQUE constraint on api_key to allow universal master key
-- This allows all centers to use the same API key for auto-registration

-- Drop the unique constraint
ALTER TABLE centers DROP CONSTRAINT IF EXISTS ix_centers_api_key;

-- Drop the index if it exists
DROP INDEX IF EXISTS ix_centers_api_key;

-- Recreate as a regular index (not unique)
CREATE INDEX IF NOT EXISTS idx_centers_api_key ON centers(api_key);

-- Now update all centers to use master key
UPDATE centers SET api_key = 'codex-kpi-master-key-2025';

-- Verify
SELECT id, code, name, api_key, is_active FROM centers ORDER BY id;
