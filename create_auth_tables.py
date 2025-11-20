"""
Create authentication tables in Railway PostgreSQL database
Run this after create_tables.py to add user authentication
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

print("=" * 80)
print("CREATING AUTHENTICATION TABLES IN RAILWAY")
print("=" * 80)
print()

# Create engine
engine = create_engine(DATABASE_URL)

# SQL script for auth tables
sql_script = """
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_superuser BOOLEAN NOT NULL DEFAULT false,
    email_verified BOOLEAN NOT NULL DEFAULT false,
    center_id INTEGER REFERENCES centers(id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_center_id ON users(center_id);

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);

-- Create permissions table
CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(255),
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_permissions_name ON permissions(name);
CREATE INDEX IF NOT EXISTS idx_permissions_resource ON permissions(resource);

-- Create user_roles junction table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Create role_permissions junction table
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- Insert default roles
INSERT INTO roles (name, description) VALUES
    ('admin', 'Full system administrator with all permissions'),
    ('analyst', 'Data analyst with read and export permissions'),
    ('viewer', 'Read-only access to dashboards'),
    ('center_manager', 'Manager with permissions for specific center')
ON CONFLICT (name) DO NOTHING;

-- Insert default permissions
INSERT INTO permissions (name, description, resource, action) VALUES
    -- Dashboard permissions
    ('view_dashboard', 'View main dashboard', 'dashboard', 'view'),

    -- Analytics permissions
    ('view_analytics', 'View analytics and reports', 'analytics', 'view'),
    ('export_analytics', 'Export analytics data', 'analytics', 'export'),

    -- User management permissions
    ('view_users', 'View user list', 'users', 'view'),
    ('create_users', 'Create new users', 'users', 'create'),
    ('update_users', 'Update user information', 'users', 'update'),
    ('delete_users', 'Delete users', 'users', 'delete'),

    -- Center management permissions
    ('view_centers', 'View centers list', 'centers', 'view'),
    ('create_centers', 'Register new centers', 'centers', 'create'),
    ('update_centers', 'Update center information', 'centers', 'update'),
    ('delete_centers', 'Delete centers', 'centers', 'delete'),

    -- KPI permissions
    ('view_kpi', 'View KPI metrics', 'kpi', 'view'),
    ('submit_kpi', 'Submit KPI events', 'kpi', 'create'),
    ('export_kpi', 'Export KPI data', 'kpi', 'export')
ON CONFLICT (name) DO NOTHING;

-- Assign all permissions to admin role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'admin'
ON CONFLICT DO NOTHING;

-- Assign view and export permissions to analyst role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'analyst'
  AND p.action IN ('view', 'export')
ON CONFLICT DO NOTHING;

-- Assign only view permissions to viewer role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'viewer'
  AND p.action = 'view'
  AND p.resource IN ('dashboard', 'analytics', 'kpi')
ON CONFLICT DO NOTHING;

-- Assign center-specific permissions to center_manager role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'center_manager'
  AND (
      (p.resource IN ('dashboard', 'analytics', 'kpi') AND p.action IN ('view', 'export'))
      OR (p.resource = 'centers' AND p.action = 'view')
  )
ON CONFLICT DO NOTHING;
"""

try:
    with engine.connect() as conn:
        # Execute the script
        conn.execute(text(sql_script))
        conn.commit()

        print("[SUCCESS] Authentication tables created successfully!")
        print()

        # Count tables and roles
        tables_count = conn.execute(text("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'roles', 'permissions', 'user_roles', 'role_permissions')
        """)).scalar()

        roles_count = conn.execute(text("SELECT COUNT(*) FROM roles")).scalar()
        permissions_count = conn.execute(text("SELECT COUNT(*) FROM permissions")).scalar()

        print(f"Tables created: {tables_count}/5")
        print(f"Default roles created: {roles_count}")
        print(f"Default permissions created: {permissions_count}")
        print()

        # Show roles and their permissions
        print("=" * 80)
        print("ROLES AND PERMISSIONS")
        print("=" * 80)

        roles = conn.execute(text("""
            SELECT r.name, r.description, COUNT(rp.permission_id) as perm_count
            FROM roles r
            LEFT JOIN role_permissions rp ON r.id = rp.role_id
            GROUP BY r.id, r.name, r.description
            ORDER BY r.name
        """)).fetchall()

        for role in roles:
            print(f"\n{role[0].upper()}: {role[1]}")
            print(f"  Permissions: {role[2]}")

            # Get specific permissions for this role
            perms = conn.execute(text("""
                SELECT p.name, p.description
                FROM permissions p
                JOIN role_permissions rp ON p.id = rp.permission_id
                JOIN roles r ON r.id = rp.role_id
                WHERE r.name = :role_name
                ORDER BY p.resource, p.action
            """), {"role_name": role[0]}).fetchall()

            if perms:
                for perm in perms[:5]:  # Show first 5
                    print(f"    - {perm[0]}: {perm[1]}")
                if len(perms) > 5:
                    print(f"    ... and {len(perms) - 5} more")

        print()
        print("=" * 80)
        print("NEXT STEP: Run create_admin_user.py to create your first admin user")
        print("=" * 80)

except Exception as e:
    print(f"[ERROR] Error creating auth tables: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
