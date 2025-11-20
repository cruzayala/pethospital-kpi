"""
Create default analyst user for PetHospital KPI Service
"""
import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[ERROR] DATABASE_URL not found in environment variables")
    exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Import models after engine is created
from app.models import User, Role

def create_analyst_user():
    """Create default analyst user"""
    db = SessionLocal()

    try:
        print("="*80)
        print("CREATE DEFAULT ANALYST USER IN RAILWAY")
        print("="*80)
        print()

        # Check if user exists
        existing_user = db.execute(
            select(User).where(User.username == "analyst")
        ).scalar_one_or_none()

        if existing_user:
            print(f"[WARNING] User already exists: analyst")
            print(f"[INFO] To reset password, delete the user manually and run this script again")
            return

        # Get analyst role
        analyst_role = db.execute(
            select(Role).where(Role.name == "analyst")
        ).scalar_one_or_none()

        if not analyst_role:
            print("[ERROR] Analyst role not found. Run create_auth_tables.py first")
            return

        # Create user
        print("Creating analyst user with default credentials...")
        print("  Username: analyst")
        print("  Email: analyst@pethospital-kpi.com")
        print("  Password: Analyst123!")
        print()

        hashed_password = pwd_context.hash("Analyst123!")

        user = User(
            username="analyst",
            email="analyst@pethospital-kpi.com",
            full_name="Data Analyst",
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
            email_verified=True
        )

        # Add analyst role
        user.roles.append(analyst_role)

        db.add(user)
        db.commit()

        print("[SUCCESS] Analyst user created successfully!")
        print()
        print("="*80)
        print("CREDENTIALS")
        print("="*80)
        print("Username: analyst")
        print("Password: Analyst123!")
        print()
        print("[IMPORTANT] Change this password in production!")
        print("="*80)

    except Exception as e:
        print(f"[ERROR] Failed to create analyst user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_analyst_user()
