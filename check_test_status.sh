#!/bin/bash
# Quick check of test status and log files

REMOTE_HOST="localhost"
REMOTE_PORT="2222"
REMOTE_USER="bioinfo"
REMOTE_PASS="ampseq@2025"
JUMP_HOST="root@8.133.18.117"
OUTPUT_DIR="/data1/opt/nanopore_plasmid_pipeline/test_output"
LOGS_DIR="${OUTPUT_DIR}/logs"

SSH_CMD="sshpass -p '${REMOTE_PASS}' ssh -o StrictHostKeyChecking=no -J ${JUMP_HOST} -p ${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST}"

${SSH_CMD} << 'ENDSSH'
OUTPUT_DIR="/data1/opt/nanopore_plasmid_pipeline/test_output"
LOGS_DIR="${OUTPUT_DIR}/logs"

echo "=========================================="
echo "Pipeline Test Status Check"
echo "=========================================="
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Check if pipeline is running
echo "=== Pipeline Process ==="
if pgrep -f "run_pipeline.py" > /dev/null; then
    echo "✓ Pipeline is running"
    ps aux | grep "run_pipeline.py" | grep -v grep | head -1
else
    echo "✗ Pipeline is not running"
fi
echo ""

# Check log files
echo "=== Log Files ==="
if [ -d "${LOGS_DIR}" ]; then
    echo "Log files in ${LOGS_DIR}:"
    ls -lh ${LOGS_DIR}/*.log 2>/dev/null | awk '{printf "  %-35s %8s\n", $9, $5}'
    echo ""
    
    # Show latest entries from each log
    echo "=== Latest Log Entries (last 3 lines) ==="
    for log_file in ${LOGS_DIR}/*.log; do
        if [ -f "${log_file}" ]; then
            echo ""
            echo "--- $(basename ${log_file}) ---"
            tail -3 "${log_file}" 2>/dev/null | sed 's/^/  /'
        fi
    done
else
    echo "Logs directory does not exist yet: ${LOGS_DIR}"
fi
echo ""

# Check output directories
echo "=== Output Directories ==="
if [ -d "${OUTPUT_DIR}" ]; then
    for dir in 01.assembly 02.fragments 03.ab1_files 04.reports logs; do
        if [ -d "${OUTPUT_DIR}/${dir}" ]; then
            count=$(find "${OUTPUT_DIR}/${dir}" -type f 2>/dev/null | wc -l)
            echo "  ${dir}/: ${count} files"
        else
            echo "  ${dir}/: not created yet"
        fi
    done
else
    echo "Output directory does not exist: ${OUTPUT_DIR}"
fi

ENDSSH

