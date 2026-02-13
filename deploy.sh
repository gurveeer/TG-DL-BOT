#!/bin/bash

# Deployment script for GCP VM

set -e

echo "🚀 Starting deployment..."

# Pull latest changes (if using git)
if [ -d ".git" ]; then
    echo "📥 Pulling latest changes..."
    git pull
fi

# Stop existing container
echo "🛑 Stopping existing container..."
docker-compose down || true

# Build new image
echo "🔨 Building Docker image..."
docker-compose build --no-cache

# Start container
echo "▶️  Starting container..."
docker-compose up -d

# Show logs
echo "📋 Container logs:"
docker-compose logs --tail=50

echo "✅ Deployment complete!"
echo "🔍 Check status: docker-compose ps"
echo "📋 View logs: docker-compose logs -f"
