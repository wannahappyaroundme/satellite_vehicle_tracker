@echo off
echo 🪟 Setting up Satellite Vehicle Tracker on Windows...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set python_version=%%i
echo ✅ Python %python_version% found

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

for /f %%i in ('node --version') do set node_version=%%i
echo ✅ Node.js %node_version% found

echo 📦 Installing Python dependencies...
cd backend

REM Create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
echo Installing Python packages...
pip install -r requirements.txt

REM Download YOLO model if it doesn't exist
if not exist "yolov8n.pt" (
    echo Downloading YOLO model...
    python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
)

cd ..

echo 📦 Installing Node.js dependencies...
cd frontend
call npm install
cd ..

echo 📦 Installing root dependencies...
call npm install

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating environment file...
    copy env.example .env
    echo ⚠️  Please edit .env file with your configuration (especially Google Maps API key)
)

REM Create startup script
echo Creating startup script...
(
echo @echo off
echo echo 🚀 Starting Satellite Vehicle Tracker...
echo echo.
echo echo Activating Python virtual environment...
echo cd backend
echo call venv\Scripts\activate.bat
echo cd ..
echo echo.
echo echo Starting both frontend and backend...
echo call npm run dev
echo pause
) > start_windows.bat

echo.
echo 🎉 Setup complete!
echo.
echo To start the application:
echo   start_windows.bat
echo.
echo Or manually:
echo   cd backend ^&^& venv\Scripts\activate ^&^& python app.py
echo   cd frontend ^&^& npm start
echo.
echo Access the application at:
echo   🌐 Frontend: http://localhost:3000
echo   🔧 Backend API: http://localhost:5000
echo.
echo 📝 Don't forget to:
echo   1. Get a Google Maps API key and add it to .env
echo   2. Configure other settings in .env as needed
echo.
echo 🛰️ Happy satellite tracking!
pause
