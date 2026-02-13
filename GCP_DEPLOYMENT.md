# GCP Deployment Guide

## Prerequisites

1. **Install Google Cloud SDK**
   ```bash
   # macOS
   brew install google-cloud-sdk
   
   # Windows
   # Download from: https://cloud.google.com/sdk/docs/install
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   ```

2. **Authenticate with GCP**
   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

3. **Enable Required APIs**
   ```bash
   gcloud services enable compute.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

## Configuration

1. **Update deployment scripts** with your GCP project details:
   - Edit `gcp-deploy.sh`
   - Edit `gcp-vm-setup.sh`
   - Edit `gcp-update.sh`
   - Edit `gcp-logs.sh`
   - Edit `gcp-cleanup.sh`
   
   Replace these values:
   ```bash
   PROJECT_ID="your-gcp-project-id"
   REGION="us-central1"  # Choose your preferred region
   INSTANCE_NAME="telegram-bot-vm"
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   nano .env  # Add your Telegram credentials
   ```

## Deployment Steps

### First Time Deployment

```bash
# Make scripts executable
chmod +x gcp-*.sh

# Step 1: Build and push Docker image to GCR
./gcp-deploy.sh

# Step 2: Create VM and deploy container
./gcp-vm-setup.sh
```

### Update Existing Deployment

```bash
# Quick update (rebuild and redeploy)
./gcp-update.sh
```

### View Logs

```bash
# Stream live logs
./gcp-logs.sh

# Or use gcloud directly
gcloud compute ssh telegram-bot-vm --zone=us-central1-a --command="docker logs -f telegram-bot"
```

### Manual Commands

```bash
# SSH into VM
gcloud compute ssh telegram-bot-vm --zone=us-central1-a

# Restart container
gcloud compute ssh telegram-bot-vm --zone=us-central1-a --command="docker restart telegram-bot"

# Stop container
gcloud compute ssh telegram-bot-vm --zone=us-central1-a --command="docker stop telegram-bot"

# Check container status
gcloud compute ssh telegram-bot-vm --zone=us-central1-a --command="docker ps"

# View VM details
gcloud compute instances describe telegram-bot-vm --zone=us-central1-a
```

## Cost Optimization

The default configuration uses:
- **Machine Type**: e2-micro (free tier eligible)
- **Disk**: 10GB standard persistent disk
- **Region**: us-central1 (adjust for your location)

**Free Tier Limits** (as of 2024):
- 1 e2-micro instance per month
- 30GB standard persistent disk
- 1GB egress per month

## Monitoring

### Health Check
```bash
# Get VM IP
EXTERNAL_IP=$(gcloud compute instances describe telegram-bot-vm \
    --zone=us-central1-a \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

# Check health endpoint
curl http://$EXTERNAL_IP:3000/health
```

### Cloud Logging
```bash
# View VM logs in Cloud Console
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_id=telegram-bot-vm" --limit 50
```

## Troubleshooting

### Container won't start
```bash
# Check container logs
gcloud compute ssh telegram-bot-vm --zone=us-central1-a --command="docker logs telegram-bot"

# Check if .env file exists
gcloud compute ssh telegram-bot-vm --zone=us-central1-a --command="cat ~/.env"
```

### Can't pull image
```bash
# Reconfigure Docker credentials on VM
gcloud compute ssh telegram-bot-vm --zone=us-central1-a --command="docker-credential-gcr configure-docker"
```

### Firewall issues
```bash
# List firewall rules
gcloud compute firewall-rules list

# Recreate health check rule
gcloud compute firewall-rules create allow-telegram-bot-health \
    --allow=tcp:3000 \
    --target-tags=telegram-bot
```

## Cleanup

To remove all GCP resources:
```bash
./gcp-cleanup.sh
```

Or manually:
```bash
# Delete VM
gcloud compute instances delete telegram-bot-vm --zone=us-central1-a

# Delete firewall rule
gcloud compute firewall-rules delete allow-telegram-bot-health

# Delete images
gcloud container images delete gcr.io/your-project-id/telegram-saver-bot:latest
```

## Architecture

```
Local Machine
    ↓ (docker build + push)
Google Container Registry (GCR)
    ↓ (docker pull)
GCP Compute Engine VM (Container-Optimized OS)
    ↓ (docker run)
Telegram Bot Container
    ├── Port 3000 (health check)
    ├── Volume: ~/downloads
    ├── Volume: ~/sessions
    └── Volume: ~/attached_assets
```

## Security Notes

- The VM uses Container-Optimized OS (minimal attack surface)
- Firewall only allows port 3000 for health checks
- Telegram API uses encrypted connections
- Session files are stored in persistent volumes
- Environment variables are not exposed in container images
