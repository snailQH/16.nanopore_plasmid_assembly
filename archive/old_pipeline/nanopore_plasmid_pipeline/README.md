# Nanopore Plasmid Assembly Pipeline

A comprehensive pipeline for analyzing nanopore-derived plasmid sequencing data, including assembly, polishing, annotation, and visualization.

## Overview

This pipeline performs the following steps:
1. **Data Quality Control**: Read filtering and quality assessment
2. **Assembly**: De novo assembly using Flye
3. **Polishing**: Consensus improvement using Medaka
4. **Annotation**: Gene prediction and annotation using Prokka
5. **Visualization**: Plasmid maps, coverage plots, and read statistics
6. **Validation**: Read mapping back to assemblies for validation
7. **Reporting**: Comprehensive HTML report with all results

## Dependencies

### Required Software
- **Flye**: De novo assembly
- **Medaka**: Consensus polishing
- **Prokka**: Genome annotation
- **NanoPlot**: Read quality visualization
- **minimap2**: Read alignment
- **samtools**: BAM file manipulation
- **bedtools**: Coverage analysis

### Python Packages
- pandas
- matplotlib
- seaborn
- jinja2
- biopython
- numpy

## Installation

### Using Conda (Recommended)
```bash
# Create environment
conda create -n plasmid_pipeline python=3.9
conda activate plasmid_pipeline

# Install bioinformatics tools
conda install -c bioconda flye medaka prokka nanoplot minimap2 samtools bedtools

# Install Python packages
pip install -r requirements.txt
```

### Manual Installation
Install each tool individually following their respective documentation.

## Usage

```bash
python plasmid_pipeline.py \
    --input nanopore_plasmid_pass.fastq.gz \
    --output results \
    --threads 16 \
    --expected-plasmids 5
```

## Output

The pipeline generates:
- Assembled plasmid sequences (FASTA)
- Annotated genomes (GBK, GFF)
- Coverage plots and statistics
- Plasmid maps and visualizations
- Read quality reports
- Comprehensive HTML report

## Parameters

- `--input`: Input FASTQ file (gzipped)
- `--output`: Output directory
- `--threads`: Number of threads (default: 4)
- `--expected-plasmids`: Expected number of plasmids (default: 1)
- `--min-read-length`: Minimum read length to keep (default: 1000)
- `--genome-size`: Estimated genome size for Flye (default: auto-detect)

## Citation

If you use this pipeline in your research, please cite the following tools:
- Flye: Kolmogorov et al. (2019) Nature Biotechnology
- Medaka: Oxford Nanopore Technologies
- Prokka: Seemann (2014) Bioinformatics
