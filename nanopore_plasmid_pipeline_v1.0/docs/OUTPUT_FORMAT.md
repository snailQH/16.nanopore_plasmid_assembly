# Nanopore Plasmid Assembly Pipeline - Output Format Documentation

**Version:** 1.0  
**Last Updated:** 2025-12-03  
**Author:** AmpSeq

---

## Table of Contents

1. [Overview](#overview)
2. [Output Directory Structure](#output-directory-structure)
3. [File Formats](#file-formats)
4. [Report Structure](#report-structure)
5. [Summary Files](#summary-files)
6. [Log Files](#log-files)
7. [File Naming Conventions](#file-naming-conventions)
8. [Data Interpretation](#data-interpretation)

---

## Overview

This document describes the output format and structure of the Nanopore Plasmid Assembly Pipeline. All outputs are organized in a hierarchical directory structure, with each step producing specific file types.

### Output Organization Principles

1. **Step-based directories**: Each pipeline step has its own output directory (`01.assembly/`, `02.fragments/`, etc.)
2. **Sample-based organization**: Reports are organized by sample in `04.reports/`
3. **Comprehensive logging**: All steps generate detailed log files
4. **Standard formats**: Outputs use standard bioinformatics formats (FASTA, FASTQ, GenBank, AB1, PDF, CSV)

---

## Output Directory Structure

### Complete Structure

```
output/
├── 01.assembly/                    # Step 1: Assembly results
│   ├── sample02.final.fasta        # Assembled plasmid sequences
│   ├── sample02.final.fastq        # Processed reads aligned to assembly
│   ├── sample02.insert.fasta       # Insert sequences (if primers provided)
│   ├── sample02.annotations.gbk    # GenBank format annotations
│   ├── sample02.annotations.bed    # BED format annotations
│   ├── sample02.assembly.maf       # Multiple alignment format
│   ├── sample02.assembly_stats.tsv # Assembly statistics
│   ├── samplesheet.csv             # Input samplesheet used
│   ├── sample_sheet.csv            # Alternative samplesheet format
│   ├── sample_status.txt           # Sample processing status
│   ├── feature_table.txt           # Feature annotation table
│   ├── plannotate.json             # Plannotate annotation JSON
│   ├── plannotate_report.json      # Plannotate report JSON
│   ├── wf-clone-validation-report.html # Workflow HTML report
│   ├── execution/                  # Nextflow execution reports
│   │   ├── report.html
│   │   ├── timeline.html
│   │   └── trace.txt
│   └── .nextflow/                  # Nextflow cache (if auto-installed)
│       └── nextflow                # Nextflow executable (if auto-installed)
│
├── 02.fragments/                   # Step 2: Fragment splitting results
│   ├── sample02_2k_fragmented/     # Sample-specific fragment directory
│   │   ├── sample02_part1.fasta   # First fragment (2000 bp)
│   │   └── sample02_part2.fasta   # Second fragment (remaining bp)
│   ├── sample03_2k_fragmented/
│   │   └── ...
│   └── logs/
│       └── step2_split_fragments.log
│
├── 03.ab1_files/                   # Step 3: AB1 chromatogram files
│   ├── sample02_ab1/               # Sample-specific AB1 directory
│   │   ├── sample02_part1.ab1     # AB1 file for first fragment
│   │   └── sample02_part2.ab1     # AB1 file for second fragment
│   ├── sample03_ab1/
│   │   └── ...
│   └── logs/
│       └── step3_generate_ab1.log
│
├── 04.reports/                     # Step 4: Final reports
│   ├── PROJECT_ID_summary.csv     # Summary CSV for all samples
│   ├── sample02/                   # Sample-specific report directory
│   │   ├── FASTA_FILES/           # Individual contig FASTA files
│   │   │   └── sample02_sample02.fa
│   │   ├── RAW_FASTQ_FILES/       # Processed FASTQ files
│   │   │   └── sample02_reads.fastq.gz
│   │   ├── PER_BASE_BREAKDOWN/    # Coverage and per-base statistics
│   │   │   ├── sample02_sample02_coverage.png
│   │   │   ├── sample02_sample02_per_base_details.csv
│   │   │   └── sample02_sample02_low_confidence_bases.csv
│   │   ├── QC_REPORTS/            # PDF reports
│   │   │   └── sample02_report.pdf
│   │   └── CHROMATOGRAM_FILES_ab1/ # AB1 files (copied from 03.ab1_files)
│   │       ├── sample02_part1.ab1
│   │       └── sample02_part2.ab1
│   ├── sample03/
│   │   └── ... (same structure)
│   └── logs/
│       └── step4_generate_reports.log
│
├── 05.summary/                     # Summary files (if generated)
├── config.yaml                     # Pipeline configuration file
└── logs/                           # Pipeline logs
    ├── pipeline.log                # Main pipeline execution log
    └── step0_initialize.log        # Initialization log
```

---

## File Formats

### 1. Assembly Files (`01.assembly/`)

#### FASTA Files

**File:** `sampleXX.final.fasta`

**Format:** Standard FASTA format

**Content:** Assembled plasmid sequence(s)

**Example:**
```
>sample02
ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
...
```

**Notes:**
- One sequence per file (circular plasmids)
- Sequence name = sample name
- May contain multiple contigs if assembly produced multiple sequences

#### FASTQ Files

**File:** `sampleXX.final.fastq`

**Format:** Standard FASTQ format

**Content:** Processed reads aligned to the assembly

**Example:**
```
@read1
ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
```

**Notes:**
- Contains reads used in assembly
- Quality scores included
- May be compressed (`.fastq.gz`)

#### GenBank Files

**File:** `sampleXX.annotations.gbk`

**Format:** GenBank format

**Content:** Annotated sequence with features (genes, CDS, etc.)

**Key Information:**
- **LOCUS line**: Contains circularity information (`circular` or `linear`)
- **FEATURES section**: Gene annotations, CDS, etc.
- **ORIGIN section**: Sequence data

**Example LOCUS line:**
```
LOCUS       sample02                3036 bp    DNA     circular   UNK 01-JAN-1980
```

**Notes:**
- Used to determine circularity for summary CSV
- Contains full annotation information
- Compatible with standard GenBank viewers

#### BED Files

**File:** `sampleXX.annotations.bed`

**Format:** BED format (Browser Extensible Data)

**Content:** Feature annotations in BED format

**Columns:**
1. Chromosome/contig name
2. Start position (0-based)
3. End position
4. Feature name
5. Score
6. Strand (+/-)

**Use:** Genome browser visualization

#### Assembly Statistics

**File:** `sampleXX.assembly_stats.tsv`

**Format:** Tab-separated values

**Columns:**
- Sample name
- Contig name
- Length (bp)
- Coverage
- Read count
- Other statistics

**Use:** Quick overview of assembly quality

### 2. Fragment Files (`02.fragments/`)

#### Fragment FASTA Files

**File:** `sampleXX_partN.fasta`

**Format:** FASTA format with specific header format

**Content:** Fragmented sequence (default: 2000 bp per fragment)

**Example:**
```
> 1.0
ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
...
> 2.0
ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG
...
```

**Notes:**
- **Header format**: `> N.0` (required for hyraxAbif)
- Fragment size: Default 2000 bp (configurable)
- Last fragment may be shorter if sequence length is not divisible by fragment size
- Fragments are numbered sequentially (1, 2, 3, ...)

### 3. AB1 Files (`03.ab1_files/`)

#### AB1 Chromatogram Files

**File:** `sampleXX_partN.ab1`

**Format:** AB1 format (Sanger sequencing chromatogram)

**Content:** Chromatogram data for fragment sequence

**Notes:**
- Compatible with standard Sanger sequencing analysis tools
- Can be opened in:
  - ApE
  - Sequencher
  - Geneious
  - 4Peaks
  - FinchTV
  - Other AB1 viewers
- File size: Typically 80-200 KB per file

### 4. Report Files (`04.reports/`)

#### PDF Reports

**File:** `sampleXX_report.pdf`

**Format:** PDF

**Content:** Comprehensive analysis report

**Sections:**
1. **Basic Information Statistics**
   - Total reads and bases
   - Host genomic DNA statistics
   - Percentages

2. **Assembly Status**
   - Contig information table
   - Length, coverage, mapped reads
   - Circularity status

3. **Coverage Maps**
   - Per-contig coverage plots
   - Low confidence positions marked

4. **Read Length Distribution**
   - Histogram of read lengths
   - Statistics

**Notes:**
- Professional formatting
- Company branding (AmpSeq)
- Date and page numbers
- Suitable for customer delivery

#### Coverage Plots

**File:** `sampleXX_contig_coverage.png`

**Format:** PNG image

**Content:** Coverage plot showing:
- Coverage depth across sequence
- Low confidence positions (orange 'x' markers)
- Average coverage line

**Use:** Visual quality assessment

#### Per-Base Breakdown

**File:** `sampleXX_contig_per_base_details.csv`

**Format:** CSV

**Columns:**
- Position
- Base
- Coverage
- Quality score
- Other metrics

**Use:** Detailed per-position analysis

#### Low Confidence Bases

**File:** `sampleXX_contig_low_confidence_bases.csv`

**Format:** CSV

**Content:** List of positions with low confidence

**Use:** Identify problematic regions

#### Read Length Distribution

**File:** `sampleXX_read_length_dist.png`

**Format:** PNG image

**Content:** Histogram of read lengths

**Use:** Quality control visualization

---

## Report Structure

### Per-Sample Report Directory

Each sample gets its own directory in `04.reports/`:

```
sampleXX/
├── FASTA_FILES/              # Individual contig FASTA files
│   └── sampleXX_contig.fa
├── RAW_FASTQ_FILES/          # Processed FASTQ files
│   └── sampleXX_reads.fastq.gz
├── PER_BASE_BREAKDOWN/       # Coverage and statistics
│   ├── sampleXX_contig_coverage.png
│   ├── sampleXX_contig_per_base_details.csv
│   └── sampleXX_contig_low_confidence_bases.csv
├── QC_REPORTS/               # PDF reports
│   └── sampleXX_report.pdf
└── CHROMATOGRAM_FILES_ab1/   # AB1 files
    ├── sampleXX_part1.ab1
    └── sampleXX_part2.ab1
```

### Report Components

#### 1. FASTA_FILES/

Contains individual FASTA files for each contig:
- One file per contig
- Named: `sampleXX_contigname.fa`
- Standard FASTA format

#### 2. RAW_FASTQ_FILES/

Contains processed FASTQ files:
- Compressed format (`.fastq.gz`)
- Contains reads used in assembly
- Quality scores included

#### 3. PER_BASE_BREAKDOWN/

Contains detailed per-base analysis:
- **Coverage plots**: PNG images showing coverage across sequence
- **Per-base details**: CSV with position-by-position metrics
- **Low confidence bases**: CSV listing problematic positions

#### 4. QC_REPORTS/

Contains PDF reports:
- Comprehensive analysis report
- Professional formatting
- Suitable for customer delivery

#### 5. CHROMATOGRAM_FILES_ab1/

Contains AB1 chromatogram files:
- Copied from `03.ab1_files/`
- One file per fragment
- Compatible with Sanger sequencing tools

---

## Summary Files

### Summary CSV

**File:** `PROJECT_ID_summary.csv`

**Format:** CSV (Comma-separated values)

**Content:** Summary statistics for all samples

**Columns:**

| Column | Description | Example |
|--------|-------------|---------|
| Sample Name | Sample identifier | `sample02` |
| Total Read Count | Total number of reads | `1234` |
| Total Base Count | Total bases sequenced | `1234567` |
| E-coli Read Count | Host contamination reads | `0` |
| E-coli Base Count | Host contamination bases | `0` |
| Contig Name | Contig identifier | `sample02` |
| Contig Length (bp) | Contig length | `3036` |
| Reads Mapped to Contig | Reads aligned to contig | `1234` |
| Bases Mapped to Contig | Bases aligned to contig | `1234567` |
| Multimer (by mass) | Multimer percentage | `0.00%` |
| Coverage | Average coverage depth | `407x` |
| Is Circular | Circularity status | `True` or `False` |
| Reaction Status | Processing status | `SUCCESS` |

**Example:**
```csv
Sample Name,Total Read Count,Total Base Count,E-coli Read Count,E-coli Base Count,Contig Name,Contig Length (bp),Reads Mapped to Contig,Bases Mapped to Contig,Multimer (by mass),Coverage,Is Circular,Reaction Status
sample02,1,3036,0,0,sample02,3036,1,3036,0.00%,1x,True,SUCCESS
sample03,1,3096,0,0,sample03,1189,0,0,0.00%,0x,False,SUCCESS
```

**Notes:**
- One row per contig (samples with multiple contigs have multiple rows)
- Circularity is read from GenBank files (`.annotations.gbk`)
- Coverage is calculated from mapped reads

---

## Log Files

### Main Pipeline Log

**File:** `logs/pipeline.log`

**Format:** Text log

**Content:** Complete pipeline execution log

**Format:**
```
[YYYY-MM-DD HH:MM:SS] Message
```

**Use:** Troubleshooting, execution tracking

### Step-Specific Logs

**Location:** `XX.step/logs/stepX_*.log`

**Examples:**
- `02.fragments/logs/step2_split_fragments.log`
- `03.ab1_files/logs/step3_generate_ab1.log`
- `04.reports/logs/step4_generate_reports.log`

**Content:** Detailed logs for each pipeline step

**Use:** Step-specific troubleshooting

### Nextflow Logs

**File:** `01.assembly/.nextflow.log`

**Content:** Nextflow workflow execution log

**Use:** Debugging assembly issues

---

## File Naming Conventions

### General Rules

1. **Sample names**: Extracted from input directory names or filenames
2. **Step prefixes**: Files prefixed with step number (`01.assembly/`, `02.fragments/`, etc.)
3. **Consistent naming**: Same sample name used across all steps

### Naming Patterns

| File Type | Pattern | Example |
|-----------|---------|---------|
| Assembly FASTA | `{sample}.final.fasta` | `sample02.final.fasta` |
| Assembly FASTQ | `{sample}.final.fastq` | `sample02.final.fastq` |
| GenBank | `{sample}.annotations.gbk` | `sample02.annotations.gbk` |
| Fragment | `{sample}_part{N}.fasta` | `sample02_part1.fasta` |
| AB1 | `{sample}_part{N}.ab1` | `sample02_part1.ab1` |
| Report PDF | `{sample}_report.pdf` | `sample02_report.pdf` |
| Summary CSV | `{project_id}_summary.csv` | `PROJECT_001_summary.csv` |

### Directory Naming

| Directory Type | Pattern | Example |
|----------------|---------|---------|
| Fragment directory | `{sample}_2k_fragmented` | `sample02_2k_fragmented` |
| AB1 directory | `{sample}_ab1` | `sample02_ab1` |
| Report directory | `{sample}` | `sample02` |

---

## Data Interpretation

### Understanding Coverage

**Coverage** = Average number of reads covering each base position

- **Low coverage** (< 10x): May have gaps or errors
- **Good coverage** (20-50x): Reliable assembly
- **High coverage** (50-100x): Very reliable, high quality
- **Very high coverage** (> 100x): Diminishing returns, slower processing

### Understanding Circularity

**Circular** (`True`): Plasmid forms a circular molecule
- Typical for plasmids
- Indicates complete assembly

**Linear** (`False`): Plasmid is linear
- May indicate incomplete assembly
- Or naturally linear construct

**Source:** Read from GenBank LOCUS line in `.annotations.gbk` file

### Understanding Fragment Files

**Fragment size**: Default 2000 bp
- Each fragment is ~2000 bp (last fragment may be shorter)
- Fragments are numbered sequentially (1, 2, 3, ...)
- Each fragment becomes one AB1 file

**Fragment count**: Depends on plasmid length
- 2000-4000 bp: 2 fragments
- 4000-6000 bp: 3 fragments
- etc.

### Understanding AB1 Files

**AB1 format**: Standard Sanger sequencing chromatogram format
- Contains base calls and quality scores
- Compatible with standard sequencing analysis tools
- Can be used for manual verification
- Can be imported into sequence assembly software

### Understanding Report PDFs

**Report sections**:
1. **Basic Statistics**: Overview of sequencing data
2. **Assembly Status**: Contig information and quality metrics
3. **Coverage Maps**: Visual representation of coverage
4. **Read Length Distribution**: Quality control visualization

**Use cases**:
- Customer delivery
- Quality assessment
- Publication figures
- Documentation

---

## Quality Metrics

### Assembly Quality Indicators

1. **Coverage depth**: Higher = better (aim for 20x+)
2. **Contig count**: 1 contig = ideal (circular plasmid)
3. **Circularity**: `True` = complete circular assembly
4. **Read mapping**: High percentage = good alignment

### Report Quality Indicators

1. **Coverage plots**: Smooth coverage = good quality
2. **Low confidence bases**: Fewer = better
3. **Read length distribution**: Consistent lengths = good quality
4. **Assembly status**: "single contig" = ideal

---

## File Size Estimates

### Typical File Sizes

| File Type | Typical Size | Notes |
|-----------|--------------|-------|
| Assembly FASTA | 3-10 KB | Depends on plasmid size |
| Assembly FASTQ | 100 KB - 10 MB | Depends on read count |
| GenBank file | 10-50 KB | Depends on annotation complexity |
| Fragment FASTA | 2-3 KB | ~2000 bp per fragment |
| AB1 file | 80-200 KB | Standard AB1 size |
| PDF report | 500 KB - 2 MB | Depends on number of plots |
| Coverage plot PNG | 50-200 KB | Image size |
| Summary CSV | 1-10 KB | Depends on sample count |

### Storage Requirements

**Per sample** (typical):
- Assembly files: ~1-10 MB
- Fragments: ~10-50 KB
- AB1 files: ~200-500 KB
- Reports: ~1-3 MB
- **Total per sample**: ~2-15 MB

**For 100 samples**: ~200 MB - 1.5 GB

---

## Compatibility

### Software Compatibility

| File Type | Compatible Software |
|-----------|---------------------|
| FASTA | Any sequence viewer/editor |
| FASTQ | Any read viewer/analyzer |
| GenBank | GenBank viewers, Geneious, SnapGene |
| BED | Genome browsers (IGV, UCSC) |
| AB1 | Sequencher, Geneious, 4Peaks, FinchTV |
| PDF | Any PDF viewer |
| CSV | Excel, Google Sheets, R, Python |

### Standard Formats

All outputs use standard bioinformatics formats:
- **FASTA**: Standard sequence format
- **FASTQ**: Standard read format
- **GenBank**: Standard annotation format
- **BED**: Standard genome browser format
- **AB1**: Standard Sanger sequencing format
- **PDF**: Standard document format
- **CSV**: Standard data format

---

## Best Practices

1. **Keep all outputs**: Don't delete intermediate files (useful for troubleshooting)
2. **Check logs first**: Always check log files when troubleshooting
3. **Verify file sizes**: Unusually small files may indicate errors
4. **Review summary CSV**: Quick overview of all samples
5. **Use PDF reports**: Best format for customer delivery
6. **Archive outputs**: Compress and archive for long-term storage

---

## Support

For questions about output formats:
- Check log files for detailed information
- Review this documentation
- Contact support: www.ampseq.com

---

**Last Updated:** 2025-12-03  
**Pipeline Version:** 1.0

