# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Docker-based pipeline for nanopore plasmid sequencing analysis that integrates epi2me wf-clone-validation workflow, fragment splitting, AB1 chromatogram generation, and PDF report generation. The pipeline processes nanopore sequencing data from `fast_pass/` folders.

## Common Commands

### Build Docker Image
```bash
docker build -t nanopore-plasmid-pipeline:latest .
```

### Run Full Pipeline (Recommended)
```bash
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50
```

### Run Pipeline with Docker Directly
```bash
docker run --rm \
  -v /path/to/fast_pass:/data/input/fast_pass:ro \
  -v /path/to/output:/data/output \
  -v /var/run/docker.sock:/var/run/docker.sock \
  nanopore-plasmid-pipeline:latest \
  --input /data/input \
  --output /data/output \
  --project-id PROJECT_ID
```

### Run Individual Steps
```bash
# Step 0: Initialization
python scripts/step0_initialize_analysis.py --input fast_pass/ --output output/

# Step 1: Assembly (runs on host, uses Nextflow)
python scripts/step1_run_epi2me_workflow.py --config config.yaml

# Step 2: Fragment splitting
python scripts/step2_split_fragments.py --input output/01.assembly/

# Step 3: AB1 generation
python scripts/step3_generate_ab1.py --input output/02.fragments/

# Step 4: Reports
python scripts/step4_generate_reports.py --fasta-dir output/01.assembly/
```

### Local Execution (without Docker)
```bash
conda env create -f environment.yml
conda activate plasmid_pipeline_env
python scripts/run_pipeline.py --input fast_pass/ --output output/ --project-id PROJECT_ID
```

## Architecture

### Pipeline Flow
The pipeline follows a modular step-based architecture:

1. **Step 0: Initialization** (`step0_initialize_analysis.py`) - Validates inputs, generates `config.yaml`
2. **Step 1: Assembly** (`step1_run_epi2me_workflow.py` / `step1_run_epi2me_workflow_host.py`) - Runs epi2me wf-clone-validation Nextflow workflow
3. **Step 2: Fragment Splitting** (`step2_split_fragments.py`) - Splits FASTA files into 2kb fragments using `split_plasmid_fasta.py`
4. **Step 3: AB1 Generation** (`step3_generate_ab1.py`) - Converts fragments to AB1 chromatograms using hyraxAbif
5. **Step 4: Reports** (`step4_generate_reports.py`) - Generates PDF reports using `generate_complete_reports.py`

### Hybrid Execution Model
The main entry point `run_pipeline.sh` orchestrates:
- Docker container for initialization and post-assembly steps
- Nextflow runs on the HOST machine (not inside Docker) because epi2me wf-clone-validation itself uses Docker containers for processes (medaka, flye, etc.)

### Output Directory Structure
```
output/
├── 01.assembly/     # epi2me wf-clone-validation results (*.final.fasta, *.final.fastq)
├── 02.fragments/    # Split FASTA fragments (2kb segments)
├── 03.ab1_files/    # AB1 chromatogram files
├── 04.reports/      # PDF reports and JSON summaries
├── 05.summary/      # Summary JSON and visualizations
└── logs/            # Pipeline log files
```

### Key External Tools
- **epi2me wf-clone-validation**: Nextflow workflow for assembly and annotation
- **hyraxAbif**: Haskell-based AB1 file generator (`hyraxAbif-exe gen`)

## Development Guidelines

### Code Organization
- Step scripts: `step{N}_{description}.py`
- Utility scripts: `split_plasmid_fasta.py`, `generate_complete_reports.py`, `generate_coverage_reports.py`
- All scripts use relative paths and follow the step-based architecture

### Script Standards
- Use `set -e` in bash scripts
- Check file existence before processing:
```bash
if [ -f "${output_file}" ] && [ -s "${output_file}" ]; then
    echo "  ✓ File already exists: $(basename "${output_file}")"
    continue
fi
```
- Never modify original input data
- All outputs go to `${OUTDIR}`

### Code Reuse Priority
Before creating new files:
1. Search existing scripts for similar functionality
2. Extend existing scripts rather than creating new ones
3. Document why new code is necessary if unavoidable

### Path Management for Docker
When running inside Docker:
- Input mounted at `/data/input`
- Output mounted at `/data/output`
- Scripts located at `/opt/pipeline/scripts/`

The pipeline handles HOST_INPUT_DIR and HOST_OUTPUT_DIR for proper Docker-in-Docker path mapping when Nextflow processes need to access files.

## Configuration

Pipeline parameters are stored in `config.yaml` (auto-generated):
- `approx_size`: Approximate plasmid size in bp (default: 5000)
- `coverage`: Target coverage (default: 50)
- `fragment_size`: Fragment size for splitting (default: 2000)
- `assembly_tool`: Assembly tool (default: flye)
