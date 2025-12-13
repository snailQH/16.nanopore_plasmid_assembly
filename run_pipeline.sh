#!/bin/bash
# Main pipeline entry script
# This script runs on the HOST machine and orchestrates:
# 1. Docker container for initialization and configuration
# 2. Nextflow on HOST for epi2me workflow (requires Docker for processes)
# 3. Docker container for fragment splitting, AB1 generation, and reports

set -e

# Handle log redirection early: if stdout is redirected to a file,
# create the directory first, then reopen the log file
if [[ ! -t 1 ]] && [[ -n "${BASH_SOURCE[0]}" ]]; then
    # stdout is not a terminal (redirected)
    # Try to detect if it's redirected to a file in an output directory
    # We'll handle this after parsing --output argument
    LOG_REDIRECTED=true
else
    LOG_REDIRECTED=false
fi

# Default values
PROJECT_ID=""
INPUT_DIR=""
OUTPUT_DIR=""
FRAGMENT_SIZE=2000
APPROX_SIZE=5000
COVERAGE=50
PRIMERS_FILE=""
VERBOSE=false
SKIP_ASSEMBLY=false
SKIP_FRAGMENTS=false
SKIP_AB1=false
SKIP_REPORTS=false

# Docker image name
# Priority: 1. Environment variable DOCKER_IMAGE, 2. Local image, 3. Docker Hub image
if [[ -n "${DOCKER_IMAGE:-}" ]]; then
    # Use environment variable if set
    DOCKER_IMAGE="${DOCKER_IMAGE}"
elif docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^nanopore-plasmid-pipeline:latest$"; then
    # Use local image if available
    DOCKER_IMAGE="nanopore-plasmid-pipeline:latest"
else
    # Fallback to Docker Hub image
    DOCKER_IMAGE="snailqh/nanopore-plasmid-pipeline:ampseq"
fi

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --input|-i)
            INPUT_DIR="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT_DIR="$2"
            # Create output directory immediately to allow log redirection
            # Shell processes redirection before script execution, so we need
            # to create the directory as soon as we know where it is
            mkdir -p "$OUTPUT_DIR" 2>/dev/null || true
            # If log is redirected and it's to this output directory, reopen it
            if [[ "$LOG_REDIRECTED" == "true" ]] && [[ -n "${BASH_SOURCE[0]}" ]]; then
                # Check if stdout is redirected to a file in OUTPUT_DIR
                # We'll handle this after all arguments are parsed
                OUTPUT_DIR_SET=true
            fi
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
        --skip-assembly)
            SKIP_ASSEMBLY=true
            shift
            ;;
        --skip-fragments)
            SKIP_FRAGMENTS=true
            shift
            ;;
        --skip-ab1)
            SKIP_AB1=true
            shift
            ;;
        --skip-reports)
            SKIP_REPORTS=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 --input INPUT_DIR --output OUTPUT_DIR [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --input, -i          Input directory containing fastq/ or fast_pass/ folder"
            echo "                       Or directly specify fastq directory path"
            echo "  --output, -o         Output directory for results"
            echo "  --project-id         Project ID (auto-generated if not provided)"
            echo "  --fragment-size      Fragment size for splitting (default: 2000)"
            echo "  --approx-size        Approximate plasmid size (default: 5000)"
            echo "  --coverage           Target coverage (default: 50)"
            echo "  --skip-assembly     Skip assembly step"
            echo "  --skip-fragments     Skip fragment splitting"
            echo "  --skip-ab1          Skip AB1 generation"
            echo "  --skip-reports       Skip report generation"
            echo "  --verbose, -v       Enable verbose logging"
            echo "  --help, -h          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$INPUT_DIR" ]] || [[ -z "$OUTPUT_DIR" ]]; then
    echo "ERROR: --input and --output are required"
    echo "Use --help for usage information"
    exit 1
fi

# Create output directory FIRST (before realpath) to allow log redirection
# This ensures the directory exists even if user redirects logs to a file in it
mkdir -p "$OUTPUT_DIR"

# Convert to absolute paths (now safe since directory exists)
INPUT_DIR=$(realpath "$INPUT_DIR")
OUTPUT_DIR=$(realpath "$OUTPUT_DIR")

