-- Migration 031: Fix system_config duplicate rows
-- Date: 2025-11-20
-- Description: Remove duplicate rows and ensure only one config row exists

-- Step 1: Delete duplicate rows, keep only the first one
DELETE FROM system_config
WHERE id NOT IN (
    SELECT MIN(id) FROM system_config
);

-- Step 2: Add a constraint to ensure only one row can exist
-- We'll use a CHECK constraint with a subquery
ALTER TABLE system_config
ADD CONSTRAINT single_config_row
CHECK ((SELECT COUNT(*) FROM system_config) <= 1);

-- Step 3: If no config exists, insert default
INSERT INTO system_config (company_name, company_address, company_phone, company_email, timezone, language, theme)
SELECT 'PetHospital KPI', '', '', 'info@pethospital-kpi.com', 'America/Santo_Domingo', 'es', 'light'
WHERE NOT EXISTS (SELECT 1 FROM system_config);

-- Add comment
COMMENT ON CONSTRAINT single_config_row ON system_config IS 'Ensures only one system configuration row exists';
