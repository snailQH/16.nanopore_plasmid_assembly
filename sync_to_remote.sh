#!/bin/bash
# Sync pipeline code to remote test server (bioinfo@ampseq01)
# This script uses scp/rsync to sync code directly for testing

set -e

# Configuration for test server (ampseq01)
REMOTE_USER="bioinfo"
REMOTE_HOST="ampseq01"
REMOTE_DIR="/opt/nanopore_plasmid_pipeline/cursor_pipeline"
LOCAL_DIR="."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Syncing pipeline code to test server...${NC}"
echo "Remote: ${REMOTE_USER}@${REMOTE_HOST}"
echo "Target: ${REMOTE_DIR}"
echo ""

# Test SSH connection
echo -e "${YELLOW}Testing SSH connection...${NC}"
if ssh -o ConnectTimeout=5 "${REMOTE_USER}@${REMOTE_HOST}" "echo 'Connection successful'" 2>/dev/null; then
  echo -e "${GREEN}✓ SSH connection successful${NC}"
else
  echo "ERROR: Cannot connect to ${REMOTE_USER}@${REMOTE_HOST}"
  echo "Please check:"
  echo "  1. SSH keys are configured for passwordless login"
  echo "  2. Host is accessible: ${REMOTE_HOST}"
  exit 1
fi

# Create remote directory if it doesn't exist
echo -e "${YELLOW}Creating remote directory (if needed)...${NC}"
ssh "${REMOTE_USER}@${REMOTE_HOST}" "mkdir -p ${REMOTE_DIR}" || {
  echo "ERROR: Failed to create remote directory"
  exit 1
}

# Sync files using rsync (excluding git, archive, cache, etc.)
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
  --exclude '.nextflow/' \
  --exclude 'work/' \
  --exclude '*.fasta' \
  --exclude '*.fastq' \
  --exclude '*.ab1' \
  --exclude '*.pdf' \
  --exclude '*.csv' \
  --exclude '*.tsv' \
  --exclude 'config.yaml' \
  --exclude '.DS_Store' \
  --exclude '*.tmp' \
  --exclude '*.temp' \
  --exclude 'nanopore_plasmid_pipeline_v1.0.zip' \
  "${LOCAL_DIR}/" \
  "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"

echo ""
echo -e "${GREEN}✓ Sync completed!${NC}"
echo ""
echo "Files synced to: ${REMOTE_DIR}"
echo ""
echo "To connect to test server:"
echo "  ssh ${REMOTE_USER}@${REMOTE_HOST}"
echo ""
echo "To build and test Docker image:"
echo "  ssh ${REMOTE_USER}@${REMOTE_HOST} 'cd ${REMOTE_DIR} && docker build -t nanopore-plasmid-pipeline:latest .'"