# Create output directory structure with proper permissions
# This ensures Docker containers can write to these directories
mkdir -p "$OUTPUT_DIR"/{01.assembly,02.fragments,03.ab1_files,04.reports,logs}
chmod -R 755 "$OUTPUT_DIR"  # Ensure directories are writable

# Create .nextflow directory in assembly output (needed by Nextflow)
mkdir -p "$OUTPUT_DIR/01.assembly/.nextflow"
chmod 755 "$OUTPUT_DIR/01.assembly/.nextflow"

# Log file - always log to OUTPUT_DIR/logs/pipeline.log
# If user redirects stdout, we'll also output there, but internal log goes here
LOG_FILE="$OUTPUT_DIR/logs/pipeline.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Define log function (must be defined before first use)
# This function logs to both LOG_FILE and stdout
# If stdout is redirected, it will go there too
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Nanopore Plasmid Assembly Pipeline"
log "=========================================="
log "Input directory: $INPUT_DIR"
log "Output directory: $OUTPUT_DIR"
log "Project ID: ${PROJECT_ID:-auto-generated}"
log ""

# Step 0: Initialization (in Docker)
log "=========================================="
log "[Step 0] Initialization and Configuration"
log "=========================================="
log ""
log "Using Docker image: $DOCKER_IMAGE"
# Check if image exists locally, if not, try to pull from Docker Hub
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${DOCKER_IMAGE}$"; then
    if [[ "$DOCKER_IMAGE" == "snailqh/nanopore-plasmid-pipeline"* ]] || [[ "$DOCKER_IMAGE" == "ampseq/nanopore-plasmid-pipeline"* ]] || [[ "$DOCKER_IMAGE" == *"/nanopore-plasmid-pipeline"* ]]; then
        log "Docker Hub image not found locally. Attempting to pull..."
        if docker pull "$DOCKER_IMAGE" 2>&1 | tee -a "$LOG_FILE"; then
            log "✓ Successfully pulled Docker Hub image"
        else
            log "ERROR: Failed to pull Docker image from Docker Hub: $DOCKER_IMAGE"
            log "Please ensure:"
            log "  1. Docker is running"
            log "  2. You have internet connection"
            log "  3. Image name is correct: $DOCKER_IMAGE"
            log ""
            log "Alternatively, build locally:"
            log "  docker build -t nanopore-plasmid-pipeline:latest ."
            exit 1
        fi
    else
        log "ERROR: Docker image not found: $DOCKER_IMAGE"
        log "Please build the image first:"
        log "  docker build -t nanopore-plasmid-pipeline:latest ."
        log ""
        log "Or use Docker Hub image by setting:"
        log "  export DOCKER_IMAGE=ampseq/nanopore-plasmid-pipeline:latest"
        exit 1
    fi
else
    log "✓ Docker image found locally"
fi
log ""
log "Running initialization in Docker container..."

DOCKER_ARGS=(
    --rm
    -v "$INPUT_DIR:/data/input:ro"
    -v "$OUTPUT_DIR:/data/output"
)

# Build Python script arguments
# Note: step0_initialize_analysis.py generates config.yaml itself, doesn't accept --config
PYTHON_ARGS=(
    --input /data/input
    --output /data/output
    --project-id "${PROJECT_ID:-auto}"
    --approx-size "$APPROX_SIZE"
    --coverage "$COVERAGE"
)

if [[ "$VERBOSE" == "true" ]]; then
    PYTHON_ARGS+=(--verbose)
fi

log "Docker command: docker run ${DOCKER_ARGS[*]} --entrypoint python3 $DOCKER_IMAGE /opt/pipeline/scripts/step0_initialize_analysis.py ${PYTHON_ARGS[*]}"

docker run "${DOCKER_ARGS[@]}" \
    --entrypoint python3 \
    "$DOCKER_IMAGE" \
    /opt/pipeline/scripts/step0_initialize_analysis.py \
    "${PYTHON_ARGS[@]}" 2>&1 | tee -a "$LOG_FILE" || {
    log "ERROR: Initialization failed"
    exit 1
}

log "✓ Initialization complete"
log ""

