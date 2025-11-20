"""
Create admin user in Railway PostgreSQL database
Run this after create_auth_tables.py to create your first superuser
"""
import os
import sys
import getpass
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

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
print("CREATE ADMIN USER IN RAILWAY")
print("=" * 80)
print()

# Get admin user details
print("Please provide admin user details:")
print()

username = input("Username (default: admin): ").strip() or "admin"
email = input("Email: ").strip()

if not email:
    print("[ERROR] Email is required")
    sys.exit(1)

full_name = input("Full Name (default: System Administrator): ").strip() or "System Administrator"

# Get password with confirmation
while True:
    password = getpass.getpass("Password (min 8 chars): ")

    if len(password) < 8:
        print("[ERROR] Password must be at least 8 characters")
        continue

    if not any(char.isdigit() for char in password):
        print("[ERROR] Password must contain at least one digit")
        continue

    if not any(char.isalpha() for char in password):
        print("[ERROR] Password must contain at least one letter")
        continue

    password_confirm = getpass.getpass("Confirm Password: ")

    if password != password_confirm:
        print("[ERROR] Passwords do not match")
        continue

    break

print()
print("Creating admin user...")

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
            print(f"[ERROR] User already exists: {existing[1]}")
            sys.exit(1)

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
        print("User details:")
        print(f"  ID: {user[0]}")
        print(f"  Username: {user[1]}")
        print(f"  Email: {user[2]}")
        print(f"  Full Name: {user[3]}")
        print(f"  Role: admin (superuser)")
        print()
        print("=" * 80)
        print("You can now login with these credentials!")
        print()
        print("Login endpoint: POST http://localhost:8000/auth/login")
        print("Request body:")
        print(f'  {{"username": "{username}", "password": "your-password"}}')
        print()
        print("=" * 80)

except Exception as e:
    print(f"[ERROR] Error creating admin user: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
