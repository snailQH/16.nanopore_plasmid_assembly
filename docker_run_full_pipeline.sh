#!/bin/bash
# Run the complete pipeline inside Docker container
# This script wraps run_pipeline.sh and allows full pipeline execution in Docker
#
# Usage:
#   ./docker_run_full_pipeline.sh --input /path/to/input --output /path/to/output ...
#
# Requirements:
#   - Docker socket must be accessible (/var/run/docker.sock)
#   - Input and output directories must be accessible

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCKER_IMAGE="${DOCKER_IMAGE:-nanopore-plasmid-pipeline:latest}"

# Check if Docker image exists
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${DOCKER_IMAGE}$"; then
    echo "ERROR: Docker image not found: ${DOCKER_IMAGE}"
    echo "Please build the image first:"
    echo "  docker build -t ${DOCKER_IMAGE} ."
    exit 1
fi

# Build docker run command
DOCKER_RUN_ARGS=(
    --rm
    -it
    # Mount Docker socket for Nextflow to run process containers
    -v /var/run/docker.sock:/var/run/docker.sock
    # Mount input directory (read-only)
    # Mount output directory (read-write)
    # Mount scripts directory to use local scripts (optional, can use image scripts)
    -v "${SCRIPT_DIR}/scripts:/opt/pipeline/scripts:ro"
    # Mount run_pipeline.sh
    -v "${SCRIPT_DIR}/run_pipeline.sh:/opt/pipeline/run_pipeline.sh:ro"
    # Set working directory
    -w /opt/pipeline
    # Use entrypoint that supports bash
    --entrypoint /bin/bash
    "$DOCKER_IMAGE"
)

# Pass all arguments to run_pipeline.sh
# Note: Paths need to be adjusted for container filesystem
# Input and output paths will be mounted separately

echo "=========================================="
echo "Running full pipeline inside Docker"
echo "=========================================="
echo "Docker image: ${DOCKER_IMAGE}"
echo "Script directory: ${SCRIPT_DIR}"
echo ""
echo "NOTE: This will run the complete pipeline inside Docker container"
echo "      including Nextflow (with Docker socket access)"
echo ""

# Run the pipeline script inside container
# We need to adjust paths - mount input/output as volumes and use container paths
docker run "${DOCKER_RUN_ARGS[@]}" \
    -c "./run_pipeline.sh \"\$@\"" \
    -- "$@"

