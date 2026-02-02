@echo off
REM SuraSmart Frontend Setup Script for Windows

echo ================================
echo SuraSmart Frontend Setup
echo ================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo X Node.js is not installed. Please install Node.js 16+ first.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo + Node.js %NODE_VERSION% detected
echo.

REM Navigate to frontend directory
cd /d "%~dp0frontend" || exit /b 1

REM Check if node_modules exists
if not exist "node_modules" (
    echo.
    echo Installing dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo X Failed to install dependencies
        pause
        exit /b 1
    )
    echo + Dependencies installed
) else (
    echo + Dependencies already installed
)

REM Copy .env file if it doesn't exist
if not exist ".env" (
    echo.
    echo Creating .env file from .env.example...
    copy .env.example .env
    if %errorlevel% neq 0 (
        echo X Failed to create .env file
        pause
        exit /b 1
    )
    echo + .env file created
)

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo Available commands:
echo   npm start       - Start development server (port 3000)
echo   npm run build   - Create production build
echo   npm test        - Run tests
echo.
echo Starting development server...
echo Frontend will be available at: http://localhost:3000
echo.

call npm start
pause