# Step 1: Assembly using Nextflow (on HOST)
if [[ "$SKIP_ASSEMBLY" != "true" ]]; then
    log "=========================================="
    log "[Step 1] Running epi2me wf-clone-validation"
    log "=========================================="
    log "Running Nextflow on HOST machine..."
    log "Note: Nextflow will use Docker containers for processes (medaka, flye, etc.)"
    log ""
    
    # Find fastq/fast_pass directory
    # User can specify:
    # 1. Parent directory containing fastq/ or fast_pass/ subdirectory
    # 2. Direct fastq/fast_pass directory path
    # 3. Parent directory containing subdirectories with *-Raw/ or similar patterns
    if [[ -d "$INPUT_DIR/fastq" ]]; then
        # Demo data structure: wf-clone-validation-demo/fastq/
        FASTQ_DIR="$INPUT_DIR/fastq"
    elif [[ -d "$INPUT_DIR/fast_pass" ]]; then
        # Standard structure: input_dir/fast_pass/
        FASTQ_DIR="$INPUT_DIR/fast_pass"
    elif [[ -d "$INPUT_DIR" ]] && ([[ "$(basename "$INPUT_DIR")" == "fastq" ]] || [[ "$(basename "$INPUT_DIR")" == "fast_pass" ]]); then
        # Input directory is directly the fastq/fast_pass directory
        FASTQ_DIR="$INPUT_DIR"
    else
        # Check if INPUT_DIR itself contains sample subdirectories with FASTQ files
        # Look for subdirectories containing FASTQ files directly
        SAMPLE_DIRS_WITH_FASTQ=$(find "$INPUT_DIR" -maxdepth 2 -type d -exec sh -c 'find "$1" -maxdepth 1 -name "*.fastq*" -o -name "*.fq*" | head -1 | grep -q .' _ {} \; -print 2>/dev/null | head -1)
        
        if [[ -n "$SAMPLE_DIRS_WITH_FASTQ" ]]; then
            # Found subdirectories with FASTQ files, check if they're nested
            # If parent directory has multiple subdirectories, use parent as FASTQ_DIR
            PARENT_DIR=$(dirname "$SAMPLE_DIRS_WITH_FASTQ")
            if [[ "$PARENT_DIR" != "$INPUT_DIR" ]] && [[ -d "$PARENT_DIR" ]]; then
                # Check if this looks like a project directory (e.g., CT121125GS-Raw/)
                if [[ "$(basename "$PARENT_DIR")" =~ .*-Raw$ ]] || [[ "$(basename "$PARENT_DIR")" =~ .*-raw$ ]]; then
                    FASTQ_DIR="$PARENT_DIR"
                    log "Detected project directory structure: $(basename "$FASTQ_DIR")"
                else
                    FASTQ_DIR="$PARENT_DIR"
                fi
            else
                FASTQ_DIR="$INPUT_DIR"
            fi
        else
            # Last resort: check if INPUT_DIR itself contains FASTQ files directly
            if find "$INPUT_DIR" -maxdepth 2 -name "*.fastq*" -o -name "*.fq*" 2>/dev/null | head -1 | grep -q .; then
                FASTQ_DIR="$INPUT_DIR"
            else
                log "ERROR: Could not find fastq or fast_pass directory in: $INPUT_DIR"
                log "Expected structure:"
                log "  - input_dir/fastq/ or input_dir/fast_pass/ with sample subdirectories"
                log "  - input_dir/*-Raw/ with sample subdirectories containing FASTQ files"
                exit 1
            fi
        fi
    fi
    
    log "Detected FASTQ directory: $FASTQ_DIR"
    
    # Generate samplesheet
    # Note: samplesheet generation will merge multiple FASTQ files per sample (if needed)
    # and create barcode directories with merged files if directory names don't match barcode format
    # We need to mount fast_pass as read-write (not :ro) to allow directory/file creation
    SAMPLESHEET="$OUTPUT_DIR/01.assembly/samplesheet.csv"
    mkdir -p "$(dirname "$SAMPLESHEET")"
    
    log "Generating samplesheet..."
    log "Note: Multiple FASTQ files per sample will be merged, and barcode directories will be created if needed"
    
    # Validate FASTQ_DIR is set and exists
    if [[ -z "$FASTQ_DIR" ]] || [[ ! -d "$FASTQ_DIR" ]]; then
        log "ERROR: FASTQ directory not found or invalid: ${FASTQ_DIR:-<empty>}"
        exit 1
    fi
    
    # Optionally mount local scripts directory (for development/testing without rebuild)
    # Set USE_LOCAL_SCRIPTS=1 environment variable to enable
    DOCKER_RUN_ARGS=(
        --rm
        -v "${FASTQ_DIR}:/data/input/fastq"
        -v "$(dirname "$SAMPLESHEET"):/data/output"
    )
    
    if [[ "${USE_LOCAL_SCRIPTS:-0}" == "1" ]]; then
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        DOCKER_RUN_ARGS+=(-v "${SCRIPT_DIR}/scripts:/opt/pipeline/scripts:ro")
        log "Using local scripts from: ${SCRIPT_DIR}/scripts"
    fi
    
    docker run "${DOCKER_RUN_ARGS[@]}" \
        --entrypoint python3 \
        "$DOCKER_IMAGE" \
        /opt/pipeline/scripts/generate_samplesheet.py \
        --fast-pass /data/input/fastq \
        --out /data/output/samplesheet.csv \
        --approx-size "$APPROX_SIZE" || {
        log "ERROR: Samplesheet generation failed"
        exit 1
    }
    
    log "Running Nextflow workflow..."
    log "Command: NXF_VER=23.10.0 nextflow run epi2me-labs/wf-clone-validation -r v1.8.3 ..."
    
    # Check if Nextflow is installed
    NEXTFLOW_CMD=""
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    
    if command -v nextflow &> /dev/null; then
        # Use full path from 'which' to avoid path resolution issues
        NEXTFLOW_CMD=$(which nextflow)
        log "Found Nextflow in PATH: $NEXTFLOW_CMD"
    elif [[ -f "$SCRIPT_DIR/nextflow" ]]; then
        NEXTFLOW_CMD="$SCRIPT_DIR/nextflow"
        log "Found Nextflow in script directory: $NEXTFLOW_CMD"
    elif [[ -f "$HOME/bin/nextflow" ]]; then
        NEXTFLOW_CMD="$HOME/bin/nextflow"
        log "Found Nextflow in ~/bin: $NEXTFLOW_CMD"
    elif [[ -f "/usr/local/bin/nextflow" ]]; then
        NEXTFLOW_CMD="/usr/local/bin/nextflow"
        log "Found Nextflow in /usr/local/bin: $NEXTFLOW_CMD"
    else
        log "Nextflow not found. Installing Nextflow 23.10.0 to output directory..."
        export NXF_VER=23.10.0
        # Install to OUTPUT_DIR instead of SCRIPT_DIR to avoid permission issues
        NEXTFLOW_INSTALL_DIR="$OUTPUT_DIR/01.assembly"
        mkdir -p "$NEXTFLOW_INSTALL_DIR"
        cd "$NEXTFLOW_INSTALL_DIR"
        curl -fsSL https://get.nextflow.io | bash
        if [[ -f "$NEXTFLOW_INSTALL_DIR/nextflow" ]]; then
            chmod +x "$NEXTFLOW_INSTALL_DIR/nextflow"
            NEXTFLOW_CMD="$NEXTFLOW_INSTALL_DIR/nextflow"
            log "Nextflow installed to: $NEXTFLOW_CMD"
        else
            log "ERROR: Failed to install Nextflow"
            exit 1
        fi
    fi
    
    # Verify Nextflow is executable
    if [[ -z "$NEXTFLOW_CMD" ]]; then
        log "ERROR: Nextflow command not found or could not be installed"
        exit 1
    fi
    
    if [[ ! -f "$NEXTFLOW_CMD" ]]; then
        log "ERROR: Nextflow executable not found: $NEXTFLOW_CMD"
        exit 1
    fi
    
    if [[ ! -x "$NEXTFLOW_CMD" ]]; then
        chmod +x "$NEXTFLOW_CMD" || {
            log "ERROR: Failed to make Nextflow executable: $NEXTFLOW_CMD"
            exit 1
        }
    fi
    
    # Verify Nextflow works
    if ! "$NEXTFLOW_CMD" -version &>/dev/null; then
        log "WARNING: Nextflow found but version check failed, continuing anyway..."
    else
        NEXTFLOW_VERSION=$("$NEXTFLOW_CMD" -version 2>/dev/null | head -1 || echo "unknown")
        log "Nextflow version: $NEXTFLOW_VERSION"
    fi
    
    # Run Nextflow workflow
    export NXF_VER=23.10.0
    cd "$OUTPUT_DIR/01.assembly"
    
    # Ensure .nextflow directory exists and has correct permissions
    # (Already created above, but ensure it's accessible)
    mkdir -p "$OUTPUT_DIR/01.assembly/.nextflow"
    chmod 755 "$OUTPUT_DIR/01.assembly/.nextflow"
    
    # Clean up Nextflow lock files from previous interrupted runs
    # Lock files can prevent new runs if previous execution was interrupted
    log "Checking for stale Nextflow lock files..."
    LOCK_DIR="$OUTPUT_DIR/01.assembly/.nextflow/cache"
    if [[ -d "$LOCK_DIR" ]]; then
        # Check if there are any lock files
        LOCK_FILES=$(find "$LOCK_DIR" -name "LOCK" -type f 2>/dev/null || true)
        if [[ -n "$LOCK_FILES" ]]; then
            # Check if there are any running Nextflow processes
            RUNNING_PROCESSES=$(pgrep -f "nextflow.*wf-clone-validation" || true)
            if [[ -z "$RUNNING_PROCESSES" ]]; then
                log "Found stale lock files but no running Nextflow processes. Cleaning up locks..."
                find "$LOCK_DIR" -name "LOCK" -type f -delete 2>/dev/null || true
                log "✓ Lock files cleaned"
            else
                log "WARNING: Found running Nextflow process(es): $RUNNING_PROCESSES"
                log "WARNING: Not cleaning lock files to avoid interfering with running process"
                log "WARNING: If this is an error, manually kill the process and delete lock files:"
                log "WARNING:   find $LOCK_DIR -name 'LOCK' -type f -delete"
                exit 1
            fi
        else
            log "✓ No lock files found"
        fi
    else
        log "✓ No cache directory found (first run)"
    fi
    
    # Set Nextflow temporary directory to avoid /tmp space issues
    # Use a temporary directory within the output directory
    NXF_TEMP_DIR="$OUTPUT_DIR/01.assembly/.nextflow/tmp"
    mkdir -p "$NXF_TEMP_DIR"
    chmod 755 "$NXF_TEMP_DIR"
    export NXF_TEMP="$NXF_TEMP_DIR"
    
    # Set matplotlib config directory for Docker containers
    # Matplotlib needs a writable cache directory inside containers
    MPLCONFIGDIR="$OUTPUT_DIR/01.assembly/.nextflow/matplotlib"
    mkdir -p "$MPLCONFIGDIR"
    chmod 755 "$MPLCONFIGDIR"
    export MPLCONFIGDIR="$MPLCONFIGDIR"
    
    log "Running Nextflow workflow..."
    log "Using Nextflow: $NEXTFLOW_CMD"
    log "Working directory: $(pwd)"
    log "Nextflow temp directory: $NXF_TEMP"
    log "Matplotlib config directory: $MPLCONFIGDIR"
    log "Command: NXF_VER=23.10.0 $NEXTFLOW_CMD run epi2me-labs/wf-clone-validation -r v1.8.3 ..."
    
    # Create Nextflow config override to set environment variables for Docker containers
    # This ensures matplotlib and other tools have writable directories
    # Use /tmp in containers (always writable) instead of workDir to avoid path issues
    NEXTFLOW_CONFIG_OVERRIDE="$OUTPUT_DIR/01.assembly/nextflow.config.override"
    cat > "$NEXTFLOW_CONFIG_OVERRIDE" <<'EOF'
