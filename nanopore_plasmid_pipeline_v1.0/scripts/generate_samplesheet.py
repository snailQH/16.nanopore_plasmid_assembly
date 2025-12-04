#!/usr/bin/env python3
"""
Generate samplesheet CSV for epi2me wf-clone-validation workflow.

The samplesheet format for epi2me wf-clone-validation should have columns:
- barcode: Subdirectory name (used as barcode identifier)
- alias: Sample identifier/name
- type: Sample type (test_sample, positive_control, negative_control, no_template_control)
- approx_size: Optional approximate plasmid size (bp)

Reference: https://github.com/epi2me-labs/wf-clone-validation

Usage:
    python generate_samplesheet.py --fast-pass fast_pass/ --out samplesheet.csv
"""

import argparse
import csv
import logging
import sys
from pathlib import Path

def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def find_fastq_files(sample_dir):
    """Find all FASTQ files in a sample directory."""
    fastq_files = []
    sample_path = Path(sample_dir)
    
    # Look for common FASTQ patterns
    patterns = ['*.fastq', '*.fastq.gz', '*.fq', '*.fq.gz']
    for pattern in patterns:
        fastq_files.extend(list(sample_path.glob(pattern)))
    
    return sorted(fastq_files)

def generate_samplesheet(fast_pass_dir, output_file, approx_size=None, verbose=False):
    """Generate samplesheet CSV from fast_pass directory structure.
    
    Args:
        fast_pass_dir: Path to fast_pass directory containing sample subdirectories
        output_file: Output samplesheet CSV file path
        approx_size: Optional approximate plasmid size (bp) to include in samplesheet
        verbose: Enable verbose logging
    
    Note:
        epi2me wf-clone-validation requires barcode format: barcodeXX (e.g., barcode01, barcode02)
        If subdirectories don't match this format, we create symbolic links with barcode names
    """
    setup_logging(verbose)
    
    fast_pass_path = Path(fast_pass_dir)
    
    if not fast_pass_path.exists():
        raise FileNotFoundError(f"fast_pass directory not found: {fast_pass_dir}")
    
    # Find all sample directories
    # Filter out symbolic links - we only want actual directories
    # We'll create symbolic links later for barcode mapping
    sample_dirs = [
        d for d in fast_pass_path.iterdir() 
        if d.is_dir() and not d.is_symlink()
    ]
    
    if not sample_dirs:
        raise ValueError(f"No sample directories found in {fast_pass_dir}")
    
    logging.info(f"Found {len(sample_dirs)} sample directories")
    
    # Generate samplesheet
    # epi2me wf-clone-validation requires barcode format: barcodeXX (e.g., barcode01, barcode02)
    # The barcode MUST match the subdirectory name in fast_pass/
    # If directories don't match barcode format, we need to create symbolic links
    
    samplesheet_data = []
    barcode_links_created = []
    
    for idx, sample_dir in enumerate(sorted(sample_dirs), start=1):
        sample_id = sample_dir.name
        fastq_files = find_fastq_files(sample_dir)
        
        if not fastq_files:
            logging.warning(f"No FASTQ files found in {sample_dir}")
            continue
        
        # Check if directory name already matches barcode format (barcodeXX)
        if sample_id.startswith('barcode') and len(sample_id) > 7:
            # Check if it's barcode followed by digits
            suffix = sample_id[7:]  # Everything after "barcode"
            if suffix.isdigit():
                # Already in correct format
                barcode = sample_id
                logging.info(f"  {sample_id}: Already in barcode format -> {barcode}")
            else:
                # Not in correct format, create barcode name
                barcode = f"barcode{idx:02d}"
                logging.warning(f"  {sample_id}: Directory name doesn't match barcode format, using {barcode}")
        else:
            # Not in barcode format, create barcode name
            barcode = f"barcode{idx:02d}"
            logging.info(f"  {sample_id}: Creating barcode mapping -> {barcode}")
        
        # Create symbolic link if barcode doesn't match directory name
        if barcode != sample_id:
            barcode_link_path = fast_pass_path / barcode
            if not barcode_link_path.exists():
                try:
                    # Create relative symbolic link
                    barcode_link_path.symlink_to(sample_dir.name)
                    barcode_links_created.append((barcode, sample_id))
                    logging.info(f"    Created symbolic link: {barcode} -> {sample_id}")
                except OSError as e:
                    logging.error(f"    Failed to create symbolic link {barcode} -> {sample_id}: {e}")
                    raise
        
        # Build row data
        # IMPORTANT: alias must NOT begin with 'barcode' (epi2me workflow validation rule)
        # If sample_id starts with 'barcode', use a different alias (e.g., sample01, sample02)
        if sample_id.startswith('barcode'):
            # For demo data where directory names are barcode01, barcode02, etc.
            # Extract the number and create alias like sample01, sample02
            barcode_num = sample_id[7:]  # Everything after "barcode"
            alias = f"sample{barcode_num}"
        else:
            # Use original sample ID as alias
            alias = sample_id
        
        row_data = {
            'barcode': barcode,
            'alias': alias,
        }
        
        # Add approx_size if provided
        if approx_size is not None:
            row_data['approx_size'] = str(approx_size)
        
        samplesheet_data.append(row_data)
        
        logging.info(f"  {sample_id}: {len(fastq_files)} FASTQ file(s) -> barcode: {barcode}, alias: {alias}")
    
    if barcode_links_created:
        logging.info(f"Created {len(barcode_links_created)} symbolic links for barcode mapping")
    
    # Write samplesheet CSV
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine fieldnames - include approx_size if provided
    if approx_size is not None:
        fieldnames = ['barcode', 'alias', 'approx_size']
    else:
        # Use minimal format: barcode,alias (type column not in demo data)
        fieldnames = ['barcode', 'alias']
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(samplesheet_data)
    
    logging.info(f"Samplesheet written to: {output_path}")
    logging.info(f"Total samples: {len(samplesheet_data)}")
    
    return str(output_path)

def main():
    parser = argparse.ArgumentParser(
        description='Generate samplesheet CSV for epi2me wf-clone-validation'
    )
    parser.add_argument('--fast-pass', required=True, help='Path to fast_pass directory')
    parser.add_argument('--out', required=True, help='Output samplesheet CSV file')
    parser.add_argument('--approx-size', type=int, help='Approximate plasmid size (bp) to include in samplesheet')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    try:
        samplesheet_file = generate_samplesheet(
            fast_pass_dir=args.fast_pass,
            output_file=args.out,
            approx_size=args.approx_size,
            verbose=args.verbose
        )
        print(f"Samplesheet: {samplesheet_file}")
        return 0
    except Exception as e:
        logging.error(f"Failed to generate samplesheet: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

