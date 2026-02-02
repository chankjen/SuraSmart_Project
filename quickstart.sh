#!/bin/bash
# Quick Start Script for SuraSmart Phase 1 Backend

set -e

echo "🚀 SuraSmart Backend - Quick Start"
echo "=================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Desktop."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Navigate to backend
cd "$(dirname "$0")/backend" || exit 1

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env - update with your values if needed"
fi

# Start services
echo ""
echo "🐳 Starting Docker services..."
echo "   - PostgreSQL (port 5432)"
echo "   - Redis (port 6379)"
echo "   - Django Backend (port 8000)"
echo "   - Celery Worker"
echo "   - Celery Beat"

docker-compose up -d

# Wait for services
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo ""
echo "🔄 Running database migrations..."
docker-compose exec -T backend python manage.py migrate

# Create superuser
echo ""
echo "👤 Creating superuser account..."
docker-compose exec backend python manage.py createsuperuser

# Check health
echo ""
echo "🏥 Checking system health..."
HEALTH=$(curl -s http://localhost:8000/api/health/check/ || echo "")

if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ System is healthy!"
else
    echo "⚠️  Could not verify health. Check Docker logs:"
    echo "   docker-compose logs backend"
fi

echo ""
echo "✨ Setup Complete!"
echo ""
echo "📱 Access Points:"
echo "   - API: http://localhost:8000/api/"
echo "   - Admin: http://localhost:8000/admin/"
echo "   - Health Check: http://localhost:8000/api/health/check/"
echo ""
echo "📚 Documentation:"
echo "   - Backend: cat backend/README.md"
echo "   - Migration: cat MIGRATION_GUIDE.md"
echo ""
echo "🛑 To stop services: docker-compose down"
echo "📊 To view logs: docker-compose logs -f backend"
