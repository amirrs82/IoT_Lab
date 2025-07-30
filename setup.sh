#!/bin/bash

echo "🚀 Starting IoT Lab Complete Setup..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo "✅ Docker and docker-compose are available"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start all services
echo "🏗️  Building and starting all services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Run migrations
echo "📋 Running database migrations..."
docker-compose exec -T backend python manage.py migrate

# Create superuser (non-interactive)
echo "👤 Creating superuser (admin/admin)..."
docker-compose exec -T backend python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

echo "🎉 Setup complete!"
echo ""
echo "📱 Frontend: http://localhost:10004"
echo "🔧 Backend API: http://localhost:10003"
echo "👨‍💼 Admin Panel: http://localhost:10003/admin/"
echo "🗄️  Database: localhost:10001"
echo "📮 Redis: localhost:10002"
echo ""
echo "🔑 Admin credentials: admin/admin"
echo ""
echo "🚀 You can now access the application at http://localhost:10004"
