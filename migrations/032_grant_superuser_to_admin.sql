-- Migration 032: Grant superuser permissions to admin user
-- Date: 2025-11-20
-- Description: One-time script to grant superuser permissions to the admin user

-- Update admin user to be superuser and active
UPDATE users
SET
    is_superuser = TRUE,
    is_active = TRUE,
    updated_at = NOW()
WHERE username = 'admin';

-- Verify the update
SELECT
    id,
    username,
    email,
    is_superuser,
    is_active,
    created_at
FROM users
WHERE username = 'admin';

-- Add comment
COMMENT ON TABLE users IS 'System users with authentication and authorization';
