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
import subprocess
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

def merge_fastq_files(fastq_files, output_file):
    """Merge multiple FASTQ.gz files into one file.
    
    Args:
        fastq_files: List of Path objects for input FASTQ files
        output_file: Path object for output merged FASTQ.gz file
    
    Returns:
        Path object of merged file if successful, None otherwise
    """
    if not fastq_files:
        return None
    
    if len(fastq_files) == 1:
        # Only one file, just copy it
        output_file.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(fastq_files[0], output_file)
        return output_file
    
    # Multiple files, merge them using zcat/cat and gzip
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Build command: zcat file1.gz file2.gz ... | gzip > output.gz
        cmd = ['zcat'] + [str(f) for f in fastq_files]
        
        with open(output_file, 'wb') as f_out:
            proc1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc2 = subprocess.Popen(['gzip'], stdin=proc1.stdout, stdout=f_out, stderr=subprocess.PIPE)
            proc1.stdout.close()  # Allow proc1 to receive SIGPIPE if proc2 exits
            _, stderr1 = proc1.communicate()
            _, stderr2 = proc2.communicate()
            
            if proc1.returncode != 0:
                logging.error(f"Failed to merge FASTQ files: {stderr1.decode()}")
                return None
            if proc2.returncode != 0:
                logging.error(f"Failed to compress merged FASTQ: {stderr2.decode()}")
                return None
        
        return output_file
    except Exception as e:
        logging.error(f"Error merging FASTQ files: {e}")
        return None

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
    # We'll create new barcode directories with merged files if needed
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
    # Strategy: Merge multiple FASTQ files per sample into a single file,
    # then create new barcode directories with merged files to avoid Nextflow conflicts
    
    samplesheet_data = []
    barcode_dirs_created = []
    
    for idx, sample_dir in enumerate(sorted(sample_dirs), start=1):
        sample_id = sample_dir.name
        fastq_files = find_fastq_files(sample_dir)
        
        if not fastq_files:
            logging.warning(f"No FASTQ files found in {sample_dir}")
            continue
        
        # Determine barcode name
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
        
        # Create barcode directory and merge FASTQ files
        barcode_dir = fast_pass_path / barcode
        
        # If barcode matches sample_id, use existing directory
        # Otherwise, create new directory with merged files
        if barcode == sample_id:
            # Already correct format, but may need to merge multiple files
            if len(fastq_files) > 1:
                logging.info(f"  {sample_id}: Merging {len(fastq_files)} FASTQ files into single file")
                merged_file = barcode_dir / f"{barcode}.fastq.gz"
                merged_result = merge_fastq_files(fastq_files, merged_file)
                if merged_result:
                    logging.info(f"    Merged FASTQ files -> {merged_file}")
                else:
                    logging.warning(f"    Failed to merge FASTQ files, using first file only")
                    # Fall back to using first file
            else:
                logging.info(f"  {sample_id}: Single FASTQ file, no merge needed")
        else:
            # Create new barcode directory (not a symlink to avoid Nextflow conflicts)
            if barcode_dir.exists():
                if barcode_dir.is_symlink():
                    # Remove existing symlink to avoid Nextflow conflicts
                    logging.info(f"  {sample_id}: Removing existing symlink {barcode}")
                    barcode_dir.unlink()
                    barcode_dir.mkdir(parents=True, exist_ok=True)
                elif barcode_dir.is_dir():
                    # Directory exists, check if it has files
                    existing_files = list(barcode_dir.glob("*.fastq*"))
                    if existing_files:
                        logging.info(f"  {sample_id}: Barcode directory {barcode} already exists with {len(existing_files)} file(s), reusing")
                    else:
                        logging.info(f"  {sample_id}: Barcode directory {barcode} exists but is empty, will add files")
                else:
                    # Exists but not a directory, remove and create directory
                    logging.warning(f"  {sample_id}: Removing existing non-directory {barcode}")
                    barcode_dir.unlink()
                    barcode_dir.mkdir(parents=True, exist_ok=True)
            else:
                barcode_dir.mkdir(parents=True, exist_ok=True)
            
            # Merge FASTQ files into barcode directory
            if len(fastq_files) > 1:
                logging.info(f"  {sample_id}: Merging {len(fastq_files)} FASTQ files -> {barcode}/")
                merged_file = barcode_dir / f"{barcode}.fastq.gz"
                merged_result = merge_fastq_files(fastq_files, merged_file)
                if merged_result:
                    logging.info(f"    Merged FASTQ files -> {merged_file}")
                    barcode_dirs_created.append((barcode, sample_id, True))
                else:
                    logging.warning(f"    Failed to merge FASTQ files, copying first file only")
                    import shutil
                    shutil.copy2(fastq_files[0], barcode_dir / f"{barcode}.fastq.gz")
                    barcode_dirs_created.append((barcode, sample_id, False))
            else:
                # Only one file, copy it
                import shutil
                merged_file = barcode_dir / f"{barcode}.fastq.gz"
                shutil.copy2(fastq_files[0], merged_file)
                logging.info(f"    Copied FASTQ file -> {merged_file}")
                barcode_dirs_created.append((barcode, sample_id, False))
        
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
    
    if barcode_dirs_created:
        merged_count = sum(1 for _, _, merged in barcode_dirs_created if merged)
        logging.info(f"Created {len(barcode_dirs_created)} barcode directories ({merged_count} with merged files)")
    
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

