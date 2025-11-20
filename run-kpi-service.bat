@echo off
REM ========================================
REM Codex Veterinaria - KPI Service Launcher
REM ========================================
REM This script starts the KPI tracking service
REM that receives metrics from the main application
REM ========================================

TITLE Codex Veterinaria - KPI Service

color 0A
cls

echo.
echo ========================================
echo  CODEX VETERINARIA - KPI SERVICE
echo ========================================
echo.
echo  Starting KPI tracking service...
echo  Port: 8000
echo.
echo ========================================
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ to continue
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo [INFO] Virtual environment not found. Creating...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [SUCCESS] Virtual environment created
)

REM Check if dependencies are installed
if not exist ".venv\Scripts\uvicorn.exe" (
    echo [INFO] Installing dependencies...
    .venv\Scripts\pip.exe install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed
)

REM Start the service
echo.
echo ========================================
echo  SERVICE STARTING...
echo ========================================
echo.
echo  KPI Service URL: http://localhost:8000
echo  Documentation: http://localhost:8000/docs
echo.
echo  Press CTRL+C to stop the service
echo.
echo ========================================
echo.

.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload

REM If service stops, pause to see error
echo.
echo [INFO] KPI Service stopped
pause
