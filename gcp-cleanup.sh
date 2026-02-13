#!/bin/bash

# Cleanup GCP resources
set -e

# Configuration
PROJECT_ID="noble-operation-479809-g5"
REGION="us-central1"
ZONE="${REGION}-a"
INSTANCE_NAME="telegram-bot-vm"
IMAGE_NAME="telegram-saver-bot"

echo "🗑️  Cleaning up GCP resources..."

read -p "⚠️  This will delete the VM and all data. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Stop and delete VM
echo "🛑 Deleting VM instance..."
gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE --quiet

# Delete firewall rule
echo "🔥 Deleting firewall rule..."
gcloud compute firewall-rules delete allow-telegram-bot-health --quiet

# Delete container images (optional)
read -p "Delete container images from GCR? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Deleting images..."
    gcloud container images delete gcr.io/$PROJECT_ID/$IMAGE_NAME:latest --quiet
fi

echo "✅ Cleanup complete!"
