#!/usr/bin/env python3
"""
Step 2: Split assembled FASTA files into fragments.

This script splits each assembled FASTA file into fixed-length fragments (default 2kb).
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from Bio import SeqIO

def setup_logging(output_dir, verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory
    logs_dir = Path(output_dir) / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / 'step2_split_fragments.log'
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file))
        ],
        force=True
    )

def find_fasta_files(assembly_dir):
    """Find all .final.fasta files in assembly directory.
    
    Only searches the top-level assembly directory, excluding work/ subdirectories
    to avoid processing Nextflow intermediate files.
    """
    assembly_path = Path(assembly_dir)
    fasta_files = []
    
    # Only search in the top-level directory, not in work/ subdirectories
    # This avoids processing Nextflow intermediate files
    # Use iterdir() to explicitly check only direct children
    for item in assembly_path.iterdir():
        if item.is_file() and item.name.endswith('.final.fasta'):
            fasta_files.append(item)
    
    return sorted(fasta_files)  # Sort for consistent processing order

def split_seq(record, outdir, sample, size):
    """Split a single sequence record into fragments.
    
    Output format matches hyraxAbif requirements:
    - Header: "> 1.0" (with space after >, 1.0 means 100% confidence)
    - Sequence written in 80-character lines
    """
    seq = str(record.seq)
    L = len(seq)
    i = 0
    idx = 1
    fragment_count = 0
    
    while i < L:
        part = seq[i:i+size]
        fname = Path(outdir) / f"{sample}_part{idx}.fasta"
        
        # Use "> 1.0" format required by hyraxAbif (space after >, 1.0 = 100% confidence)
        header = "> 1.0"
        
        with open(fname, "w") as fh:
            fh.write(header + "\n")
            # Write sequence in 80-character lines
            for j in range(0, len(part), 80):
                fh.write(part[j:j+80] + "\n")
        
        fragment_count += 1
        idx += 1
        i += size
    
    return fragment_count

def split_sample_fasta(fasta_file, output_dir, sample_name, fragment_size):
    """Split a single FASTA file into fragments."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Ensure output directory is writable
    if not output_path.exists() or not os.access(str(output_path), os.W_OK):
        raise PermissionError(f"Output directory is not writable: {output_path}")
    
    records = list(SeqIO.parse(fasta_file, "fasta"))
    if not records:
        logging.warning(f"No records found in {fasta_file}")
        return 0
    
    total_fragments = 0
    for rec in records:
        # If multiple contigs, append contig id
        sample_prefix = sample_name
        if len(records) > 1:
            sample_prefix = f"{sample_name}_{rec.id}"
        
        fragment_count = split_seq(rec, output_path, sample_prefix, fragment_size)
        total_fragments += fragment_count
        logging.debug(f"  Split contig {rec.id} into {fragment_count} fragments")
    
    return total_fragments

def split_fragments(input_dir, output_dir, fragment_size=2000, verbose=False):
    """Split all FASTA files into fragments."""
    setup_logging(output_dir, verbose)
    
    logging.info("=" * 80)
    logging.info("Step 2: Splitting FASTA Files into Fragments")
    logging.info("=" * 80)
    
    # Find all FASTA files
    fasta_files = find_fasta_files(input_dir)
    logging.info(f"Found {len(fasta_files)} FASTA files to process")
    
    if not fasta_files:
        logging.warning("No FASTA files found!")
        return str(output_dir)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each FASTA file
    for fasta_file in fasta_files:
        # Extract sample name from filename (e.g., sample02.final.fasta -> sample02)
        # Remove .final.fasta extension and get base name
        sample_name = fasta_file.stem.replace('.final', '')
        
        # Validate sample name (should start with 'sample' and have digits)
        if not sample_name or not sample_name.startswith('sample'):
            # Fallback: use filename without extension
            sample_name = fasta_file.stem.replace('.final', '')
            logging.warning(f"Unexpected filename format: {fasta_file.name}, using '{sample_name}' as sample name")
        
        logging.info(f"Processing {fasta_file.name} -> sample: {sample_name}")
        
        # Create sample-specific output directory
        sample_output = output_path / f"{sample_name}_2k_fragmented"
        sample_output.mkdir(parents=True, exist_ok=True)
        
        try:
            fragment_count = split_sample_fasta(
                fasta_file=fasta_file,
                output_dir=sample_output,
                sample_name=sample_name,
                fragment_size=fragment_size
            )
            if fragment_count > 0:
                logging.info(f"✓ Split {fasta_file.name} into {fragment_count} fragments")
            else:
                logging.warning(f"No fragments generated for {fasta_file.name}")
        except Exception as e:
            logging.error(f"Failed to process {fasta_file}: {e}")
            import traceback
            logging.error(traceback.format_exc())
    
    logging.info("\n" + "=" * 80)
    logging.info("Fragment splitting complete!")
    logging.info("=" * 80)
    
    return str(output_path)

def main():
    parser = argparse.ArgumentParser(description='Step 2: Split FASTA files into fragments')
    parser.add_argument('--input', '-i', required=True, help='Input assembly directory')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('--fragment-size', type=int, default=2000, help='Fragment size in bp')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    try:
        output_dir = split_fragments(
            input_dir=args.input,
            output_dir=args.output,
            fragment_size=args.fragment_size,
            verbose=args.verbose
        )
        print(f"Fragments output: {output_dir}")
        return 0
    except Exception as e:
        logging.error(f"Fragment splitting failed: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return 1

if __name__ == '__main__':
    sys.exit(main())
