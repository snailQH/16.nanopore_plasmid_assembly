#!/bin/bash
# Run full pipeline test on remote server

set -e

REMOTE_HOST="localhost"
REMOTE_PORT="2222"
REMOTE_USER="bioinfo"
REMOTE_PASS="ampseq@2025"
JUMP_HOST="root@8.133.18.117"
REMOTE_DIR="/data1/opt/nanopore_plasmid_pipeline/cursor_pipeline"
TEST_DATA_DIR="/data1/opt/nanopore_plasmid_pipeline/fast_pass"
OUTPUT_DIR="/data1/opt/nanopore_plasmid_pipeline/test_output"

SSH_CMD="sshpass -p '${REMOTE_PASS}' ssh -o StrictHostKeyChecking=no -J ${JUMP_HOST} -p ${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST}"

echo "=========================================="
echo "Running Full Pipeline Test"
echo "=========================================="

${SSH_CMD} << 'ENDSSH'
set -e

REMOTE_DIR="/data1/opt/nanopore_plasmid_pipeline/cursor_pipeline"
TEST_DATA_DIR="/data1/opt/nanopore_plasmid_pipeline/fast_pass"
OUTPUT_DIR="/data1/opt/nanopore_plasmid_pipeline/test_output"

cd ${REMOTE_DIR}

echo "Cleaning previous test output..."
rm -rf ${OUTPUT_DIR}/*
mkdir -p ${OUTPUT_DIR}

echo ""
echo "=========================================="
echo "Running complete pipeline..."
echo "=========================================="
echo "This may take a while..."
echo ""

# Run full pipeline
# Note: epi2me workflow requires Docker socket for -profile docker
docker run --rm \
  -v ${TEST_DATA_DIR}:/data/input/fast_pass:ro \
  -v ${OUTPUT_DIR}:/data/output \
  -v /var/run/docker.sock:/var/run/docker.sock \
  nanopore-plasmid-pipeline:latest \
  --input /data/input \
  --output /data/output \
  --project-id test_run \
  --approx-size 5000 \
  --coverage 50 \
  --verbose 2>&1 | tee ${OUTPUT_DIR}/pipeline.log

echo ""
echo "=========================================="
echo "Pipeline execution completed!"
echo "=========================================="
echo ""
echo "Checking outputs..."

if [ -f "${OUTPUT_DIR}/config.yaml" ]; then
    echo "✓ Config file exists"
else
    echo "✗ Config file missing"
fi

if [ -d "${OUTPUT_DIR}/01.assembly" ]; then
    echo "✓ Assembly directory exists"
    ls -la ${OUTPUT_DIR}/01.assembly/ | head -10
else
    echo "✗ Assembly directory missing"
fi

if [ -d "${OUTPUT_DIR}/02.fragments" ]; then
    echo "✓ Fragments directory exists"
    ls -la ${OUTPUT_DIR}/02.fragments/ | head -5
else
    echo "⚠ Fragments directory missing (may be skipped)"
fi

if [ -d "${OUTPUT_DIR}/03.ab1_files" ]; then
    echo "✓ AB1 files directory exists"
    ls -la ${OUTPUT_DIR}/03.ab1_files/ | head -5
else
    echo "⚠ AB1 files directory missing (may be skipped)"
fi

if [ -d "${OUTPUT_DIR}/04.reports" ]; then
    echo "✓ Reports directory exists"
    find ${OUTPUT_DIR}/04.reports -name "*.pdf" | head -5
else
    echo "⚠ Reports directory missing (may be skipped)"
fi

echo ""
echo "Full log available at: ${OUTPUT_DIR}/pipeline.log"

ENDSSH

echo ""
echo "Full pipeline test completed!"

