#!/bin/bash

# GCP Deployment Script for Telegram Bot
set -e

# Configuration
PROJECT_ID="noble-operation-479809-g5"
REGION="us-central1"
INSTANCE_NAME="telegram-bot-vm"
IMAGE_NAME="telegram-saver-bot"
ZONE="${REGION}-a"

echo "🔧 GCP Configuration:"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Instance: $INSTANCE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Build and push to Google Container Registry
echo "🔨 Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/$IMAGE_NAME:latest .

echo "🔐 Configuring Docker for GCR..."
gcloud auth configure-docker

echo "📤 Pushing image to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

echo "✅ Image pushed successfully!"
echo "📦 Image: gcr.io/$PROJECT_ID/$IMAGE_NAME:latest"
