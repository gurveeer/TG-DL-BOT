#!/bin/bash

# View bot logs from GCP VM
set -e

# Configuration
PROJECT_ID="noble-operation-479809-g5"
REGION="us-central1"
ZONE="${REGION}-a"
INSTANCE_NAME="telegram-bot-vm"

gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="docker logs -f telegram-bot"
