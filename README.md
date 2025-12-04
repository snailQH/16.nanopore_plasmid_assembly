# Nanopore Plasmid Assembly Pipeline

A comprehensive Docker-based pipeline for nanopore plasmid sequencing analysis, integrating epi2me wf-clone-validation workflow, fragment splitting, AB1 file generation, and comprehensive PDF report generation.

## Overview

This pipeline processes nanopore sequencing data from `fast_pass/` folders, performs assembly and annotation using epi2me's wf-clone-validation workflow, splits assemblies into fragments, generates AB1 chromatogram files, and produces comprehensive PDF reports with JSON summaries.

## Quick Start

### Step 1: Build Docker Image

```bash
# Build the Docker image (required first step)
docker build -t nanopore-plasmid-pipeline:latest .

# Expected build time: 10-30 minutes
# Image size: ~6.7 GB
```

### Step 2: Run Pipeline

```bash
# Run pipeline using the provided script
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50

#demo:
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

### Local Execution

```bash
# Install dependencies (see environment.yml)
conda env create -f environment.yml
conda activate plasmid_pipeline_env

# Run pipeline
python scripts/run_pipeline.py \
  --input fast_pass/ \
  --output output/ \
  --project-id PROJECT_ID
```

## Pipeline Workflow

1. **Step 0: Initialization** - Validate inputs and generate configuration
2. **Step 1: Assembly & Annotation** - Run epi2me wf-clone-validation workflow
3. **Step 2: Fragment Splitting** - Split assembled FASTA files into 2kb fragments
4. **Step 3: AB1 Generation** - Convert fragments to AB1 chromatogram files
5. **Step 4: Report Generation** - Generate comprehensive PDF reports and JSON summaries

## Input Data Structure

```
fast_pass/
├── sample1/
│   ├── *.fastq.gz
│   └── *.fastq.gz
├── sample2/
│   ├── *.fastq.gz
│   └── *.fastq.gz
└── ...
```

Each subfolder in `fast_pass/` represents a different plasmid sample.

## Output Structure

```
output/
├── 01.assembly/          # epi2me wf-clone-validation results
│   ├── sample1/
│   │   ├── *.final.fasta
│   │   ├── *.final.fastq
│   │   └── wf-clone-validation-report.html
│   └── sample2/
├── 02.fragments/         # Split FASTA fragments (2kb)
│   ├── sample1_2k_fragmented/
│   └── sample2_2k_fragmented/
├── 03.ab1_files/         # AB1 chromatogram files
│   ├── sample1_ab1/
│   └── sample2_ab1/
├── 04.reports/           # PDF reports and JSON summaries
│   ├── sample1/
│   │   ├── FASTA_FILES/
│   │   ├── RAW_FASTQ_FILES/
│   │   ├── PER_BASE_BREAKDOWN/
│   │   ├── QC_REPORTS/
│   │   └── sample1_report.pdf
│   └── sample2/
├── 05.summary/           # Summary JSON and visualizations
└── logs/                 # All log files
```

## Configuration

The pipeline automatically generates `config.yaml` during initialization. You can customize parameters:

```bash
python scripts/run_pipeline.py \
  --input fast_pass/ \
  --output output/ \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50 \
  --fragment-size 2000
```

## Documentation

### User Documentation
- **User Guide**: `docs/USER_GUIDE.md` - Complete usage instructions and examples
- **Output Format**: `docs/OUTPUT_FORMAT.md` - Detailed output file format documentation

### Technical Documentation
- **Pipeline Documentation**: `docs/PIPELINE.md`
- **Docker Setup**: `docs/DOCKER.md`
- **Project Structure**: `docs/PROJECT_STRUCTURE.md`
- **Change Logs**: `CHANGE_LOGS.md`

## Features

- ✅ **Docker-based**: Easy deployment and reproducibility
- ✅ **Modular design**: Each step can run independently
- ✅ **Comprehensive reports**: PDF reports with coverage plots and statistics
- ✅ **JSON output**: Structured JSON summaries for programmatic access
- ✅ **Error handling**: Robust error handling and logging
- ✅ **Skip options**: Skip individual steps with `--skip-*` flags

## Tools Used

- **epi2me wf-clone-validation**: Assembly and annotation workflow
- **hyraxAbif**: AB1 file generation from FASTA
- **split_plasmid_fasta.py**: Fragment splitting
- **generate_complete_reports.py**: Report generation

## Requirements

### Docker (Recommended)
- Docker 20.10+
- 4GB+ RAM
- 10GB+ disk space

### Local Execution
- Python 3.9+
- Nextflow
- Haskell Stack (for hyraxAbif)
- See `environment.yml` for full dependencies

## Citation

If you use this pipeline, please cite:
- epi2me wf-clone-validation: https://github.com/epi2me-labs/wf-clone-validation
- hyraxAbif: https://github.com/hyraxbio/hyraxAbif

## Support

For issues and questions, please visit: www.ampseq.com
