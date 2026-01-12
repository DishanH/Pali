@echo off
REM Batch script to run the numberRange migration on Windows

echo ============================================================
echo NumberRange Migration for Turso Database
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python first: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Step 1: Checking dependencies...
echo.

REM Try to import libsql_experimental
python -c "import libsql_experimental" >nul 2>&1
if errorlevel 1 (
    echo libsql-experimental is not installed.
    echo.
    echo Would you like to install it now? (Y/N)
    set /p install_deps=
    if /i "%install_deps%"=="Y" (
        echo Installing dependencies...
        pip install libsql-experimental python-dotenv
        if errorlevel 1 (
            echo.
            echo Error: Failed to install dependencies
            echo.
            echo Alternative: Run the SQL files manually using Turso CLI:
            echo   turso db shell your-db-name ^< add_number_range_migration.sql
            echo   turso db shell your-db-name ^< number_range_updates.sql
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Skipping automatic migration.
        echo.
        echo Please run the SQL files manually using Turso CLI:
        echo   turso db shell your-db-name ^< add_number_range_migration.sql
        echo   turso db shell your-db-name ^< number_range_updates.sql
        echo.
        echo Or install dependencies and run: python execute_number_range_migration.py
        pause
        exit /b 0
    )
)

echo.
echo Step 2: Running migration script...
echo.

python execute_number_range_migration.py

if errorlevel 1 (
    echo.
    echo Migration failed. Please check the error messages above.
    echo.
    echo You can also try running the SQL files manually:
    echo   turso db shell your-db-name ^< add_number_range_migration.sql
    echo   turso db shell your-db-name ^< number_range_updates.sql
) else (
    echo.
    echo ============================================================
    echo Migration completed successfully!
    echo ============================================================
)

echo.
pause
