@echo off
REM Setup script for Windows
REM Creates virtual environment and installs dependencies

echo 🚀 Setting up SeamlessM4T S2ST Translator...

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found. Please install Python 3.9+ first.
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Install dev dependencies if available
if exist "requirements-dev.txt" (
    echo 📥 Installing development dependencies...
    pip install -r requirements-dev.txt
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "input" mkdir input
if not exist "output\translated" mkdir output\translated
if not exist "output\metadata" mkdir output\metadata
if not exist "output\logs" mkdir output\logs
if not exist "output\backups" mkdir output\backups
if not exist "config" mkdir config

echo.
echo ✅ Setup complete!
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To start using the tool, run:
echo   run.bat --help
echo.

pause

