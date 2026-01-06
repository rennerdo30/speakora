@echo off
REM All-in-one startup script for Windows
REM Updates venv, builds frontend, and starts the server

echo 🚀 Starting S2ST Translator (All-in-One)...
echo.

REM Check if venv exists
if not exist "venv" (
    echo ⚠️  Virtual environment not found. Running setup first...
    call setup.bat
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Update Python dependencies
echo 📦 Updating Python dependencies...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
pip install -r requirements.txt --quiet
if exist "requirements-dev.txt" (
    pip install -r requirements-dev.txt --quiet
)
echo ✅ Python dependencies updated
echo.

REM Check if Node.js is available
where node >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Node.js not found. Skipping frontend build.
    echo    Install Node.js to build the frontend, or use dev mode separately.
    set FRONTEND_BUILT=false
) else (
    REM Check if frontend directory exists
    if not exist "frontend" (
        echo ⚠️  Frontend directory not found. Skipping frontend build.
        set FRONTEND_BUILT=false
    ) else (
        REM Update frontend dependencies and build
        echo 📦 Updating frontend dependencies...
        cd frontend
        
        REM Check if node_modules exists, if not, install
        if not exist "node_modules" (
            echo    Installing npm packages (this may take a while)...
            call npm install
        ) else (
            REM Update packages
            call npm install --silent
        )
        
        echo ✅ Frontend dependencies updated
        echo.
        
        REM Build frontend
        echo 🔨 Building frontend...
        call npm run build
        
        if exist "dist" (
            echo ✅ Frontend built successfully
            set FRONTEND_BUILT=true
        ) else (
            echo ⚠️  Frontend build may have failed, but continuing...
            set FRONTEND_BUILT=false
        )
        
        cd ..
        echo.
    )
)

REM Create necessary directories
if not exist "input" mkdir input
if not exist "output\translated" mkdir output\translated
if not exist "output\metadata" mkdir output\metadata
if not exist "output\logs" mkdir output\logs
if not exist "output\backups" mkdir output\backups
if not exist "config" mkdir config

REM Start the server
echo 🎉 Starting server...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ✅ Setup complete!
if "%FRONTEND_BUILT%"=="true" (
    echo ✅ Frontend built and ready
)
echo.
echo 🌐 Server will be available at:
echo    http://127.0.0.1:5000
echo.
echo 📚 API Documentation:
echo    http://127.0.0.1:5000/docs
echo.
echo Press CTRL+C to stop the server
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Start the GUI server
python -m tool.main gui --host 127.0.0.1 --port 5000