process {
    withName: '.*' {
        beforeScript = '''
            export MPLCONFIGDIR=/tmp/matplotlib_config_$$
            mkdir -p $MPLCONFIGDIR
        '''
    }
}
EOF
    log "Created Nextflow config override: $NEXTFLOW_CONFIG_OVERRIDE"
    
    # Build Nextflow command
    # Note: --fastq should point to the directory containing barcode subdirectories
    # For demo data: wf-clone-validation-demo/fastq (contains barcode01/, barcode02/, etc.)
    # For standard data: fast_pass (contains sample subdirectories)
    # Output directory is always $OUTPUT_DIR/01.assembly
    NEXTFLOW_ARGS=(
        run
        epi2me-labs/wf-clone-validation
        -r v1.8.3
        --fastq "$FASTQ_DIR"
        --sample_sheet "$SAMPLESHEET"
        --out_dir "$OUTPUT_DIR/01.assembly"
        --approx_size "$APPROX_SIZE"
        --assm_coverage "$COVERAGE"
        --assembly_tool flye
        -profile standard
        -c "$NEXTFLOW_CONFIG_OVERRIDE"
        -resume
    )
    
    # Add primers if specified (optional)
    if [[ -n "$PRIMERS_FILE" ]] && [[ -f "$PRIMERS_FILE" ]]; then
        NEXTFLOW_ARGS+=(--primers "$PRIMERS_FILE")
        log "Using primers file: $PRIMERS_FILE"
    else
        log "No primers file provided (optional - workflow will skip primer detection)"
    fi
    
    # Execute Nextflow workflow and capture exit status
    # Use a temporary file to capture exit status since pipe prevents direct access
    TEMP_LOG=$(mktemp)
    set +e  # Don't exit on error immediately
    "$NEXTFLOW_CMD" "${NEXTFLOW_ARGS[@]}" 2>&1 | tee -a "$LOG_FILE" | tee "$TEMP_LOG"
    NEXFLOW_EXIT_CODE=${PIPESTATUS[0]}
    set -e  # Re-enable exit on error
    
    # Check if Nextflow succeeded
    if [[ $NEXFLOW_EXIT_CODE -ne 0 ]]; then
        log "ERROR: Nextflow workflow failed with exit code $NEXFLOW_EXIT_CODE"
        log "Check the log above for details"
        rm -f "$TEMP_LOG"
        exit 1
    fi
    
    # Verify that assembly output files exist
    if ! find "$OUTPUT_DIR/01.assembly" -name "*.final.fasta" -type f | head -1 | grep -q .; then
        log "ERROR: Nextflow completed but no FASTA files found in output"
        log "Please check Nextflow logs for errors"
        rm -f "$TEMP_LOG"
        exit 1
    fi
    
    rm -f "$TEMP_LOG"
    
    # Clean up Nextflow work directory to save space
    # The work directory contains intermediate files that are not needed after assembly
    if [[ -d "$OUTPUT_DIR/01.assembly/work" ]]; then
        log "Cleaning up Nextflow work directory..."
        rm -rf "$OUTPUT_DIR/01.assembly/work"
        log "✓ Work directory cleaned"
    fi
    
    log "✓ Assembly complete"
    log ""
