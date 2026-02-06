#!/bin/bash
# SignalScore Development Setup Script

set -e

echo "🚀 SignalScore Setup"
echo "===================="

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || command -v docker compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed."; exit 1; }

echo "✅ Prerequisites check passed"

# Navigate to execution directory
cd "$(dirname "$0")/../execution"

echo ""
echo "📦 Building containers..."
docker compose build

echo ""
echo "🏃 Starting services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

echo ""
echo "🔍 Verifying services..."

# Check backend health
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
fi

# Check frontend
if curl -s http://localhost:3000 | grep -q "SignalScore"; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend may still be starting..."
fi

echo ""
echo "🎉 SignalScore is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "To stop: docker compose down"
