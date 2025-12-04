# Quick Start Guide

## Installation (5 minutes)

### Step 1: Get Docker Image

**Option A: Build Locally**
```bash
cd nanopore_plasmid_pipeline_v1.0
docker build -t nanopore-plasmid-pipeline:latest .
```
**Expected time:** 10-30 minutes  
**Image size:** ~6.7 GB

**Option B: Use Docker Hub (Faster)**
```bash
docker pull snailqh/nanopore-plasmid-pipeline:ampseq
# Optional: export DOCKER_IMAGE="snailqh/nanopore-plasmid-pipeline:ampseq"
# Script will auto-detect Docker Hub image if local image not found
```

### Step 2: Verify Installation

```bash
# For local build
docker run --rm nanopore-plasmid-pipeline:latest python3 --version

# For Docker Hub image
docker run --rm snailqh/nanopore-plasmid-pipeline:ampseq python3 --version
```

## Running the Pipeline (2 minutes)

### Basic Usage

```bash
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

### Output Structure

```
output/
├── 01.assembly/          # Assembly results
├── 02.fragments/         # Split FASTA fragments
├── 03.ab1_files/         # AB1 chromatogram files
├── 04.reports/           # PDF and JSON reports
├── config.yaml           # Pipeline configuration
└── logs/                 # Execution logs
```

## Common Commands

### Run with verbose logging

```bash
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --verbose
```

### Skip specific steps

```bash
# Skip assembly (use existing results)
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --skip-assembly

# Only generate reports
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --skip-assembly \
  --skip-fragments \
  --skip-ab1
```

## Next Steps

- **Detailed Installation**: See `INSTALLATION.md`
- **Complete User Guide**: See `docs/USER_GUIDE.md`
- **Output Format**: See `docs/OUTPUT_FORMAT.md`
- **Troubleshooting**: See `docs/USER_GUIDE.md` troubleshooting section

---

**Version**: 1.0  
**Last Updated**: 2025-12-03
