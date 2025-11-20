"""
Test script to verify Supabase database connection
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load environment variables
load_dotenv()

def test_connection():
    """Test the database connection"""
    database_url = os.getenv("DATABASE_URL")

    print("=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)
    print()

    # Check if DATABASE_URL exists
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in .env file")
        return False

    # Check if password placeholder is still present
    if "[YOUR-PASSWORD]" in database_url:
        print("❌ ERROR: Password placeholder detected!")
        print()
        print("The DATABASE_URL still contains [YOUR-PASSWORD]")
        print("You need to replace it with your real Supabase password.")
        print()
        print("Steps to get your password:")
        print("1. Go to https://supabase.com")
        print("2. Open your project")
        print("3. Go to Settings → Database")
        print("4. Look for 'Database password' section")
        print("5. If you don't remember it, click 'Reset Database Password'")
        print("6. Copy the new password")
        print("7. Replace [YOUR-PASSWORD] in the .env file")
        print()
        return False

    # Obscure password for display
    display_url = database_url
    if "@" in database_url:
        parts = database_url.split("@")
        auth_part = parts[0].split(":")
        if len(auth_part) > 2:
            password = auth_part[2]
            display_url = database_url.replace(password, "***")

    print(f"DATABASE_URL: {display_url}")
    print()

    # Try to connect
    print("Attempting to connect to Supabase...")
    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            # Test basic query
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]

            print("✅ CONNECTION SUCCESSFUL!")
            print()
            print(f"PostgreSQL Version: {version}")
            print()

            # Check if tables exist
            print("Checking for required tables...")
            tables_query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('centers', 'daily_metrics', 'test_summary', 'species_summary', 'breed_summary')
                ORDER BY table_name;
            """)

            result = conn.execute(tables_query)
            existing_tables = [row[0] for row in result]

            required_tables = ['centers', 'daily_metrics', 'test_summary', 'species_summary', 'breed_summary']

            if len(existing_tables) == 0:
                print("⚠️  WARNING: No tables found!")
                print()
                print("You need to create the database tables.")
                print("Follow these steps:")
                print("1. Go to your Supabase project")
                print("2. Click on 'SQL Editor'")
                print("3. Copy the SQL script from GUIA_SUPABASE.md")
                print("4. Paste and run it in the SQL Editor")
                print()
            elif len(existing_tables) < len(required_tables):
                print(f"⚠️  WARNING: Only {len(existing_tables)}/{len(required_tables)} tables found")
                print()
                print("Existing tables:")
                for table in existing_tables:
                    print(f"  ✓ {table}")
                print()
                print("Missing tables:")
                for table in required_tables:
                    if table not in existing_tables:
                        print(f"  ✗ {table}")
                print()
            else:
                print("✅ All required tables found:")
                for table in existing_tables:
                    print(f"  ✓ {table}")
                print()

            # Check if any data exists
            if 'centers' in existing_tables:
                result = conn.execute(text("SELECT COUNT(*) FROM centers;"))
                center_count = result.fetchone()[0]
                print(f"Centers in database: {center_count}")

                if center_count == 0:
                    print()
                    print("ℹ️  INFO: No centers registered yet.")
                    print("You can register a center by sending data to /kpi/submit")
                    print("or by using the register_hvc.py script.")

            print()
            print("=" * 60)
            print("CONNECTION TEST COMPLETED SUCCESSFULLY")
            print("=" * 60)
            return True

    except OperationalError as e:
        print("❌ CONNECTION FAILED!")
        print()
        print(f"Error: {str(e)}")
        print()
        print("Common issues:")
        print("1. Wrong password")
        print("2. Wrong database host or port")
        print("3. Database not accessible (firewall/network)")
        print("4. Supabase project paused (free tier inactivity)")
        print()
        return False
    except Exception as e:
        print("❌ UNEXPECTED ERROR!")
        print()
        print(f"Error: {str(e)}")
        print()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
