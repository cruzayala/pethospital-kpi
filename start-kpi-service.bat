@echo off
REM Start KPI Service for Codex Veterinaria
REM This script starts the KPI tracking service on port 8000

echo ========================================
echo Starting KPI Service
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\uvicorn.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run setup first.
    pause
    exit /b 1
)

echo Starting KPI service on port 8000...
echo Press CTRL+C to stop the service
echo.

.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload

pause
