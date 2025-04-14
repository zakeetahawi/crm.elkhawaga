#!/bin/bash

# Exit on error
set -e

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Build Docker images
echo "Building Docker images..."
docker-compose build

# Start containers
echo "Starting containers..."
docker-compose up -d

# Wait for web service to be ready
echo "Waiting for web service..."
sleep 10

# Collect static files
echo "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
docker-compose exec -T web python manage.py migrate --noinput

# Create necessary directories if they don't exist
echo "Creating necessary directories..."
mkdir -p staticfiles
mkdir -p media

# Copy static files from container to local directory
echo "Copying static files..."
docker cp $(docker-compose ps -q web):/app/staticfiles/. ./staticfiles/

# Stop containers
echo "Stopping containers..."
docker-compose down

echo "Build completed successfully!"
