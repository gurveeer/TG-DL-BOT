#!/bin/bash

# GCP VM Setup and Deployment Script
set -e

# Configuration
PROJECT_ID="noble-operation-479809-g5"
REGION="us-central1"
ZONE="${REGION}-a"
INSTANCE_NAME="telegram-bot-vm"
IMAGE_NAME="telegram-saver-bot"
MACHINE_TYPE="e2-micro"  # Free tier eligible

echo "🚀 Deploying to GCP VM..."

# Create VM instance if it doesn't exist
if ! gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE &> /dev/null; then
    echo "📦 Creating new VM instance..."
    gcloud compute instances create $INSTANCE_NAME \
        --zone=$ZONE \
        --machine-type=$MACHINE_TYPE \
        --image-family=cos-stable \
        --image-project=cos-cloud \
        --boot-disk-size=10GB \
        --boot-disk-type=pd-standard \
        --tags=telegram-bot,http-server \
        --metadata=google-logging-enabled=true \
        --scopes=cloud-platform
    
    echo "⏳ Waiting for VM to be ready..."
    sleep 30
else
    echo "✅ VM instance already exists"
fi

# Create firewall rule for health check port
if ! gcloud compute firewall-rules describe allow-telegram-bot-health &> /dev/null; then
    echo "🔥 Creating firewall rule..."
    gcloud compute firewall-rules create allow-telegram-bot-health \
        --allow=tcp:3000 \
        --target-tags=telegram-bot \
        --description="Allow health check on port 3000"
fi

# Get VM external IP
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "🌐 VM External IP: $EXTERNAL_IP"

# Copy .env file to VM
echo "📋 Copying environment configuration..."
gcloud compute scp .env $INSTANCE_NAME:~/.env --zone=$ZONE

# Deploy container to VM
echo "🐳 Deploying container to VM..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
    set -e
    
    # Pull the image
    echo '📥 Pulling Docker image...'
    docker-credential-gcr configure-docker
    docker pull gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
    
    # Stop existing container
    echo '🛑 Stopping existing container...'
    docker stop telegram-bot 2>/dev/null || true
    docker rm telegram-bot 2>/dev/null || true
    
    # Create directories
    mkdir -p ~/downloads ~/sessions ~/attached_assets
    
    # Run new container
    echo '▶️  Starting new container...'
    docker run -d \
        --name telegram-bot \
        --restart unless-stopped \
        --env-file ~/.env \
        -v ~/downloads:/app/downloads \
        -v ~/sessions:/app/sessions \
        -v ~/attached_assets:/app/attached_assets \
        -p 3000:3000 \
        gcr.io/$PROJECT_ID/$IMAGE_NAME:latest
    
    echo '✅ Container started successfully!'
    
    # Show logs
    echo '📋 Container logs:'
    docker logs --tail=50 telegram-bot
"

echo ""
echo "✅ Deployment complete!"
echo "🌐 Health check: http://$EXTERNAL_IP:3000/health"
echo ""
echo "📋 Useful commands:"
echo "   View logs:    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='docker logs -f telegram-bot'"
echo "   Restart bot:  gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='docker restart telegram-bot'"
echo "   SSH to VM:    gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
