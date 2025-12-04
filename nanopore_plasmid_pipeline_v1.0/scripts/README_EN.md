# AmpSeq Plasmid Sequencing Report Generator

A comprehensive tool for generating professional PDF reports from nanopore plasmid sequencing data. This tool processes FASTA assembly files and FASTQ read files to generate detailed quality control reports with coverage plots, read length distributions, and per-base breakdowns.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Output Structure](#output-structure)
- [Report Contents](#report-contents)
- [Command-Line Options](#command-line-options)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [FAQs](#faqs)
- [Technical Details](#technical-details)

## ✨ Features

### Core Functionality

- **Automatic File Matching**: Intelligently matches FASTQ files to FASTA files by sample name, supporting various naming conventions
- **Per-Sample Organization**: Creates independent folders for each sample with organized subdirectories
- **Comprehensive Coverage Analysis**: Calculates read coverage depth and generates per-base coverage statistics
- **Visual Reports**: Generates publication-quality PDF reports with:
  - Coverage plots for each contig
  - Read length distribution histograms
  - Assembly statistics tables
  - Per-base coverage breakdowns

### Advanced Features

- **Flexible Input Options**: Support for separate FASTA and FASTQ directories
- **Selective Processing**: Process specific samples or all samples
- **Progress Logging**: Detailed logging with progress indicators for long-running operations
- **Error Handling**: Robust error handling with informative error messages
- **Encoding Support**: Handles various file encodings gracefully

### File Matching Intelligence

The tool can match FASTQ files to samples using:
- **Exact patterns**: `{sample_name}.final.fastq`, `{sample_name}_reads.fastq.gz`
- **Name-containing patterns**: `PBE94302_pass_USX140904_6ebb3c45_d6847234_0.fastq.gz` (contains `USX140904`)
- **Priority**: Prefers `.final.` files when multiple matches exist

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Python Dependencies

Install required Python packages:

```bash
pip3 install reportlab matplotlib numpy --user
```

Or install all dependencies at once:

```bash
pip3 install reportlab matplotlib numpy gzip --user
```

### Verify Installation

```bash
python3 -c "import reportlab, matplotlib, numpy; print('All dependencies installed successfully!')"
```

### System Dependencies

- **None required**: All processing is done in Python, no external system tools needed

## 📁 Project Structure

```
wf-clone-validation_3721d4d6-1e08-4db4-861c-f373b6934c07/
├── scripts/                      # All script files
│   ├── generate_complete_reports.py    # Main report generation script
│   ├── generate_coverage_reports.py    # Coverage calculation module
│   ├── get_length_dist_from_fastq.py  # Read length distribution generator
│   └── README_EN.md                    # This file
├── output/                       # Input data directory (default)
│   ├── *.final.fasta             # Assembly FASTA files
│   ├── *.final.fastq             # Sequencing FASTQ files
│   ├── *.assembly_stats.tsv      # Assembly statistics (optional)
│   └── sample_status.txt         # Sample status information (optional)
└── results/                      # Output directory (default)
    └── {sample_name}/            # Per-sample output folders
        ├── FASTA_FILES/
        ├── RAW_FASTQ_FILES/
        ├── PER_BASE_BREAKDOWN/
        ├── QC_REPORTS/
        └── CHROMATOGRAM_FILES_ab1/
```

## 💻 Usage

### Basic Usage

From the `scripts/` directory:

```bash
cd scripts
python3 generate_complete_reports.py
```

This will:
- Read FASTA and FASTQ files from `../output/`
- Process all samples found
- Generate reports in `../results/{sample_name}/`

### Common Use Cases

#### Process All Samples with Default Paths

```bash
python3 generate_complete_reports.py
```

#### Process Specific Samples

```bash
python3 generate_complete_reports.py --samples UPA42701 USX140904 UPA42703
```

#### Custom Input/Output Directories

```bash
python3 generate_complete_reports.py -d /path/to/data -o /path/to/output
```

#### Separate FASTA and FASTQ Directories

```bash
python3 generate_complete_reports.py \
  --fasta-dir /path/to/fasta_files \
  --fastq-dir /path/to/fastq_files \
  -o /path/to/output
```

#### Custom Project ID

```bash
python3 generate_complete_reports.py --project-id my_project_2024
```

#### Verbose Logging

```bash
python3 generate_complete_reports.py --verbose
```

### Quick Start Example

```bash
# 1. Navigate to scripts directory
cd scripts

# 2. Run with default settings (processes all samples)
python3 generate_complete_reports.py

# 3. Or process specific samples
python3 generate_complete_reports.py --samples UPA42701 USX140904
```

## 📊 Output Structure

Each sample gets its own folder with the following structure:

```
results/
└── {sample_name}/                    # e.g., UPA42701/
    ├── FASTA_FILES/                   # Split contig FASTA files
    │   └── {sample}_{contig}.fa       # e.g., UPA42701_UPA42701.fa
    ├── RAW_FASTQ_FILES/               # Copy of original FASTQ files
    │   └── {sample}_reads.fastq.gz    # e.g., UPA42701_reads.fastq.gz
    ├── PER_BASE_BREAKDOWN/            # Detailed coverage data
    │   ├── {sample}_{contig}_per_base_details.csv
    │   ├── {sample}_{contig}_low_confidence_bases.csv
    │   ├── {sample}_{contig}_coverage.png
    │   └── {sample}_read_length_dist.png
    ├── QC_REPORTS/                    # Final PDF reports
    │   └── {sample_name}_report.pdf
    └── CHROMATOGRAM_FILES_ab1/        # Empty (reserved for future use)
```

Additionally, a summary CSV file is generated:

```
results/{project_id}_summary.csv
```

## 📄 Report Contents

Each PDF report contains:

### 1. Header
- Company name: **AmpSeq**
- Website: **www.ampseq.com**
- Report title with sample name

### 2. Basic Information Statistics Table
- **Total DNA**: Total reads and bases from FASTQ file
- **Host Genomic DNA**: Number of contigs (sequences) and total bases from FASTA file, with percentages relative to FASTQ input

### 3. Assembly Status Table
For each contig:
- Contig name
- Length (bp)
- Reads mapped (count and percentage)
- Bases mapped (count and percentage)
- Multimer percentage
- Average coverage (X)
- Circular status
- Assembly status note (single contig vs. multiple contigs)

### 4. Coverage Plots
- One plot per contig
- Shows coverage depth across the entire contig
- Low confidence positions (< 3x coverage) marked with orange 'x'
- Plot dimensions: 6.5" × 3"

### 5. Read Length Distribution
- Histogram showing distribution of read lengths
- Generated from FASTQ file using integrated length distribution analysis
- Plot dimensions: 6.5" × 4"

## ⚙️ Command-Line Options

### Required Arguments
None (uses sensible defaults)

### Optional Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--data-dir` | `-d` | Directory containing FASTA and FASTQ files | `../output` |
| `--fasta-dir` | | Separate directory for FASTA files | Same as data-dir |
| `--fastq-dir` | | Separate directory for FASTQ files | Same as data-dir |
| `--output` | `-o` | Output base directory | `../results` |
| `--project-id` | | Project ID for summary CSV filename | Auto-generated (YYYYMMDD) |
| `--samples` | | Specific sample names to process (space-separated) | All samples found |
| `--verbose` | `-v` | Enable verbose logging | False |
| `--per-sample-folders` | | Create separate folder for each sample | True |

### Argument Details

#### `--data-dir` / `-d`
Base directory containing both FASTA and FASTQ files.
- Default: `../output` (relative to scripts directory)
- Used as fallback if `--fasta-dir` or `--fastq-dir` are not specified

#### `--fasta-dir`
Directory containing FASTA assembly files.
- Overrides `--data-dir` for FASTA files only
- Supports multiple file formats: `*.final.fasta`, `*.fa`, `*.fasta`
- Can extract sample names from various naming patterns:
  - `{sample}.final.fasta` → sample name
  - `{sample}_contig{num}.fa` → sample name
  - `{sample}.fa` → sample name

#### `--fastq-dir`
Directory containing FASTQ sequencing read files.
- Overrides `--data-dir` for FASTQ files only
- Supports compressed files: `*.fastq.gz`, `*.fq.gz`
- Automatically matches files containing sample names in filename

#### `--output` / `-o`
Base directory for output files.
- Default: `../results` (relative to scripts directory)
- Creates per-sample subdirectories automatically

#### `--project-id`
Project identifier used for summary CSV filename.
- Default: Current date in `YYYYMMDD` format
- Example: `20241103`
- Summary file: `{project_id}_summary.csv`

#### `--samples`
Process only specified samples (space-separated list).
- Example: `--samples UPA42701 USX140904 UPA42703`
- If a specified sample is not found, a warning is shown
- Processing continues with available samples

#### `--verbose` / `-v`
Enable detailed logging output.
- Shows debug information
- Displays progress for long operations (e.g., coverage calculation)
- Useful for troubleshooting

## 📚 Examples

### Example 1: Basic Usage

```bash
cd scripts
python3 generate_complete_reports.py
```

**What it does:**
- Finds all `*.final.fasta` files in `../output/`
- Matches corresponding FASTQ files
- Processes all samples
- Generates reports in `../results/{sample_name}/`

### Example 2: Process Specific Samples

```bash
python3 generate_complete_reports.py --samples UPA42701 USX140904
```

**What it does:**
- Only processes the two specified samples
- Skips other samples found in the directory
- Useful for testing or re-processing specific samples

### Example 3: Custom Directories

```bash
python3 generate_complete_reports.py \
  -d /data/sequencing/output \
  -o /data/reports/2024
```

**What it does:**
- Reads from `/data/sequencing/output`
- Writes to `/data/reports/2024`
- Uses absolute paths

### Example 4: Separate FASTA and FASTQ Locations

```bash
python3 generate_complete_reports.py \
  --fasta-dir /data/assemblies \
  --fastq-dir /data/raw_reads \
  -o /data/reports
```

**What it does:**
- Reads FASTA files from `/data/assemblies`
- Reads FASTQ files from `/data/raw_reads`
- Matches them by sample name
- Outputs to `/data/reports`

### Example 5: QB-Template Format Input

```bash
python3 generate_complete_reports.py \
  --fasta-dir /path/to/QB-template/1010612_FASTA_FILES \
  --fastq-dir /path/to/QB-template/1010612_RAW_FASTQ_FILES \
  -o /path/to/output \
  --project-id test_qb_template \
  --samples 001_N1 002_N2
```

**What it does:**
- Processes files organized in QB-template structure
- Matches `001_N1_contig001.fa` with `001_N1_reads.fastq.gz`
- Generates reports matching QB-template output format

### Example 6: Verbose Processing

```bash
python3 generate_complete_reports.py --verbose --samples UPA42701
```

**Output includes:**
- Detailed file matching information
- Progress updates during coverage calculation
- Read counting progress (every 10,000 reads)
- Debug information

## 🔧 Troubleshooting

### Problem: No samples found

**Symptoms:**
```
ERROR: No samples found to process!
```

**Solutions:**
1. Check that FASTA files exist:
   ```bash
   ls -la ../output/*.final.fasta
   ```

2. Verify the data directory path:
   ```bash
   python3 generate_complete_reports.py -d /path/to/data --verbose
   ```

3. Check file naming: FASTA files should be named `{sample}.final.fasta`

### Problem: FASTQ files not found

**Symptoms:**
```
WARNING: No FASTQ file found for sample: UPA42701
```

**Solutions:**
1. Verify FASTQ files exist:
   ```bash
   ls -la ../output/*.fastq*
   ```

2. Check file naming matches sample name:
   - Exact match: `UPA42701.final.fastq` ✓
   - Contains sample: `PBE94302_pass_UPA42701_xxx.fastq.gz` ✓
   - Wrong name: `sample1.fastq` ✗

3. Use separate FASTQ directory:
   ```bash
   python3 generate_complete_reports.py --fastq-dir /path/to/fastq/files
   ```

### Problem: Coverage calculation is slow

**Symptoms:**
- Script takes a very long time to process large FASTQ files
- High CPU usage

**Solutions:**
1. This is normal for large files. Use `--verbose` to see progress:
   ```bash
   python3 generate_complete_reports.py --verbose
   ```

2. Process samples individually to monitor progress:
   ```bash
   python3 generate_complete_reports.py --samples UPA42701
   ```

3. The script shows progress every 10,000 reads

### Problem: Encoding errors

**Symptoms:**
```
ERROR: 'utf-8' codec can't decode byte 0xb0
```

**Solution:**
This should be fixed in the latest version. If you still encounter it:
- Check file encoding: `file sample.fasta`
- The script uses `errors='ignore'` to handle encoding issues

### Problem: PDF generation fails

**Symptoms:**
```
WARNING: Coverage plot could not be generated
```

**Solutions:**
1. Check that matplotlib is installed:
   ```bash
   python3 -c "import matplotlib; print('OK')"
   ```

2. Check disk space:
   ```bash
   df -h
   ```

3. Check file permissions:
   ```bash
   ls -la ../results/
   ```

### Problem: Read length distribution plot missing

**Symptoms:**
```
Read length distribution plot could not be generated
```

**Solutions:**
1. Verify `get_length_dist_from_fastq.py` exists:
   ```bash
   ls -la get_length_dist_from_fastq.py
   ```

2. Check FASTQ file is readable:
   ```bash
   head -4 sample.fastq
   ```

3. Run with verbose mode for details:
   ```bash
   python3 generate_complete_reports.py --verbose
   ```

## ❓ FAQs

### Q1: What file formats are supported?

**FASTA formats:**
- `*.final.fasta` (preferred)
- `*.fa`
- `*.fasta`

**FASTQ formats:**
- `*.final.fastq`
- `*.final.fastq.gz` (compressed)
- `*.fastq`
- `*.fastq.gz` (compressed)
- `*.fq`
- `*.fq.gz` (compressed)

### Q2: How does file matching work?

The tool uses a two-stage matching process:

1. **Exact matching** (tried first):
   - `{sample}.final.fastq`
   - `{sample}_reads.fastq.gz`
   - `{sample}.fastq`

2. **Name-containing matching** (if no exact match):
   - Searches all FASTQ files
   - Matches files where `sample_name` appears in filename
   - Example: `PBE94302_pass_USX140904_xxx.fastq.gz` matches `USX140904`

### Q3: Can I process samples from different projects?

Yes! Use separate directories:
```bash
python3 generate_complete_reports.py \
  --fasta-dir /project1/assemblies \
  --fastq-dir /project1/reads \
  -o /project1/reports \
  --project-id project1
```

### Q4: How do I skip certain samples?

Process only the samples you want:
```bash
python3 generate_complete_reports.py --samples UPA42701 UPA42703
```

This will skip all other samples found in the directory.

### Q5: Can I re-run for updated files?

Yes! The script can be re-run. It will:
- Overwrite existing PDF reports
- Regenerate coverage plots
- Update summary CSV

To avoid overwriting, use different output directories or project IDs.

### Q6: What if I have multiple FASTQ files for one sample?

The tool uses the first match found. Priority:
1. Files with `.final.` in the name
2. Exact matches
3. Name-containing matches

If you need to use a specific file, rename it to match the exact pattern expected.

### Q7: How long does processing take?

Processing time depends on:
- **Number of reads**: Larger FASTQ files take longer
- **Number of contigs**: More contigs = more coverage calculations
- **File size**: Compressed files are faster to read

Typical processing times:
- Small sample (< 10,000 reads): 1-2 minutes
- Medium sample (10,000-100,000 reads): 5-10 minutes
- Large sample (> 100,000 reads): 15-30+ minutes

### Q8: What information is in the summary CSV?

The `{project_id}_summary.csv` contains:
- Sample Name
- Total Read Count (from FASTQ)
- Total Base Count (from FASTQ)
- E-coli Read Count (placeholder: 0)
- E-coli Base Count (placeholder: 0)
- Contig Name
- Contig Length (bp)
- Reads Mapped to Contig
- Bases Mapped to Contig
- Multimer percentage
- Coverage (X)
- Is Circular
- Reaction Status

One row per contig per sample.

### Q9: Can I customize the PDF reports?

Currently, PDF reports are generated with fixed formatting. Customization options:
- Company name and website (hardcoded as "AmpSeq" and "www.ampseq.com")
- Report sections and layout (fixed structure)

For major customizations, modify `generate_sample_pdf()` function in the script.

### Q10: What is "Host Genomic DNA" in the statistics?

"Host Genomic DNA" refers to the assembled sequences (contigs) from the FASTA file:
- **Reads column**: Number of contigs/sequences in FASTA
- **Bases column**: Total length of all contigs combined
- **Percentages**: Relative to the total reads/bases in the FASTQ input file

This represents the "assembled genome" versus the "raw sequencing reads."

## 🔬 Technical Details

### Coverage Calculation

The tool uses a simple alignment algorithm to map FASTQ reads to FASTA contigs:

1. **Alignment method**: Sliding window with minimum match threshold (70%)
2. **Strand handling**: Tries both forward and reverse complement
3. **Coverage depth**: Counts number of reads covering each base position
4. **Low confidence**: Bases with < 3x coverage are marked as low confidence

### Read Length Distribution

Generated using `get_length_dist_from_fastq.py`:
- Reads FASTQ file (supports gzip)
- Calculates length of each read
- Generates histogram using matplotlib
- Saves as PNG image for PDF inclusion

### File Processing Order

1. **Sample discovery**: Find all FASTA files, extract sample names
2. **File organization**: Create per-sample directory structure
3. **FASTA processing**: Split multi-contig FASTA into individual files
4. **FASTQ matching**: Find corresponding FASTQ files (exact match or name-containing match)
5. **Coverage calculation**: Align reads to reference, compute per-base coverage
6. **Per-base breakdown**: Generate detailed CSV files with coverage, base counts, VAF
7. **Plot generation**: Create coverage plots and read length distribution
8. **PDF assembly**: Combine all data into comprehensive PDF report

## 🔗 Additional Resources

### Coverage Plot Generation

For detailed information about how coverage plots are generated, see:
- `COVERAGE_PLOT_GENERATION.md` - Complete technical documentation

### Related Scripts

- `extract_sample_reports.py` - Extract individual sample reports from HTML
- `generate_ampseq_reports.py` - Legacy report generator
- `get_length_dist_from_fastq.py` - Standalone read length distribution tool
- `generate_pdfs.sh` - HTML to PDF conversion script

## 📞 Support

- **Website**: www.ampseq.com
- **Company**: AmpSeq

---

## 📝 Version History

### Current Version
- Automatic FASTQ/FASTA file matching (exact and name-containing patterns)
- Per-sample folder organization
- Comprehensive coverage analysis with per-base breakdowns
- Read length distribution integration
- Percentage statistics in Assembly Status table
- Detailed logging and progress indicators
- Support for various file formats and encodings

---

**Last Updated**: 2024-11-03
