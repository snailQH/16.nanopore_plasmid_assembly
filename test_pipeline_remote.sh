#!/bin/bash
# Test pipeline on remote server

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
echo "Testing Nanopore Plasmid Pipeline"
echo "=========================================="

${SSH_CMD} << 'ENDSSH'
set -e

REMOTE_DIR="/data1/opt/nanopore_plasmid_pipeline/cursor_pipeline"
TEST_DATA_DIR="/data1/opt/nanopore_plasmid_pipeline/fast_pass"
OUTPUT_DIR="/data1/opt/nanopore_plasmid_pipeline/test_output"

echo "Checking test data..."
if [ -d "${TEST_DATA_DIR}" ]; then
    echo "Test data directory: ${TEST_DATA_DIR}"
    echo "Sample directories:"
    ls -d ${TEST_DATA_DIR}/*/ 2>/dev/null | head -5 | xargs -n1 basename
else
    echo "ERROR: Test data directory not found: ${TEST_DATA_DIR}"
    exit 1
fi

echo ""
echo "Creating output directory..."
mkdir -p ${OUTPUT_DIR}
chmod 755 ${OUTPUT_DIR}

echo ""
echo "=========================================="
echo "Running pipeline (Step 0: Initialization)"
echo "=========================================="
cd ${REMOTE_DIR}

docker run --rm \
  --entrypoint python3 \
  -v ${TEST_DATA_DIR}:/data/input/fast_pass:ro \
  -v ${OUTPUT_DIR}:/data/output \
  nanopore-plasmid-pipeline:latest \
  /opt/pipeline/scripts/step0_initialize_analysis.py \
    --input /data/input \
    --output /data/output \
    --project-id test_run \
    --verbose

echo ""
echo "=========================================="
echo "Checking initialization results..."
echo "=========================================="
ls -la ${OUTPUT_DIR}/config.yaml 2>/dev/null && echo "✓ Config file created" || echo "✗ Config file missing"
ls -d ${OUTPUT_DIR}/01.* 2>/dev/null | head -3

echo ""
echo "=========================================="
echo "Testing samplesheet generation..."
echo "=========================================="
docker run --rm \
  --entrypoint python3 \
  -v ${TEST_DATA_DIR}:/data/input/fast_pass:ro \
  -v ${OUTPUT_DIR}:/data/output \
  nanopore-plasmid-pipeline:latest \
  /opt/pipeline/scripts/generate_samplesheet.py \
    --fast-pass /data/input/fast_pass \
    --out /data/output/test_samplesheet.csv

if [ -f "${OUTPUT_DIR}/test_samplesheet.csv" ]; then
    echo "✓ Samplesheet generated"
    head -5 ${OUTPUT_DIR}/test_samplesheet.csv
else
    echo "✗ Samplesheet generation failed"
fi

echo ""
echo "=========================================="
echo "Ready for full pipeline test!"
echo "=========================================="
echo "To run full pipeline:"
echo "  cd ${REMOTE_DIR}"
echo "  docker run --rm \\"
echo "    -v ${TEST_DATA_DIR}:/data/input/fast_pass:ro \\"
echo "    -v ${OUTPUT_DIR}:/data/output \\"
echo "    nanopore-plasmid-pipeline:latest \\"
echo "    --input /data/input \\"
echo "    --output /data/output \\"
echo "    --project-id test_run \\"
echo "    --verbose"

ENDSSH

echo ""
echo "Test script completed!"

