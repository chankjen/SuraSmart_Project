@echo off
REM Quick Start Script for SuraSmart Phase 1 Backend (Windows)

echo.
echo 🚀 SuraSmart Backend - Quick Start
echo ==================================
echo.

REM Check if docker is installed
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop.
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose found
echo.

REM Navigate to backend
cd /d "%~dp0backend" || exit /b 1

REM Check if .env exists
if not exist .env (
    echo ⚙️  Creating .env file from template...
    copy .env.example .env
    echo ✅ Created .env - update with your values if needed
    echo.
)

REM Start services
echo 🐳 Starting Docker services...
echo    - PostgreSQL (port 5432)
echo    - Redis (port 6379)
echo    - Django Backend (port 8000)
echo    - Celery Worker
echo    - Celery Beat
echo.

docker-compose up -d

REM Wait for services
echo ⏳ Waiting for services to be ready... (30 seconds)
timeout /t 30 /nobreak

REM Run migrations
echo.
echo 🔄 Running database migrations...
docker-compose exec -T backend python manage.py migrate

REM Create superuser
echo.
echo 👤 Creating superuser account...
docker-compose exec backend python manage.py createsuperuser

echo.
echo ✨ Setup Complete!
echo.
echo 📱 Access Points:
echo    - API: http://localhost:8000/api/
echo    - Admin: http://localhost:8000/admin/
echo    - Health Check: http://localhost:8000/api/health/check/
echo.
echo 📚 Documentation:
echo    - Backend: open backend\README.md
echo    - Migration: open MIGRATION_GUIDE.md
echo.
echo 🛑 To stop services: docker-compose down (in backend\ directory)
echo 📊 To view logs: docker-compose logs -f backend
echo.
pause
