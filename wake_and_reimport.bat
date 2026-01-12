@echo off
echo ============================================================
echo Wake Turso Database and Reimport Sections
echo ============================================================
echo.
echo Step 1: Waking up Turso database...
echo Running a simple query to wake the database...
turso db shell pitaka-dishanhewage "SELECT 1;"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to wake database. Please check:
    echo    1. Turso CLI is installed: turso --version
    echo    2. You're logged in: turso auth login
    echo    3. Database name is correct: pitaka-dishanhewage
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Database is awake!
echo.
echo Step 2: Running reimport script...
echo.
timeout /t 2 /nobreak >nul

python delete_and_reimport_sections.py

pause
