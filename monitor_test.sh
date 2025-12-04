#!/bin/bash
# Monitor pipeline test execution and log files

set -e

REMOTE_HOST="localhost"
REMOTE_PORT="2222"
REMOTE_USER="bioinfo"
REMOTE_PASS="ampseq@2025"
JUMP_HOST="root@8.133.18.117"
OUTPUT_DIR="/data1/opt/nanopore_plasmid_pipeline/test_output"
LOGS_DIR="${OUTPUT_DIR}/logs"

SSH_CMD="sshpass -p '${REMOTE_PASS}' ssh -o StrictHostKeyChecking=no -J ${JUMP_HOST} -p ${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST}"

echo "=========================================="
echo "Monitoring Pipeline Test Execution"
echo "=========================================="
echo "Logs directory: ${LOGS_DIR}"
echo ""

# Function to check log files
check_logs() {
    ${SSH_CMD} << 'ENDSSH'
LOGS_DIR="/data1/opt/nanopore_plasmid_pipeline/test_output/logs"

echo "Current log files:"
if [ -d "${LOGS_DIR}" ]; then
    ls -lh ${LOGS_DIR}/*.log 2>/dev/null | awk '{print $9, "(" $5 ")"}'
    echo ""
    echo "Latest log entries (last 5 lines of each):"
    for log_file in ${LOGS_DIR}/*.log; do
        if [ -f "${log_file}" ]; then
            echo "--- $(basename ${log_file}) ---"
            tail -5 "${log_file}" 2>/dev/null || echo "(empty)"
            echo ""
        fi
    done
else
    echo "Logs directory does not exist yet"
fi
ENDSSH
}

# Monitor loop
while true; do
    clear
    echo "=========================================="
    echo "Pipeline Test Monitor - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    check_logs
    echo "Press Ctrl+C to stop monitoring"
    sleep 10
done

