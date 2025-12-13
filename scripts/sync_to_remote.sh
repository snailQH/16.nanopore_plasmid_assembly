#!/bin/bash
# Sync code to remote server for Docker rebuild
# 
# Usage:
#   ./scripts/sync_to_remote.sh
#   ./scripts/sync_to_remote.sh /opt/nanopore_plasmid_pipeline/cursor_pipeline

set -e

# Default remote path
REMOTE_PATH="${1:-/opt/nanopore_plasmid_pipeline/cursor_pipeline}"
REMOTE_USER="${REMOTE_USER:-qinghuili}"
REMOTE_HOST="${REMOTE_HOST:-localhost}"
REMOTE_PORT="${REMOTE_PORT:-2223}"
JUMP_HOST="${JUMP_HOST:-root@8.133.18.117}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "Syncing code to remote server"
echo "=========================================="
echo "Remote path: ${REMOTE_PATH}"
echo "Remote host: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PORT}"
echo "Jump host: ${JUMP_HOST}"
echo ""

# Check if SSH connection works
echo "Testing SSH connection..."
if ssh -J "${JUMP_HOST}" "${REMOTE_USER}@${REMOTE_HOST}" -p "${REMOTE_PORT}" "echo 'Connection successful'" 2>/dev/null; then
    echo "✓ SSH connection successful"
else
    echo "ERROR: Cannot connect to remote server"
    echo "Please check:"
    echo "  1. SSH keys are configured"
    echo "  2. Jump host is accessible: ${JUMP_HOST}"
    echo "  3. Remote host is accessible: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PORT}"
    exit 1
fi

# Create remote directory if it doesn't exist (check if user has permission)
echo "Creating remote directory (if needed)..."
ssh -J "${JUMP_HOST}" "${REMOTE_USER}@${REMOTE_HOST}" -p "${REMOTE_PORT}" \
    "mkdir -p ${REMOTE_PATH} 2>/dev/null || { echo 'Note: Cannot create ${REMOTE_PATH}, attempting to sync to existing directory...'; exit 0; }"

# Sync files using rsync
echo "Syncing files..."
rsync -avz --delete \
    -e "ssh -J ${JUMP_HOST} -p ${REMOTE_PORT}" \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '*.log' \
    --exclude 'output/' \
    --exclude 'results/' \
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
    "${PROJECT_DIR}/" \
    "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/"

echo ""
echo "✓ Code sync completed"
echo ""
echo "Next steps:"
echo "  1. SSH to remote server:"
echo "     ssh -J ${JUMP_HOST} ${REMOTE_USER}@${REMOTE_HOST} -p ${REMOTE_PORT}"
echo ""
echo "  2. Navigate to project directory:"
echo "     cd ${REMOTE_PATH}"
echo ""
echo "  3. Build Docker image:"
echo "     docker build -t nanopore-plasmid-pipeline:latest ."
echo ""

