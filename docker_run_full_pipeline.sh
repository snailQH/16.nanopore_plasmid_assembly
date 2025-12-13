#!/bin/bash
# Wrapper script to run the entire Nanopore Plasmid Assembly Pipeline
# directly within a Docker container.
# This script mounts the Docker socket to allow Nextflow to run its
# process containers (medaka, flye, etc.) inside the main pipeline container.

set -e

# Default values
PROJECT_ID="auto"
INPUT_DIR=""
OUTPUT_DIR=""
FRAGMENT_SIZE=2000
APPROX_SIZE=5000
COVERAGE=50
PRIMERS_FILE=""
VERBOSE=false

# Docker image name
DOCKER_IMAGE="nanopore-plasmid-pipeline:latest"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --input|-i)
            INPUT_DIR="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        --fragment-size)
            FRAGMENT_SIZE="$2"
            shift 2
            ;;
        --approx-size)
            APPROX_SIZE="$2"
            shift 2
            ;;
        --coverage)
            COVERAGE="$2"
            shift 2
            ;;
        --primers)
            PRIMERS_FILE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$INPUT_DIR" || -z "$OUTPUT_DIR" ]]; then
    echo "Usage: $0 --input <input_dir> --output <output_dir> [--project-id <id>] [--approx-size <bp>] [--coverage <x>] [--primers <file>] [-v|--verbose]"
    exit 1
fi

# Ensure output directory exists on host before mounting
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "Running Nanopore Plasmid Assembly Pipeline (Full Docker Mode)"
echo "=========================================="
echo "Input directory: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo "Project ID: $PROJECT_ID"
echo "Approx. Size: $APPROX_SIZE"
echo "Coverage: $COVERAGE"
echo "Primers file: ${PRIMERS_FILE:-N/A}"
echo "Verbose: $VERBOSE"
echo "Docker Image: $DOCKER_IMAGE"
echo "=========================================="
echo ""

# Build Docker run command
# IMPORTANT: Pass HOST_INPUT_DIR and HOST_OUTPUT_DIR so sub-containers can mount them
DOCKER_RUN_CMD=(
    docker run --rm -it
    -v /var/run/docker.sock:/var/run/docker.sock  # Crucial for Nextflow to run Docker processes
    -v "${INPUT_DIR}:/data/input:ro"
    -v "${OUTPUT_DIR}:/data/output"
    -e "HOST_OUTPUT_DIR=${OUTPUT_DIR}"  # Pass host output path for sub-containers
    -e "HOST_INPUT_DIR=${INPUT_DIR}"    # Pass host input path for sub-containers
    "$DOCKER_IMAGE"
    --input /data/input
    --output /data/output
    --project-id "$PROJECT_ID"
    --approx-size "$APPROX_SIZE"
    --coverage "$COVERAGE"
    --fragment-size "$FRAGMENT_SIZE"
)

if [[ -n "$PRIMERS_FILE" ]]; then
    DOCKER_RUN_CMD+=(-v "${PRIMERS_FILE}:/data/primers.tsv:ro" --primers /data/primers.tsv)
fi

if [[ "$VERBOSE" == "true" ]]; then
    DOCKER_RUN_CMD+=(--verbose)
fi

echo "Executing Docker command:"
echo "${DOCKER_RUN_CMD[@]}"
echo ""

# Execute the Docker command
"${DOCKER_RUN_CMD[@]}"