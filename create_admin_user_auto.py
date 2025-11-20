"""
Create default admin user in Railway PostgreSQL database (automatic)
Creates admin user with default credentials for quick setup
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Import auth utilities
from app.auth import hash_password

# Get Railway database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not found in .env file")
    sys.exit(1)

print("=" * 80)
print("CREATE DEFAULT ADMIN USER IN RAILWAY")
print("=" * 80)
print()

# Default admin credentials
username = "admin"
email = "admin@pethospital-kpi.com"
full_name = "System Administrator"
password = "Admin123!"  # Must meet password requirements

print("Creating admin user with default credentials...")
print(f"  Username: {username}")
print(f"  Email: {email}")
print(f"  Password: {password}")
print()

# Create engine
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check if user already exists
        existing = conn.execute(
            text("SELECT id, username FROM users WHERE username = :username OR email = :email"),
            {"username": username, "email": email}
        ).fetchone()

        if existing:
            print(f"[WARNING] User already exists: {existing[1]}")
            print("[INFO] To reset password, delete the user manually and run this script again")
            sys.exit(0)

        # Get admin role
        admin_role = conn.execute(
            text("SELECT id FROM roles WHERE name = 'admin'")
        ).fetchone()

        if not admin_role:
            print("[ERROR] Admin role not found. Did you run create_auth_tables.py?")
            sys.exit(1)

        admin_role_id = admin_role[0]

        # Hash password
        hashed_password = hash_password(password)

        # Insert user
        result = conn.execute(
            text("""
                INSERT INTO users (
                    username, email, hashed_password, full_name,
                    is_active, is_superuser, email_verified,
                    created_at, updated_at
                )
                VALUES (
                    :username, :email, :hashed_password, :full_name,
                    true, true, true,
                    NOW(), NOW()
                )
                RETURNING id, username, email, full_name
            """),
            {
                "username": username,
                "email": email,
                "hashed_password": hashed_password,
                "full_name": full_name
            }
        )

        user = result.fetchone()
        user_id = user[0]

        # Assign admin role
        conn.execute(
            text("""
                INSERT INTO user_roles (user_id, role_id)
                VALUES (:user_id, :role_id)
            """),
            {"user_id": user_id, "role_id": admin_role_id}
        )

        conn.commit()

        print()
        print("[SUCCESS] Admin user created successfully in Railway!")
        print()
        print("=" * 80)
        print("LOGIN CREDENTIALS")
        print("=" * 80)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print()
        print("=" * 80)
        print("TEST THE LOGIN")
        print("=" * 80)
        print()
        print("Using curl:")
        print('curl -X POST http://localhost:8000/auth/login \\')
        print('  -H "Content-Type: application/json" \\')
        print(f'  -d \'{{"username": "{username}", "password": "{password}"}}\'')
        print()
        print("Or visit: http://localhost:8000/docs")
        print("  (FastAPI automatic documentation with Try It Out feature)")
        print()
        print("=" * 80)
        print("IMPORTANT: Change the password after first login!")
        print("=" * 80)

except Exception as e:
    print(f"[ERROR] Error creating admin user: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
