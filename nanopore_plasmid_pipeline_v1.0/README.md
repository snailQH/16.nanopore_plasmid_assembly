# Nanopore Plasmid Assembly Pipeline v1.0

A comprehensive Docker-based pipeline for nanopore plasmid sequencing analysis, integrating epi2me wf-clone-validation workflow, fragment splitting, AB1 file generation, and comprehensive PDF report generation.

## Overview

This pipeline processes nanopore sequencing data from `fast_pass/` folders, performs assembly and annotation using epi2me's wf-clone-validation workflow, splits assemblies into fragments, generates AB1 chromatogram files, and produces comprehensive PDF reports with JSON summaries.

## Quick Start

### Step 1: Get Docker Image

You have two options:

#### Option A: Build Locally (Recommended for Customization)

```bash
# Build the Docker image (required first step)
docker build -t nanopore-plasmid-pipeline:latest .

# Or load the image from image.tar
docker load -i nanopore-plasmid-pipeline.tar
# Expected build time: 10-30 minutes
# Image size: ~6.7 GB
```

#### Option B: Use Docker Hub Image (Faster Setup)

```bash
# Pull pre-built image from Docker Hub
docker pull snailqh/nanopore-plasmid-pipeline:ampseq

# Set environment variable to use Docker Hub image (optional, script will auto-detect)
export DOCKER_IMAGE="snailqh/nanopore-plasmid-pipeline:ampseq"
```

**Note**: The pipeline will automatically use Docker Hub image if local image is not found. See `docs/DOCKER_HUB_USAGE.md` for detailed instructions.

### Step 2: Run Pipeline

```bash
# Run pipeline using the provided script
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50

# Demo:
nohup ./run_pipeline.sh \
  --input /data1/opt/nanopore_plasmid_pipeline/wf-clone-validation-demo/fastq \
  --output /data1/opt/nanopore_plasmid_pipeline/final_test_output \
  --project-id final_test \
  --approx-size 3000 \
  --coverage 60 \
  --primers /data1/opt/nanopore_plasmid_pipeline/wf-clone-validation-demo/primers.tsv \
  --verbose > /data1/opt/nanopore_plasmid_pipeline/final_test_output/pipeline_console.log 2>&1 &

```

### Alternative: Using Docker Directly

```bash
# Run pipeline directly with Docker
docker run --rm \
  -v /path/to/fast_pass:/data/input/fast_pass:ro \
  -v /path/to/output:/data/output \
  nanopore-plasmid-pipeline:latest \
  python3 /opt/pipeline/scripts/run_pipeline.py \
  --input /data/input/fast_pass \
  --output /data/output \
  --project-id PROJECT_ID \
  --skip-assembly  # Note: Assembly runs on HOST via run_pipeline.sh
```

## Installation

See `INSTALLATION.md` for detailed installation instructions.

## Documentation

- **User Guide**: `docs/USER_GUIDE.md` - Complete usage instructions
- **Output Format**: `docs/OUTPUT_FORMAT.md` - Output file descriptions
- **Installation**: `INSTALLATION.md` - Step-by-step installation guide
- **Docker Hub Usage**: `docs/DOCKER_HUB_USAGE.md` - Using pre-built Docker Hub image
- **Package Contents**: `DELIVERY_PACKAGE.md` - File structure and contents

## Pipeline Steps

1. **Initialization**: Validate inputs, generate configuration
2. **Assembly**: Run epi2me wf-clone-validation workflow (on HOST)
3. **Fragment Splitting**: Split FASTA files into 2kb fragments
4. **AB1 Generation**: Convert fragments to AB1 chromatogram files
5. **Report Generation**: Generate comprehensive PDF and JSON reports

## Input Data Structure

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

## Output Structure

```
output/
├── 01.assembly/          # Assembly results
├── 02.fragments/         # Split FASTA fragments
├── 03.ab1_files/         # AB1 chromatogram files
├── 04.reports/           # PDF and JSON reports
├── config.yaml           # Pipeline configuration
└── logs/                 # Execution logs
```

## Key Features

- **Docker-based**: Easy deployment and reproducibility
- **Hybrid Architecture**: Nextflow runs on HOST, other steps in Docker
- **Comprehensive Reports**: PDF reports with coverage plots and statistics
- **AB1 Generation**: Converts FASTA fragments to Sanger sequencing format
- **Automatic Nextflow**: Auto-downloads Nextflow if not found

## System Requirements

- **Docker**: 20.10+
- **OS**: Linux (Ubuntu 20.04+) or macOS
- **RAM**: 4GB minimum, 8GB+ recommended
- **Disk**: 10GB+ free space
- **Internet**: Required for building Docker image

## Version Information

- **Version**: 1.0
- **Release Date**: 2025-12-03
- **Docker Image**: `nanopore-plasmid-pipeline:latest` (local build)
- **Nextflow Version**: 23.10.0 (auto-downloaded)
- **epi2me Workflow**: v1.8.3

## Support

For detailed usage instructions, troubleshooting, and examples, see:
- `docs/USER_GUIDE.md` - Complete user manual
- `docs/OUTPUT_FORMAT.md` - Output file format documentation
- `INSTALLATION.md` - Installation guide

---

**Last Updated:** 2025-12-03  
**Pipeline Version:** 1.0

