#!/bin/bash
# Build Docker and test on remote server

set -e

# Configuration
REMOTE_HOST="localhost"
REMOTE_PORT="2222"
REMOTE_USER="bioinfo"
REMOTE_PASS="ampseq@2025"
JUMP_HOST="root@8.133.18.117"
REMOTE_DIR="/data1/opt/nanopore_plasmid_pipeline/cursor_pipeline"
TEST_DATA_DIR="/data1/opt/nanopore_plasmid_pipeline/fast_pass"
OUTPUT_DIR="/data1/opt/nanopore_plasmid_pipeline/test_output"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Connecting to remote server and building Docker...${NC}"

# SSH command with jump host
SSH_CMD="sshpass -p '${REMOTE_PASS}' ssh -o StrictHostKeyChecking=no -J ${JUMP_HOST} -p ${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST}"

# Execute commands on remote server
${SSH_CMD} << 'ENDSSH'
set -e

REMOTE_DIR="/data1/opt/nanopore_plasmid_pipeline/cursor_pipeline"
TEST_DATA_DIR="/data1/opt/nanopore_plasmid_pipeline/fast_pass"
OUTPUT_DIR="/data1/opt/nanopore_plasmid_pipeline/test_output"

echo "=========================================="
echo "Checking remote directory..."
echo "=========================================="
cd ${REMOTE_DIR}
pwd
ls -la

echo ""
echo "=========================================="
echo "Checking Docker installation..."
echo "=========================================="
docker --version || echo "Docker not found"
docker-compose --version || echo "Docker Compose not found"

echo ""
echo "=========================================="
echo "Checking test data..."
echo "=========================================="
if [ -d "${TEST_DATA_DIR}" ]; then
    echo "Test data directory exists: ${TEST_DATA_DIR}"
    ls -la ${TEST_DATA_DIR} | head -10
    echo ""
    echo "Sample subdirectories:"
    find ${TEST_DATA_DIR} -maxdepth 1 -type d | head -5
else
    echo "WARNING: Test data directory not found: ${TEST_DATA_DIR}"
fi

echo ""
echo "=========================================="
echo "Building Docker image..."
echo "=========================================="
cd ${REMOTE_DIR}
docker build -t nanopore-plasmid-pipeline:latest . 2>&1 | tee docker_build.log

echo ""
echo "=========================================="
echo "Docker build completed!"
echo "=========================================="
docker images | grep nanopore-plasmid-pipeline || echo "Image not found"

echo ""
echo "=========================================="
echo "Creating output directory..."
echo "=========================================="
mkdir -p ${OUTPUT_DIR}
chmod 755 ${OUTPUT_DIR}

echo ""
echo "=========================================="
echo "Ready for testing!"
echo "=========================================="
echo "To run the pipeline:"
echo "  cd ${REMOTE_DIR}"
echo "  docker run --rm \\"
echo "    -v ${TEST_DATA_DIR}:/data/input/fast_pass:ro \\"
echo "    -v ${OUTPUT_DIR}:/data/output \\"
echo "    nanopore-plasmid-pipeline:latest \\"
echo "    --input /data/input \\"
echo "    --output /data/output \\"
echo "    --project-id test_run"

ENDSSH

echo -e "${GREEN}Remote build script completed!${NC}"

