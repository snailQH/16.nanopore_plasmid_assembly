# Nanopore Plasmid Assembly Pipeline - Delivery Package

## Package Contents

This delivery package contains all necessary files to run the Nanopore Plasmid Assembly Pipeline.

### Required Files

#### 1. Main Scripts
- **`run_pipeline.sh`** - Main entry script (runs on HOST machine)
  - Orchestrates all pipeline steps
  - Handles Docker container execution
  - Manages Nextflow execution on HOST

#### 2. Docker Files
- **`Dockerfile`** - Docker image definition
  - Contains all dependencies and pipeline scripts
  - Builds complete execution environment

#### 3. Pipeline Scripts (`scripts/` directory)
- **`step0_initialize_analysis.py`** - Initialization and configuration
- **`step1_run_epi2me_workflow.py`** - Assembly workflow wrapper (not used directly)
- **`step2_split_fragments.py`** - FASTA fragmentation
- **`step3_generate_ab1.py`** - AB1 file generation
- **`step4_generate_reports.py`** - Report generation
- **`run_pipeline.py`** - Docker container entry point
- **`generate_samplesheet.py`** - Samplesheet generation
- **`split_plasmid_fasta.py`** - FASTA splitting utility
- **`generate_complete_reports.py`** - Comprehensive report generator

#### 4. Documentation (`docs/` directory)
- **`USER_GUIDE.md`** - Complete user manual
- **`OUTPUT_FORMAT.md`** - Output file format documentation
- **`README.md`** - Project overview and quick start

#### 5. Configuration Files
- **`CHANGE_LOGS.md`** - Change history and version tracking

### Optional Files

- **`sync_to_remote.sh`** - Remote server sync script (for development)
- **`archive/`** - Historical files and backups
- **`.cursor/`** - Development rules (not needed for execution)

## File Structure

```
nanopore_plasmid_assembly/
├── README.md                          # Project overview
├── CHANGE_LOGS.md                     # Version history
├── DELIVERY_PACKAGE.md                # This file
├── Dockerfile                         # Docker image definition
├── run_pipeline.sh                    # Main entry script (HOST)
│
├── scripts/                           # Pipeline scripts
│   ├── step0_initialize_analysis.py
│   ├── step1_run_epi2me_workflow.py
│   ├── step2_split_fragments.py
│   ├── step3_generate_ab1.py
│   ├── step4_generate_reports.py
│   ├── run_pipeline.py                # Docker entry point
│   ├── generate_samplesheet.py
│   ├── split_plasmid_fasta.py
│   └── generate_complete_reports.py
│
└── docs/                              # Documentation
    ├── USER_GUIDE.md                  # Complete user manual
    └── OUTPUT_FORMAT.md               # Output format documentation
```

## Installation Instructions

### Step 1: Prerequisites

- **Docker**: Version 20.10+ installed and running
- **Operating System**: Linux (Ubuntu 20.04+ recommended) or macOS
- **Disk Space**: 
  - Minimum: 10GB free space
  - Recommended: 20GB+ for multiple samples
- **Memory**: 
  - Minimum: 4GB RAM
  - Recommended: 8GB+ RAM
- **Internet Connection**: Required for building Docker image and downloading Nextflow

### Step 2: Build Docker Image

```bash
# Navigate to pipeline directory
cd nanopore_plasmid_assembly

# Build Docker image
docker build -t nanopore-plasmid-pipeline:latest .

# Expected build time: 10-30 minutes
# Final image size: ~6.7 GB
```

### Step 3: Verify Installation

```bash
# Test Docker image
docker run --rm nanopore-plasmid-pipeline:latest python3 --version

# Test pipeline script
docker run --rm nanopore-plasmid-pipeline:latest python3 /opt/pipeline/scripts/step0_initialize_analysis.py --help
```

## Quick Start

### Basic Usage

```bash
# Run pipeline
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50
```

### Input Data Structure

```
fast_pass/
├── sample1/
│   ├── sample1_read1.fastq.gz
│   └── sample1_read2.fastq.gz
├── sample2/
│   ├── sample2_read1.fastq.gz
│   └── sample2_read2.fastq.gz
└── ...
```

## Documentation

- **User Guide**: See `docs/USER_GUIDE.md` for complete usage instructions
- **Output Format**: See `docs/OUTPUT_FORMAT.md` for output file descriptions
- **Quick Start**: See `README.md` for overview

## Architecture

The pipeline uses a **hybrid architecture**:

1. **`run_pipeline.sh`** runs on HOST machine
   - Step 0: Initialization (in Docker container)
   - Step 1: Assembly with Nextflow (on HOST - requires Docker socket access)
   - Steps 2-4: Fragment splitting, AB1 generation, Reports (in Docker container)

2. **`run_pipeline.py`** runs inside Docker container
   - Use only for Steps 2-4 when assembly is already complete
   - Assembly step must be skipped (`--skip-assembly`)

## Key Points

- **Nextflow runs on HOST**: Required for Docker socket access
- **Docker image contains**: All Python scripts and dependencies
- **Nextflow auto-download**: Installed to output directory if not found
- **Output structure**: Organized by step (01.assembly, 02.fragments, etc.)

## Support

For detailed usage instructions, troubleshooting, and examples, see:
- `docs/USER_GUIDE.md` - Complete user manual
- `docs/OUTPUT_FORMAT.md` - Output file format documentation

## Version Information

- **Pipeline Version**: 1.0
- **Last Updated**: 2025-12-03
- **Docker Image**: `nanopore-plasmid-pipeline:latest`
- **Nextflow Version**: 23.10.0 (auto-downloaded)
- **epi2me Workflow**: v1.8.3

---

**Note**: This package is designed for local execution. All dependencies are included in the Docker image except Nextflow, which runs on the HOST machine and is auto-downloaded if needed.

