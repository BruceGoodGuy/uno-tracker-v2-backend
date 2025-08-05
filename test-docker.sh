#!/bin/bash

echo "🐳 Testing Uno Tracker Backend Docker Setup"
echo "============================================"

# Check if containers are running
echo "📋 Checking container status..."
docker-compose ps

echo ""
echo "🔍 Testing API endpoints..."

# Test API documentation
echo "- Testing API docs endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ $response -eq 200 ]; then
    echo "  ✅ API docs accessible at http://localhost:8000/docs"
else
    echo "  ❌ API docs not accessible (HTTP $response)"
fi

# Test OpenAPI JSON
echo "- Testing OpenAPI JSON endpoint..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/openapi.json)
if [ $response -eq 200 ]; then
    echo "  ✅ OpenAPI JSON accessible at http://localhost:8000/openapi.json"
else
    echo "  ❌ OpenAPI JSON not accessible (HTTP $response)"
fi

# Test database connectivity (check if we can connect to the container)
echo "- Testing database connectivity..."
db_test=$(docker-compose exec -T db pg_isready -U uno_user -d uno_tracker 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "  ✅ Database is ready and accepting connections"
else
    echo "  ❌ Database connection failed"
fi

echo ""
echo "📊 Container resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

echo ""
echo "🔧 Quick commands:"
echo "- View logs: docker-compose logs -f"
echo "- Stop containers: docker-compose down"
echo "- Restart: docker-compose restart"
echo "- Access API docs: http://localhost:8000/docs"
echo "- Connect to database: docker-compose exec db psql -U uno_user -d uno_tracker"

echo ""
echo "✅ Docker setup test completed!"
