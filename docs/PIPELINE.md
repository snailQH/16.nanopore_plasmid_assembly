# Nanopore Plasmid Assembly Pipeline Documentation

## Pipeline Overview

This pipeline integrates multiple tools to process nanopore sequencing data for plasmid assembly and analysis.

## Complete Workflow

### Step 0: Initialization

**Script**: `scripts/step0_initialize_analysis.py`

**Purpose**: 
- Validate input data structure
- Check software dependencies
- Generate `config.yaml` configuration file
- Create output directory structure

**Inputs**:
- `fast_pass/` folder (nanopore sequencing output)
- Project ID (optional, auto-generated if not provided)

**Outputs**:
- `config.yaml` - Pipeline configuration
- Output directory structure
- Dependency check report

**Usage**:
```bash
python scripts/step0_initialize_analysis.py \
  --input fast_pass/ \
  --output output/ \
  --project-id PROJECT_ID
```

### Step 1: Assembly and Annotation

**Script**: `scripts/step1_run_epi2me_workflow.py`

**Purpose**:
- Run epi2me wf-clone-validation workflow for each sample
- Perform assembly, polishing, and annotation
- Generate workflow reports

**Tool**: epi2me wf-clone-validation (Nextflow workflow)
- Repository: https://github.com/epi2me-labs/wf-clone-validation
- Documentation: See epi2me documentation

**Inputs**:
- Sample subfolders in `fast_pass/`
- Configuration from `config.yaml`

**Outputs**:
- `*.final.fasta` - Assembled sequences
- `*.final.fastq` - Processed reads
- `wf-clone-validation-report.html` - Workflow report
- Annotation files (if available)

**Key Parameters**:
- `--approx_size`: Approximate plasmid size (bp)
- `--coverage`: Target coverage (default: 50x)
- `--assembly_tool`: Flye or Canu (default: Flye)

**Usage**:
```bash
python scripts/step1_run_epi2me_workflow.py \
  --config config.yaml \
  --input fast_pass/ \
  --output output/01.assembly/
```

### Step 2: Fragment Splitting

**Script**: `scripts/step2_split_fragments.py`

**Purpose**:
- Split assembled FASTA files into fixed-length fragments
- Default fragment size: 2000 bp

**Tool**: `scripts/split_plasmid_fasta.py`

**Inputs**:
- `*.final.fasta` files from Step 1

**Outputs**:
- Fragmented FASTA files in `output/02.fragments/{sample}_2k_fragmented/`

**Parameters**:
- `--fragment-size`: Fragment size in bp (default: 2000)

**Usage**:
```bash
python scripts/step2_split_fragments.py \
  --input output/01.assembly/ \
  --output output/02.fragments/ \
  --fragment-size 2000
```

### Step 3: AB1 File Generation

**Script**: `scripts/step3_generate_ab1.py`

**Purpose**:
- Convert fragmented FASTA files to AB1 chromatogram files
- Generate AB1 files for Sanger sequencing visualization

**Tool**: hyraxAbif
- Repository: https://github.com/hyraxbio/hyraxAbif
- Installation: See `archive/old_data/nanopore-plasmid_analysis_docker.txt`

**Inputs**:
- Fragmented FASTA directories from Step 2

**Outputs**:
- AB1 files in `output/03.ab1_files/{sample}_ab1/`

**Usage**:
```bash
python scripts/step3_generate_ab1.py \
  --input output/02.fragments/ \
  --output output/03.ab1_files/ \
  --hyraxabif-path /opt/hyraxAbif/hyraxAbif-exe
```

### Step 4: Report Generation

**Script**: `scripts/step4_generate_reports.py`

**Purpose**:
- Generate comprehensive PDF reports for each sample
- Include coverage plots, statistics, and visualizations

**Tool**: `scripts/generate_complete_reports.py`

**Inputs**:
- FASTA files from Step 1
- FASTQ files from Step 1
- Coverage data (if available)

**Outputs**:
- PDF reports in `output/04.reports/`
- Coverage plots
- Read length distributions

**Usage**:
```bash
python scripts/step4_generate_reports.py \
  --fasta-dir output/01.assembly/ \
  --fastq-dir output/01.assembly/ \
  --output output/04.reports/
```

### Step 5: Result Summary

**Script**: `scripts/step5_summarize_results.py`

**Purpose**:
- Generate summary JSON with key metrics
- Create summary visualizations
- Generate final HTML report

**Inputs**:
- All results from previous steps

**Outputs**:
- `result.json` - Summary metrics
- Summary plots in `output/05.summary/summary_plots/`
- Final HTML report

**Usage**:
```bash
python scripts/step5_summarize_results.py \
  --input output/ \
  --output output/05.summary/
```

## Running the Complete Pipeline

### Using Main Entry Script

```bash
python scripts/run_pipeline.py \
  --input fast_pass/ \
  --output output/ \
  --project-id PROJECT_ID \
  --fragment-size 2000 \
  --coverage 50
```

### Step-by-Step Execution

```bash
# Step 0: Initialize
python scripts/step0_initialize_analysis.py --input fast_pass/ --output output/

# Step 1: Assembly
python scripts/step1_run_epi2me_workflow.py --config config.yaml

# Step 2: Fragment splitting
python scripts/step2_split_fragments.py --input output/01.assembly/

# Step 3: AB1 generation
python scripts/step3_generate_ab1.py --input output/02.fragments/

# Step 4: Reports
python scripts/step4_generate_reports.py --fasta-dir output/01.assembly/

# Step 5: Summary
python scripts/step5_summarize_results.py --input output/
```

## Configuration File

The `config.yaml` file contains all pipeline parameters:

```yaml
project:
  project_id: "PROJECT_ID"
  input_dir: "fast_pass"
  output_dir: "output"
  
assembly:
  tool: "epi2me_wf_clone_validation"
  workflow_version: "latest"
  approx_size: 5000
  coverage: 50
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
```

## Output Files

### Assembly Results
- `{sample}.final.fasta` - Assembled sequences
- `{sample}.final.fastq` - Processed reads
- `wf-clone-validation-report.html` - Workflow report

### Fragments
- `{sample}_2k_fragmented/{sample}_{contig}_part{N}.fasta` - Fragment files

### AB1 Files
- `{sample}_ab1/{sample}_{contig}_part{N}.ab1` - Chromatogram files

### Reports
- `{sample}_report.pdf` - Comprehensive PDF report
- Coverage plots and statistics

## Troubleshooting

See `docs/TROUBLESHOOTING.md` for common issues and solutions.

## References

- epi2me wf-clone-validation: https://github.com/epi2me-labs/wf-clone-validation
- hyraxAbif: https://github.com/hyraxbio/hyraxAbif
- Nextflow: https://www.nextflow.io/

