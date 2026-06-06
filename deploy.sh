#!/bin/bash
# Exit on error
set -e

echo "🚀 Preparing deployment to miron@100.111.67.75..."

# SSH connection details
REMOTE_HOST="100.111.67.75"
REMOTE_USER="miron"
REMOTE_DIR="/home/miron/github-trending-web"

# Create directory on server if it doesn't exist
ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_DIR}"

# Rsync files to the remote server, excluding virtual environments, git history, cache, etc.
echo "📦 Uploading files..."
rsync -avz --exclude '.venv' \
          --exclude '.git' \
          --exclude '__pycache__' \
          --exclude '.DS_Store' \
          --exclude '*.log' \
          --exclude 'node_modules' \
          -e "ssh -o StrictHostKeyChecking=no" \
          ./ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/

# Connect via SSH and run Docker Compose
echo "🐳 Rebuilding and starting Docker containers on the server..."
ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR} && docker compose down && docker compose up -d --build"

echo "✨ Deployment complete! App is running on http://${REMOTE_HOST}:5051"
