@echo off
REM Run script for Windows
REM Activates venv and runs the CLI tool

REM Check if venv exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the CLI with all passed arguments
python -m tool.main %*

