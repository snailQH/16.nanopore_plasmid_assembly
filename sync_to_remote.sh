#!/bin/bash
# Sync pipeline code to remote server

set -e

# Configuration
REMOTE_HOST="localhost"
REMOTE_PORT="2225"
REMOTE_USER="bioinfo"
REMOTE_PASS="ampseq@2025"
JUMP_HOST="root@8.133.18.117"
REMOTE_DIR="/data1/opt/nanopore_plasmid_pipeline/cursor_pipeline"
LOCAL_DIR="."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Syncing pipeline code to remote server...${NC}"
echo "Remote: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PORT}"
echo "Target: ${REMOTE_DIR}"

# Create remote directory if it doesn't exist
echo -e "${YELLOW}Creating remote directory...${NC}"
sshpass -p "${REMOTE_PASS}" ssh -o StrictHostKeyChecking=no \
  -J ${JUMP_HOST} \
  -p ${REMOTE_PORT} \
  ${REMOTE_USER}@${REMOTE_HOST} \
  "mkdir -p ${REMOTE_DIR}"

# Sync files (excluding archive, __pycache__, etc.)
echo -e "${YELLOW}Syncing files...${NC}"
rsync -avz --progress \
  --exclude 'archive/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.git/' \
  --exclude 'output/' \
  --exclude 'results/' \
  --exclude 'logs/' \
  --exclude '*.log' \
  -e "sshpass -p '${REMOTE_PASS}' ssh -o StrictHostKeyChecking=no -J ${JUMP_HOST} -p ${REMOTE_PORT}" \
  ${LOCAL_DIR}/ \
  ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/

echo -e "${GREEN}Sync completed!${NC}"
echo ""
echo "Files synced to: ${REMOTE_DIR}"
echo ""
echo "To connect to remote server:"
echo "  ssh -J ${JUMP_HOST} ${REMOTE_USER}@${REMOTE_HOST} -p ${REMOTE_PORT}"

