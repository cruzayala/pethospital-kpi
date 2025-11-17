@echo off
REM Register Test Center in KPI Database

echo ========================================
echo   Register Test Center
echo ========================================
echo.

cd /d "%~dp0"

echo Registering HVC center in database...
echo.
echo Details:
echo   Code: HVC
echo   Name: Hospital Veterinario Central
echo   API Key: test-api-key-local-HVC-2025
echo.

"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -h localhost -d pethospital_kpi -f register-test-center.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS! Center registered.
    echo.
    echo You can now test sending metrics from pethospital.
    echo.
    echo Configure pethospital backend/.env with:
    echo   KPI_SERVICE_URL=http://localhost:8000
    echo   CENTER_CODE=HVC
    echo   CENTER_API_KEY=test-api-key-local-HVC-2025
) else (
    echo.
    echo ERROR: Failed to register center
    echo Make sure the KPI service is running first!
)

echo.
pause
