#!/bin/bash

# Quick update script - rebuild and redeploy
set -e

# Configuration
PROJECT_ID="noble-operation-479809-g5"
REGION="us-central1"
ZONE="${REGION}-a"
INSTANCE_NAME="telegram-bot-vm"
IMAGE_NAME="telegram-saver-bot"

echo "🔄 Updating bot on GCP..."

# Build and push new image
echo "🔨 Building new image..."
docker build -t gcr.io/$PROJECT_ID/$IMAGE_NAME:latest .

echo "📤 Pushing to GCR..."
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

# Update container on VM
echo "🔄 Updating container on VM..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
    docker pull gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
    docker stop telegram-bot
    docker rm telegram-bot
    docker run -d \
        --name telegram-bot \
        --restart unless-stopped \
        --env-file ~/.env \
        -v ~/downloads:/app/downloads \
        -v ~/sessions:/app/sessions \
        -v ~/attached_assets:/app/attached_assets \
        -p 3000:3000 \
        gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
    docker logs --tail=50 telegram-bot
"

echo "✅ Update complete!"
