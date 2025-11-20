"""
Setup and run KPI service locally
This script creates the database and starts the server
"""
import subprocess
import sys
import os
import time

def run_command(cmd, description):
    """Run command and show output"""
    print(f"\n[{description}]")
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    print("=" * 50)
    print("  PetHospital KPI - Setup and Run")
    print("=" * 50)

    # Set environment
    os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/pethospital_kpi'
    os.environ['PGPASSWORD'] = 'postgres'

    # Step 1: Create database
    print("\n[1/4] Creating database...")
    psql_path = r'"C:\Program Files\PostgreSQL\17\bin\psql.exe"'

    # Drop if exists
    run_command(
        f'{psql_path} -U postgres -h localhost -c "DROP DATABASE IF EXISTS pethospital_kpi;"',
        "Dropping old database"
    )

    # Create new
    success = run_command(
        f'{psql_path} -U postgres -h localhost -c "CREATE DATABASE pethospital_kpi;"',
        "Creating new database"
    )

    if not success:
        print("\nWARNING: Database might already exist, continuing...")

    # Step 2: Check if venv exists
    print("\n[2/4] Checking Python environment...")
    if not os.path.exists('.venv'):
        print("Creating virtual environment...")
        run_command('python -m venv .venv', "Creating venv")
    else:
        print("Virtual environment already exists")

    # Step 3: Install dependencies
    print("\n[3/4] Installing dependencies...")
    pip_cmd = '.venv\\Scripts\\pip.exe'
    run_command(f'{pip_cmd} install -q -r requirements.txt', "Installing packages")

    # Step 4: Start server
    print("\n[4/4] Starting KPI service...")
    print("\nServer will start on http://localhost:8000")
    print("Press Ctrl+C to stop\n")
    print("=" * 50)
    print()

    uvicorn_cmd = '.venv\\Scripts\\uvicorn.exe'
    subprocess.run(f'{uvicorn_cmd} app.main:app --reload --host 0.0.0.0 --port 8000', shell=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
