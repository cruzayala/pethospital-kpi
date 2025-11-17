@echo off
REM Test KPI Service Locally
REM This script sets up and runs the KPI service for local testing

echo ========================================
echo   PetHospital KPI - Local Test Setup
echo ========================================
echo.

cd /d "%~dp0"

REM Step 1: Create database
echo [1/6] Creating local database...
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -c "DROP DATABASE IF EXISTS pethospital_kpi;"
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -c "CREATE DATABASE pethospital_kpi;"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create database
    echo Make sure PostgreSQL is running and you have permissions
    pause
    exit /b 1
)
echo Database created successfully!
echo.

REM Step 2: Create virtual environment if not exists
if not exist .venv (
    echo [2/6] Creating Python virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created!
    echo.
) else (
    echo [2/6] Virtual environment already exists
    echo.
)

REM Step 3: Activate virtual environment and install dependencies
echo [3/6] Installing dependencies...
call .venv\Scripts\activate
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed!
echo.

REM Step 4: Set environment variables for local testing
echo [4/6] Setting environment variables...
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pethospital_kpi
echo DATABASE_URL=%DATABASE_URL%
echo.

REM Step 5: Start the server
echo [5/6] Starting KPI service...
echo.
echo Server will start on http://localhost:8000
echo.
echo Open in your browser:
echo   - Dashboard: http://localhost:8000
echo   - API Docs:   http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
