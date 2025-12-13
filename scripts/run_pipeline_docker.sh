#!/bin/bash
# Pipeline entry script that can run fully inside Docker container
# This version assumes all paths are container-relative
# 
# Usage (inside Docker):
#   bash /opt/pipeline/scripts/run_pipeline_docker.sh \
#     --input /data/input --output /data/output --project-id PROJECT_ID

set -e

# Import the main run_pipeline.sh logic
# This script is designed to be called from within Docker container
# It uses the same logic as run_pipeline.sh but with Docker-in-Docker support

SCRIPT_DIR="/opt/pipeline"
PYTHON_SCRIPT_DIR="${SCRIPT_DIR}/scripts"

# Source common functions if available, otherwise define log function
if ! command -v log &> /dev/null; then
    log() {
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    }
fi

log "=========================================="
log "Nanopore Plasmid Assembly Pipeline"
log "Running inside Docker container"
log "=========================================="

# Check if Docker socket is available (required for Nextflow)
if [[ ! -S /var/run/docker.sock ]]; then
    log "WARNING: Docker socket not found at /var/run/docker.sock"
    log "WARNING: Nextflow may not be able to run process containers"
    log "WARNING: Ensure Docker socket is mounted: -v /var/run/docker.sock:/var/run/docker.sock"
fi

# Check if docker command is available
if ! command -v docker &> /dev/null; then
    log "ERROR: docker command not found in container"
    log "ERROR: Docker CLI must be installed in the image"
    exit 1
fi

# The main pipeline logic will be handled by Python script
# which can better handle Docker-in-Docker scenarios
log "Delegating to Python pipeline script..."
exec python3 "${PYTHON_SCRIPT_DIR}/run_pipeline.py" "$@"

