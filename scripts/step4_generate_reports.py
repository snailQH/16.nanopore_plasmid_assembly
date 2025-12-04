#!/usr/bin/env python3
"""
Step 4: Generate comprehensive reports.

This script uses generate_complete_reports.py to create PDF reports
and JSON summaries for all samples.
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
    
    log_file = logs_dir / 'step4_generate_reports.log'
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file))
        ]
    )

def generate_reports(fasta_dir, fastq_dir, output_dir, project_id=None, assembly_dir=None, ab1_dir=None, verbose=False):
    """Generate reports using generate_complete_reports.py."""
    setup_logging(output_dir, verbose)
    
    logging.info("=" * 80)
    logging.info("Step 4: Generating Reports")
    logging.info("=" * 80)
    
    # Get script directory
    script_dir = Path(__file__).parent
    report_script = script_dir / 'generate_complete_reports.py'
    
    if not report_script.exists():
        raise FileNotFoundError(f"generate_complete_reports.py not found: {report_script}")
    
    # Prepare command
    cmd = [
        'python3', str(report_script),
        '--fasta-dir', str(fasta_dir),
        '--fastq-dir', str(fastq_dir),
        '--output', str(output_dir),
        '--per-sample-folders'
    ]
    
    if project_id:
        cmd.extend(['--project-id', project_id])
    
    # Pass assembly_dir if provided (for reading circularity from GenBank files)
    if assembly_dir:
        cmd.extend(['--assembly-dir', str(assembly_dir)])
    
    # Pass ab1_dir if provided (for copying AB1 files to report directories)
    if ab1_dir:
        cmd.extend(['--ab1-dir', str(ab1_dir)])
    
    if verbose:
        cmd.append('--verbose')
    
    logging.info(f"Running report generation...")
    logging.debug(f"Command: {' '.join(cmd)}")
    
    # Run report generation
    result = subprocess.run(
        cmd,
        capture_output=not verbose,
        text=True
    )
    
    if result.returncode != 0:
        logging.error("Report generation failed")
        if result.stderr:
            logging.error(f"Error: {result.stderr}")
        raise RuntimeError("Report generation failed")
    
    logging.info("\n" + "=" * 80)
    logging.info("Report generation complete!")
    logging.info("=" * 80)
    
    return str(output_dir)

def main():
    parser = argparse.ArgumentParser(description='Step 4: Generate reports')
    parser.add_argument('--fasta-dir', required=True, help='Directory containing FASTA files')
    parser.add_argument('--fastq-dir', required=True, help='Directory containing FASTQ files')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('--project-id', help='Project ID')
    parser.add_argument('--assembly-dir', help='Directory containing assembly output files (for reading circularity from GenBank files)')
    parser.add_argument('--ab1-dir', help='Directory containing AB1 files (for copying to report directories)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    try:
        output_dir = generate_reports(
            fasta_dir=args.fasta_dir,
            fastq_dir=args.fastq_dir,
            output_dir=args.output,
            project_id=args.project_id,
            assembly_dir=args.assembly_dir,
            ab1_dir=args.ab1_dir,
            verbose=args.verbose
        )
        print(f"Reports output: {output_dir}")
        return 0
    except Exception as e:
        logging.error(f"Report generation failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

