# Coverage Plot Generation Process

This document explains how coverage plots are generated in the `generate_complete_reports.py` script.

## Overview

Coverage plots visualize the sequencing depth across a reference genome/contig. They show how many sequencing reads cover each position in the reference sequence.

## Generation Workflow

### Step 1: Compute Coverage (`compute_coverage` function)

Location: `generate_coverage_reports.py`

**Process:**

1. **Read Reference Sequence**
   - Load FASTA file containing the assembled contig
   - Extract the contig sequence (reference genome)

2. **Initialize Coverage Array**
   - Create a zero-filled array with length equal to the reference sequence
   - One element per base pair position

3. **Align Reads from FASTQ**
   - Iterate through all reads in the FASTQ file
   - For each read:
     - Try to align the read sequence to the reference using `simple_align()`
     - If alignment found (forward strand):
       - Mark each position covered by the read
       - Increment coverage array at those positions
     - If no forward alignment found:
       - Try reverse complement alignment
       - If reverse complement aligns, mark those positions

4. **Calculate Statistics**
   - **Average Coverage**: Mean of all coverage values
   - **Max Coverage**: Maximum coverage value
   - **Mapped Reads**: Number of reads successfully aligned
   - **Total Reads**: Total number of reads processed

5. **Generate Per-Base Details**
   - Create CSV file with per-base breakdown:
     - Position
     - Base (consensus)
     - Depth (coverage at that position)
     - Match count
     - Variant allele frequency (VAF)
     - Base counts (A, T, G, C)
     - Quality score
     - Confidence level

6. **Identify Low Confidence Bases**
   - Mark positions with coverage < 3x as "low confidence"
   - Also mark positions with VAF < 0.8 as low confidence
   - Export to separate CSV file

### Step 2: Create Coverage Plot (`create_coverage_plot` function)

Location: `generate_coverage_reports.py`

**Visualization Steps:**

1. **Setup Plot**
   - Create figure with matplotlib (12x4 inches)
   - Set axis labels and title

2. **Plot Coverage**
   - **Line Plot**: Blue line showing coverage at each position
     - Color: `#0079a4` (AmpSeq brand color)
     - Line width: 0.5
     - Alpha: 0.7
   - **Fill Area**: Light blue filled area under the curve
     - Alpha: 0.3
     - Visual representation of total coverage

3. **Mark Low Confidence Regions**
   - For positions with coverage < 3x:
     - Add orange 'x' markers
     - Size: 20 pixels
     - Alpha: 0.6
     - Label: "Low confidence"
   - These indicate regions with insufficient sequencing depth

4. **Add Statistics Box**
   - Display in upper-left corner:
     - Average coverage (e.g., "Avg: 29.1x")
     - Maximum coverage (e.g., "Max: 90x")
   - Background: wheat/tan color with transparency

5. **Formatting**
   - Grid lines: light gray, alpha 0.3
   - X-axis: Position (bp)
   - Y-axis: Coverage (x)
   - Title: "{contig_name} Coverage Map"
   - Legend: Shows "Low confidence" markers

6. **Save Plot**
   - Save as PNG file (150 DPI)
   - Filename: `{sample_name}_{contig_name}_coverage.png`
   - Location: `{sample}/PER_BASE_BREAKDOWN/`

## Alignment Method

The `simple_align()` function uses a basic string matching approach:

1. **Sliding Window**
   - Try to find the read sequence at different positions in the reference
   - Check both forward and reverse complement orientations
   - Minimum match length: 20 bases
   - Match threshold: >70% identity

2. **Best Match Selection**
   - Choose the position with highest match score
   - If score < 70%, read is considered unmapped

## Example Output

For a contig of 5,000 bp:
- X-axis: 0 to 5,000 bp
- Y-axis: 0 to 90x coverage
- Blue line shows coverage variation across the genome
- Orange 'x' marks indicate regions with coverage < 3x (low confidence)
- Statistics box shows: "Avg: 29.1x, Max: 90x"

## Usage

The coverage plot is automatically generated when running:

```bash
python3 generate_complete_reports.py -d ../../USX140904 -o ../USX140904 --project-id USX140904
```

The plot is included in the PDF report and also saved as a separate PNG file.

## Technical Details

- **Alignment**: Simple string matching (not full alignment algorithm)
- **Coverage Calculation**: Per-base depth counting
- **Low Confidence Threshold**: Coverage < 3x or VAF < 0.8
- **Plot Resolution**: 150 DPI
- **File Format**: PNG

