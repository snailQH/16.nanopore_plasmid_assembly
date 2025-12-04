# Nanopore Plasmid Assembly Pipeline - User Guide

**Version:** 1.0  
**Last Updated:** 2025-12-03  
**Author:** AmpSeq

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Detailed Usage](#detailed-usage)
6. [Input Data Requirements](#input-data-requirements)
7. [Pipeline Steps](#pipeline-steps)
8. [Output Structure](#output-structure)
9. [Configuration Options](#configuration-options)
10. [Troubleshooting](#troubleshooting)
11. [Examples](#examples)

---

## Overview

The Nanopore Plasmid Assembly Pipeline is a comprehensive Docker-based workflow for analyzing nanopore sequencing data from plasmid samples. It integrates:

- **Assembly & Annotation**: epi2me wf-clone-validation workflow
- **Fragment Splitting**: Splits assemblies into 2kb fragments
- **AB1 Generation**: Converts fragments to AB1 chromatogram files
- **Report Generation**: Comprehensive PDF reports with coverage plots and statistics

### Key Features

- ✅ **Docker-based**: Easy deployment and reproducibility
- ✅ **Automatic Nextflow installation**: Downloads Nextflow if not found
- ✅ **Comprehensive reports**: PDF reports with coverage plots, read length distributions, and statistics
- ✅ **JSON output**: Structured JSON summaries for programmatic access
- ✅ **Modular design**: Each step can run independently or be skipped
- ✅ **Error handling**: Robust error handling and logging
- ✅ **Resume capability**: Can resume from any step if interrupted

---

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended) or macOS
- **Docker**: Docker 20.10+ (required)
- **Disk Space**: 
  - Minimum: 10GB free space
  - Recommended: 20GB+ for multiple samples
  - Docker image: ~6.7 GB
- **Memory**: 
  - Minimum: 4GB RAM
  - Recommended: 8GB+ RAM
- **CPU**: Multi-core recommended for faster processing

### Software Requirements

- **Docker**: Must be installed and running
- **Nextflow**: Optional (will be auto-downloaded if not found)
- **Internet Connection**: Required for:
  - Building Docker image (downloading dependencies)
  - Downloading Nextflow (if not installed)
  - Downloading epi2me workflow

---

## Installation

### Option 1: Use Pre-built Docker Image (Recommended)

The easiest way to use the pipeline is to pull the pre-built Docker image from Docker Hub:

```bash
# Pull the Docker image
docker pull snailqh/nanopore-plasmid-pipeline:ampseq

# Verify installation
docker run --rm snailqh/nanopore-plasmid-pipeline:ampseq python3 --version
# Should output: Python 3.x.x

# Test pipeline script
docker run --rm snailqh/nanopore-plasmid-pipeline:ampseq python3 /opt/pipeline/scripts/step0_initialize_analysis.py --help
```

**Docker Hub Image:** `snailqh/nanopore-plasmid-pipeline:ampseq`  
**Image Size:** ~6.7 GB  
**Pull time:** 5-15 minutes (depending on internet speed)

**What's included in the Docker image:**
- All pipeline scripts (`/opt/pipeline/scripts/`)
- Python 3.9+ with required packages
- hyraxAbif (for AB1 generation)
- **Note:** Nextflow is NOT included - it runs on HOST machine and is auto-downloaded if needed

### Option 2: Build Docker Image Locally

If you prefer to build the image yourself:

```bash
# Step 1: Clone or Download the Pipeline
git clone <repository-url>
cd nanopore_plasmid_assembly

# Or download and extract the pipeline directory

# Step 2: Build Docker Image
docker build -t nanopore-plasmid-pipeline:latest .
```

**Expected build time:** 10-30 minutes (depending on internet speed)

**What gets installed:**
- Ubuntu base image
- Python 3.9+ with required packages (reportlab, matplotlib, numpy, biopython)
- Haskell Stack and hyraxAbif (for AB1 generation)
- All pipeline scripts


---

## Quick Start

### Architecture Overview

The pipeline uses a **hybrid architecture**:

1. **`run_pipeline.sh`** (Recommended): Runs on HOST machine
   - Step 0: Initialization (in Docker container)
   - Step 1: Assembly with Nextflow (on HOST - requires Docker socket access)
   - Steps 2-4: Fragment splitting, AB1 generation, Reports (in Docker container)

2. **`run_pipeline.py`**: Runs inside Docker container
   - Step 0: Initialization (optional)
   - Step 1: **SKIPPED** (Nextflow must run on HOST)
   - Steps 2-4: Fragment splitting, AB1 generation, Reports
   - **Use case**: When assembly is already complete, only need Steps 2-4

### Basic Usage (Recommended: run_pipeline.sh)

**Using Pre-built Docker Image:**

```bash
# First, ensure you have the pipeline scripts (clone repository or download)
# Then run the pipeline script, which will use the Docker Hub image
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50
```

**Note:** The `run_pipeline.sh` script will automatically use the Docker Hub image (`snailqh/nanopore-plasmid-pipeline:ampseq`) if available, or fall back to local image (`nanopore-plasmid-pipeline:latest`).

**How it works:**
- Script runs on HOST machine
- Step 0 (initialization) runs in Docker container
- Step 1 (Nextflow/epi2me) runs on HOST (can access Docker socket for process containers)
- Steps 2-4 run in Docker container
- Nextflow is auto-downloaded to output directory if not found

### Alternative Usage (Docker-only: run_pipeline.py)

**When to use:** If assembly is already complete and you only need Steps 2-4.

```bash
docker run --rm \
  -v /path/to/fast_pass:/data/input:ro \
  -v /path/to/output:/data/output \
  snailqh/nanopore-plasmid-pipeline:ampseq \
  python3 /opt/pipeline/scripts/run_pipeline.py \
  --input /data/input \
  --output /data/output \
  --project-id PROJECT_ID \
  --skip-assembly  # Assembly must be skipped (runs on HOST only)
```

**Important Notes:**
- Assembly step (`--skip-assembly`) must be skipped when using `run_pipeline.py`
- Assembly results must already exist in `output/01.assembly/`
- This mode is useful for re-running Steps 2-4 without re-assembling

### With Log Redirection

```bash
./run_pipeline.sh \
  --input /path/to/fast_pass \
  --output /path/to/output \
  --project-id PROJECT_ID \
  --approx-size 5000 \
  --coverage 50 \
  --verbose > output/pipeline_console.log 2>&1
```

**Note:** The output directory will be automatically created if it doesn't exist.

---

## Detailed Usage

### Command-Line Arguments

#### Required Arguments

| Argument | Short | Description | Example |
|----------|-------|-------------|---------|
| `--input` | `-i` | Input directory containing `fast_pass/` or `fastq/` folder | `/data/fast_pass` |
| `--output` | `-o` | Output directory for results | `/data/output` |

#### Optional Arguments

| Argument | Description | Default | Example |
|----------|-------------|---------|---------|
| `--project-id` | Project identifier (used in filenames) | Auto-generated from date | `PROJECT_001` |
| `--approx-size` | Approximate plasmid size in base pairs | `5000` | `10000` |
| `--coverage` | Target coverage for assembly | `50` | `60` |
| `--fragment-size` | Fragment size for splitting (bp) | `2000` | `3000` |
| `--primers` | Path to primers TSV file (optional) | None | `/path/to/primers.tsv` |
| `--verbose` | `-v` | Enable verbose logging | `false` | N/A |
| `--skip-assembly` | Skip assembly step | `false` | N/A |
| `--skip-fragments` | Skip fragment splitting | `false` | N/A |
| `--skip-ab1` | Skip AB1 generation | `false` | N/A |
| `--skip-reports` | Skip report generation | `false` | N/A |
| `--help` | `-h` | Show help message | N/A | N/A |

### Argument Details

#### `--input` / `-i`

The input directory should contain either:
- A `fast_pass/` subdirectory with sample folders
- A `fastq/` subdirectory with sample folders
- Direct FASTQ files organized by sample

**Example structure:**
```
/path/to/input/
├── fast_pass/
│   ├── sample1/
│   │   ├── sample1_read1.fastq.gz
│   │   └── sample1_read2.fastq.gz
│   └── sample2/
│       ├── sample2_read1.fastq.gz
│       └── sample2_read2.fastq.gz
```

#### `--output` / `-o`

Output directory where all results will be stored. The directory will be created automatically if it doesn't exist.

**Note:** Ensure you have write permissions to this directory.

#### `--project-id`

Project identifier used in output filenames (e.g., `PROJECT_ID_summary.csv`). If not provided, will be auto-generated as `YYYYMMDD`.

#### `--approx-size`

Approximate size of the plasmid in base pairs. This helps the assembly algorithm:
- **Small plasmids** (< 5kb): Use `3000-5000`
- **Medium plasmids** (5-10kb): Use `5000-10000`
- **Large plasmids** (> 10kb): Use `10000+`

**Note:** This can also be specified per-sample in a samplesheet (see Advanced Usage).

#### `--coverage`

Target coverage for assembly. Higher coverage = better quality but slower:
- **Minimum**: `20x` (may have gaps)
- **Recommended**: `50-60x` (good balance)
- **High quality**: `100x+` (slower, very high quality)

#### `--fragment-size`

Size of fragments for splitting (in base pairs). Default is `2000` bp. Each fragment will be converted to an AB1 file.

#### `--primers`

Path to a TSV file containing primer sequences for insert detection. Format:
```tsv
primer_name	sequence
pRham	GACCACAACGGTTTCCCTCTAG	TGGGTAACTTTGTATGTGTCCGCAGC							
T7	TAATACGACTCACTATAGGG	GCTAGTTATTGCTCAGCGG
```

#### Skip Options

Use skip options to run only specific steps:
- `--skip-assembly`: Skip assembly (use existing assembly results)
- `--skip-fragments`: Skip fragment splitting
- `--skip-ab1`: Skip AB1 generation
- `--skip-reports`: Skip report generation

---

## Input Data Requirements

### Directory Structure

The pipeline expects one of the following structures:

#### Option 1: Standard Structure (Recommended)

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

#### Option 2: Alternative Structure

```
fastq/
├── sample1/
│   ├── *.fastq.gz
│   └── *.fastq.gz
└── ...
```


### File Requirements

- **Format**: FASTQ files (`.fastq` or `.fastq.gz`)
- **Naming**: Sample names will be extracted from directory names or filenames
- **Quality**: High-quality reads recommended (Q20+)
- **Length**: Long reads (> 1000 bp) work best

### Sample Naming

- **Directory-based**: Sample name = directory name
- **File-based**: Sample name extracted from filename (e.g., `sample1_read1.fastq.gz` → `sample1`)
- **Barcode mapping**: If directory names don't match barcode format (`barcode01`, `barcode02`, etc.), symbolic links will be created automatically

---

## Pipeline Steps

The pipeline consists of 5 main steps. **Important:** Steps 0 and 1 run differently depending on execution mode:

### Execution Modes

**Mode 1: Using `run_pipeline.sh` (Recommended)**
- Step 0: Runs in Docker container
- Step 1: Runs on HOST machine (Nextflow needs Docker socket access)
- Steps 2-4: Run in Docker container

**Mode 2: Using `run_pipeline.py` (Docker-only)**
- Step 0: Runs in Docker container (optional)
- Step 1: **SKIPPED** (must run on HOST)
- Steps 2-4: Run in Docker container
- **Requires:** Assembly results already exist in `output/01.assembly/`

### Step 0: Initialization

**Purpose**: Validate inputs, check dependencies, generate configuration

**What it does:**
- Validates input directory structure
- Checks for required software (Nextflow, Python, etc.)
- Creates output directory structure
- Generates `config.yaml` file
- Creates samplesheet for epi2me workflow

**Execution:**
- **Mode 1** (`run_pipeline.sh`): Runs in Docker container
- **Mode 2** (`run_pipeline.py`): Runs in Docker container (if not skipped)

**Output:**
- `config.yaml`: Pipeline configuration
- `logs/step0_initialize.log`: Initialization log
- `01.assembly/samplesheet.csv`: Samplesheet for epi2me workflow

**Time:** < 1 minute

### Step 1: Assembly & Annotation

**Purpose**: Assemble plasmid sequences and annotate features

**What it does:**
- Runs epi2me wf-clone-validation workflow
- Assembles reads into contigs
- Polishes assemblies with Medaka
- Annotates features (genes, CDS, etc.)
- Generates GenBank files

**Tools used:**
- Nextflow (workflow manager) - **runs on HOST machine**
- epi2me wf-clone-validation (v1.8.3)
- Flye (assembly)
- Medaka (polishing)

**Execution:**
- **Mode 1** (`run_pipeline.sh`): Runs on HOST machine
  - Nextflow is executed on HOST (can access Docker socket)
  - Nextflow auto-downloaded to `output/01.assembly/` if not found
  - Nextflow uses Docker containers for processes (medaka, flye, etc.)
- **Mode 2** (`run_pipeline.py`): **SKIPPED** (must use Mode 1 for assembly)

**Why Nextflow runs on HOST:**
- Nextflow needs to spawn Docker containers for workflow processes
- Requires access to Docker socket (`/var/run/docker.sock`)
- Running Nextflow inside Docker requires Docker-in-Docker, which is complex

**Output:**
- `*.final.fasta`: Assembled sequences
- `*.final.fastq`: Processed reads
- `*.annotations.gbk`: GenBank annotation files
- `*.annotations.bed`: BED annotation files
- `*.assembly_stats.tsv`: Assembly statistics
- `wf-clone-validation-report.html`: Workflow report
- `.nextflow/nextflow`: Nextflow executable (if auto-downloaded)

**Time:** 5-30 minutes per sample (depends on read count and coverage)

### Step 2: Fragment Splitting

**Purpose**: Split assembled FASTA files into fragments

**What it does:**
- Reads assembled FASTA files
- Splits sequences into fragments of specified size (default: 2000 bp)
- Creates individual FASTA files for each fragment
- Formats headers for hyraxAbif compatibility

**Output:**
- `sampleXX_2k_fragmented/`: Directory per sample
  - `sampleXX_part1.fasta`: First fragment
  - `sampleXX_part2.fasta`: Second fragment
  - ... (more fragments if sequence is longer)

**Time:** < 1 minute

### Step 3: AB1 Generation

**Purpose**: Convert FASTA fragments to AB1 chromatogram files

**What it does:**
- Uses hyraxAbif to convert FASTA to AB1 format
- Generates one AB1 file per fragment
- AB1 files are compatible with Sanger sequencing analysis tools

**Output:**
- `sampleXX_ab1/`: Directory per sample
  - `sampleXX_part1.ab1`: AB1 file for first fragment
  - `sampleXX_part2.ab1`: AB1 file for second fragment
  - ...

**Time:** < 1 minute per sample

### Step 4: Report Generation

**Purpose**: Generate comprehensive PDF reports and JSON summaries

**What it does:**
- Calculates coverage statistics
- Generates coverage plots
- Creates read length distribution plots
- Generates per-base breakdown
- Creates PDF reports per sample
- Generates summary CSV file

**Output:**
- `sampleXX/`: Directory per sample
  - `FASTA_FILES/`: Individual contig FASTA files
  - `RAW_FASTQ_FILES/`: Processed FASTQ files
  - `PER_BASE_BREAKDOWN/`: Coverage and per-base statistics
  - `QC_REPORTS/`: PDF reports
  - `CHROMATOGRAM_FILES_ab1/`: AB1 files
- `PROJECT_ID_summary.csv`: Summary of all samples

**Time:** 1-5 minutes per sample

---

## Output Structure

### Complete Output Directory Structure

```
output/
├── 01.assembly/                    # Assembly results
│   ├── sample02.final.fasta        # Assembled sequences
│   ├── sample02.final.fastq        # Processed reads
│   ├── sample02.insert.fasta       # Insert sequences (if primers provided)
│   ├── sample02.annotations.gbk    # GenBank annotations
│   ├── sample02.annotations.bed    # BED annotations
│   ├── sample02.assembly_stats.tsv # Assembly statistics
│   ├── samplesheet.csv             # Input samplesheet
│   ├── wf-clone-validation-report.html # Workflow report
│   └── .nextflow/                  # Nextflow cache (if Nextflow auto-installed)
│       └── nextflow                # Nextflow executable (if auto-installed)
│
├── 02.fragments/                   # Fragment splitting results
│   ├── sample02_2k_fragmented/
│   │   ├── sample02_part1.fasta
│   │   └── sample02_part2.fasta
│   └── logs/
│       └── step2_split_fragments.log
│
├── 03.ab1_files/                   # AB1 chromatogram files
│   ├── sample02_ab1/
│   │   ├── sample02_part1.ab1
│   │   └── sample02_part2.ab1
│   └── logs/
│       └── step3_generate_ab1.log
│
├── 04.reports/                      # Final reports
│   ├── PROJECT_ID_summary.csv      # Summary CSV
│   ├── sample02/
│   │   ├── FASTA_FILES/
│   │   │   └── sample02_sample02.fa
│   │   ├── RAW_FASTQ_FILES/
│   │   │   └── sample02_reads.fastq.gz
│   │   ├── PER_BASE_BREAKDOWN/
│   │   │   ├── sample02_sample02_coverage.png
│   │   │   ├── sample02_sample02_per_base_details.csv
│   │   │   └── sample02_sample02_low_confidence_bases.csv
│   │   ├── QC_REPORTS/
│   │   │   └── sample02_report.pdf
│   │   └── CHROMATOGRAM_FILES_ab1/
│   │       ├── sample02_part1.ab1
│   │       └── sample02_part2.ab1
│   └── logs/
│       └── step4_generate_reports.log
│
├── 05.summary/                      # Summary files (if generated)
├── config.yaml                      # Pipeline configuration
└── logs/                            # Pipeline logs
    ├── pipeline.log                 # Main pipeline log
    └── step0_initialize.log         # Initialization log
```

---

## Configuration Options

### Configuration File (`config.yaml`)

The pipeline automatically generates a `config.yaml` file in the output directory. This file contains all parameters used during execution:

```yaml
project:
  project_id: "PROJECT_ID"
  input_dir: "/path/to/input"
  output_dir: "/path/to/output"
  created_at: "2025-12-03T18:45:10"

assembly:
  tool: "epi2me_wf_clone_validation"
  workflow_version: "v1.8.3"
  approx_size: 10000
  coverage: 60
  assembly_tool: "flye"

fragmentation:
  fragment_size: 2000
  tool: "split_plasmid_fasta.py"

ab1_generation:
  tool: "hyraxAbif"
  executable: "/opt/hyraxAbif/hyraxAbif-exe"

reporting:
  tool: "generate_complete_reports.py"
  format: "pdf"
  include_coverage: true
  include_length_dist: true
  generate_json: true
  generate_html: false
```

**Note:** The configuration file is for reference only. To change parameters, re-run the pipeline with different command-line arguments.

---

## Troubleshooting

### Common Issues

#### 1. "Nextflow executable not found"

**Problem:** Nextflow is not installed and auto-download failed.

**Solution:**
- Check internet connection
- Check write permissions to output directory
- Manually install Nextflow:
  ```bash
  curl -fsSL https://get.nextflow.io | bash
  sudo mv nextflow /usr/local/bin/
  ```

#### 2. "Docker: permission denied"

**Problem:** Docker requires sudo or user is not in docker group.

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

#### 3. "Output directory creation failed"

**Problem:** No write permissions to output directory.

**Solution:**
```bash
# Check permissions
ls -ld /path/to/output
# Fix permissions
chmod 755 /path/to/output
# Or create directory first
mkdir -p /path/to/output
chmod 755 /path/to/output
```

#### 4. "No FASTA files found after assembly"

**Problem:** Assembly step failed or produced no results.

**Solution:**
- Check `logs/pipeline.log` for errors
- Check `01.assembly/.nextflow.log` for Nextflow errors
- Verify input FASTQ files are valid
- Check if samples have sufficient reads (minimum ~100 reads recommended)

#### 5. "AB1 generation failed"

**Problem:** hyraxAbif failed to generate AB1 files.

**Solution:**
- Check fragment FASTA files exist in `02.fragments/`
- Verify FASTA format (headers should be `> 1.0`, `> 2.0`, etc.)
- Check `03.ab1_files/logs/step3_generate_ab1.log` for errors

#### 6. "Report generation failed"

**Problem:** Report generation script failed.

**Solution:**
- Check `04.reports/logs/step4_generate_reports.log`
- Verify FASTA and FASTQ files exist in `01.assembly/`
- Check if matplotlib/reportlab dependencies are installed in Docker image

### Log Files

All logs are stored in the output directory:

- **Main log**: `logs/pipeline.log` - Complete pipeline execution log
- **Step logs**: `XX.step/logs/stepX_*.log` - Individual step logs
- **Nextflow log**: `01.assembly/.nextflow.log` - Nextflow execution log

### Getting Help

1. Check log files for detailed error messages
2. Run with `--verbose` flag for more detailed output
3. Check `CHANGE_LOGS.md` for known issues and fixes
4. Contact support: www.ampseq.com

---

## Examples

### Example 1: Basic Usage

```bash
./run_pipeline.sh \
  --input /data/fast_pass \
  --output /data/results \
  --project-id PROJECT_001 \
  --approx-size 5000 \
  --coverage 50
```

### Example 2: High Coverage Analysis

```bash
./run_pipeline.sh \
  --input /data/fast_pass \
  --output /data/results \
  --project-id PROJECT_002 \
  --approx-size 10000 \
  --coverage 100 \
  --verbose
```

### Example 3: With Primers File

```bash
./run_pipeline.sh \
  --input /data/fast_pass \
  --output /data/results \
  --project-id PROJECT_003 \
  --approx-size 5000 \
  --coverage 50 \
  --primers /data/primers.tsv
```

### Example 4: Skip Assembly (Use Existing Results)

```bash
./run_pipeline.sh \
  --input /data/fast_pass \
  --output /data/results \
  --project-id PROJECT_004 \
  --skip-assembly \
  --verbose
```

### Example 5: Only Generate Reports

```bash
./run_pipeline.sh \
  --input /data/fast_pass \
  --output /data/results \
  --project-id PROJECT_005 \
  --skip-assembly \
  --skip-fragments \
  --skip-ab1 \
  --verbose
```

### Example 6: Custom Fragment Size

```bash
./run_pipeline.sh \
  --input /data/fast_pass \
  --output /data/results \
  --project-id PROJECT_006 \
  --approx-size 5000 \
  --coverage 50 \
  --fragment-size 3000
```

### Example 7: Background Execution with Logging

```bash
nohup ./run_pipeline.sh \
  --input /data/fast_pass \
  --output /data/results \
  --project-id PROJECT_007 \
  --approx-size 5000 \
  --coverage 50 \
  --verbose > /data/results/pipeline_console.log 2>&1 &

# Monitor progress
tail -f /data/results/pipeline_console.log
```

---

## Docker Image Information

### Local Docker Image

- **Image Name**: `nanopore-plasmid-pipeline:latest`
- **Size**: ~6.7 GB
- **Base Image**: Ubuntu (latest)
- **Includes**: 
  - All pipeline scripts (`/opt/pipeline/scripts/`)
  - Python 3.9+ with required packages
  - hyraxAbif (for AB1 generation)
  - **Note:** Nextflow is NOT included (runs on HOST)

### Building the Image

```bash
# Build the image
docker build -t nanopore-plasmid-pipeline:latest .

# Verify image
docker images | grep nanopore-plasmid-pipeline
```

### Using the Image

The `run_pipeline.sh` script uses the local Docker image. You can also use it directly:

```bash
docker run --rm \
  -v /path/to/input:/data/input:ro \
  -v /path/to/output:/data/output \
  nanopore-plasmid-pipeline:latest \
  python3 /opt/pipeline/scripts/run_pipeline.py \
  --input /data/input \
  --output /data/output \
  --project-id PROJECT_ID \
  --skip-assembly  # Must skip - assembly runs on HOST only
```

---

## Best Practices

1. **Always use absolute paths** for input and output directories
2. **Check disk space** before running (especially for large datasets)
3. **Use `--verbose`** flag for debugging
4. **Monitor logs** during execution
5. **Keep output directory** for troubleshooting if errors occur
6. **Use `--skip-*` options** to resume from specific steps
7. **Backup important data** before running pipeline

---

## Performance Tips

1. **Disk I/O**: Use fast storage (SSD) for better performance
2. **Memory**: More RAM = faster processing (especially for assembly)
3. **CPU**: Multi-core systems process samples faster
4. **Network**: Fast internet helps with Nextflow workflow downloads
5. **Docker**: Use Docker with sufficient resources allocated

---

## Support and Contact

- **Website**: www.ampseq.com
- **Documentation**: See `docs/` directory
- **Change Logs**: See `CHANGE_LOGS.md`
- **Issues**: Check log files first, then contact support

---

**Last Updated:** 2025-12-03  
**Pipeline Version:** 1.0  
**Docker Image**: `nanopore-plasmid-pipeline:latest` (local build)