else
    log "[Step 1] Skipping assembly step"
    log ""
fi

# Step 2-4: Fragment splitting, AB1 generation, Reports (in Docker)
log "=========================================="
log "[Steps 2-4] Fragment Splitting, AB1 Generation, Reports"
log "=========================================="
log "Running remaining steps in Docker container..."

# Build Python script arguments for steps 2-4
PYTHON_ARGS=(
    --input /data/input
    --output /data/output
    --project-id "${PROJECT_ID:-auto}"
    --fragment-size "$FRAGMENT_SIZE"
    --skip-assembly  # Skip assembly since we already did it
)

if [[ "$SKIP_FRAGMENTS" == "true" ]]; then
    PYTHON_ARGS+=(--skip-fragments)
fi

if [[ "$SKIP_AB1" == "true" ]]; then
    PYTHON_ARGS+=(--skip-ab1)
fi

if [[ "$SKIP_REPORTS" == "true" ]]; then
    PYTHON_ARGS+=(--skip-reports)
fi

if [[ "$VERBOSE" == "true" ]]; then
    PYTHON_ARGS+=(--verbose)
fi

docker run "${DOCKER_ARGS[@]}" "$DOCKER_IMAGE" \
    "${PYTHON_ARGS[@]}" || {
    log "ERROR: Pipeline steps failed"
    exit 1
}

log ""
log "=========================================="
log "Pipeline completed successfully!"
log "=========================================="
log "Results are available in: $OUTPUT_DIR"
log ""

