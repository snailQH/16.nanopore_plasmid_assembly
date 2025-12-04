#!/usr/bin/env python3
"""
Step 3: Generate AB1 files from fragmented FASTA files.

This script uses hyraxAbif to convert fragmented FASTA files
into AB1 chromatogram files.
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

def setup_logging(output_dir, verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory
    logs_dir = Path(output_dir) / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / 'step3_generate_ab1.log'
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file))
        ]
    )

def find_fragment_dirs(fragments_dir):
    """Find all fragment directories."""
    fragments_path = Path(fragments_dir)
    fragment_dirs = [d for d in fragments_path.iterdir() if d.is_dir() and '_fragmented' in d.name]
    return fragment_dirs

def generate_ab1_for_sample(fragment_dir, output_dir, hyraxabif_exe, verbose=False):
    """Generate AB1 files for a single sample's fragments."""
    # Extract sample name from directory name
    sample_name = fragment_dir.name.replace('_2k_fragmented', '')
    
    # Create output directory for this sample
    sample_output = output_dir / f"{sample_name}_ab1"
    sample_output.mkdir(parents=True, exist_ok=True)
    
    # Check if hyraxAbif executable exists
    if not Path(hyraxabif_exe).exists():
        raise FileNotFoundError(f"hyraxAbif executable not found: {hyraxabif_exe}")
    
    # Run hyraxAbif
    cmd = [
        hyraxabif_exe,
        'gen',
        str(fragment_dir),
        str(sample_output)
    ]
    
    logging.info(f"Generating AB1 files for {sample_name}...")
    logging.debug(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logging.error(f"hyraxAbif failed for {sample_name}")
        if result.stderr:
            logging.error(f"Error: {result.stderr}")
        raise RuntimeError(f"AB1 generation failed for {sample_name}")
    
    # Count generated AB1 files
    ab1_files = list(sample_output.glob('*.ab1'))
    logging.info(f"✓ Generated {len(ab1_files)} AB1 files for {sample_name}")
    
    return sample_output

def generate_ab1_files(input_dir, output_dir, hyraxabif_exe='/opt/hyraxAbif/hyraxAbif-exe', verbose=False):
    """Generate AB1 files for all samples."""
    setup_logging(output_dir, verbose)
    
    logging.info("=" * 80)
    logging.info("Step 3: Generating AB1 Files")
    logging.info("=" * 80)
    
    # Find all fragment directories
    fragment_dirs = find_fragment_dirs(input_dir)
    logging.info(f"Found {len(fragment_dirs)} fragment directories to process")
    
    if not fragment_dirs:
        logging.warning("No fragment directories found!")
        return str(output_dir)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each sample
    successful = []
    failed = []
    
    for fragment_dir in fragment_dirs:
        try:
            generate_ab1_for_sample(
                fragment_dir=fragment_dir,
                output_dir=output_path,
                hyraxabif_exe=hyraxabif_exe,
                verbose=verbose
            )
            successful.append(fragment_dir.name)
        except Exception as e:
            logging.error(f"Failed to process {fragment_dir.name}: {e}")
            failed.append(fragment_dir.name)
    
    logging.info("\n" + "=" * 80)
    logging.info(f"Completed: {len(successful)}/{len(fragment_dirs)} samples")
    if failed:
        logging.warning(f"Failed samples: {', '.join(failed)}")
    logging.info("=" * 80)
    
    return str(output_path)

def main():
    parser = argparse.ArgumentParser(description='Step 3: Generate AB1 files')
    parser.add_argument('--input', '-i', required=True, help='Input fragments directory')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('--hyraxabif-exe', default='/opt/hyraxAbif/hyraxAbif-exe',
                       help='Path to hyraxAbif executable')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    try:
        output_dir = generate_ab1_files(
            input_dir=args.input,
            output_dir=args.output,
            hyraxabif_exe=args.hyraxabif_exe,
            verbose=args.verbose
        )
        print(f"AB1 files output: {output_dir}")
        return 0
    except Exception as e:
        logging.error(f"AB1 generation failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

