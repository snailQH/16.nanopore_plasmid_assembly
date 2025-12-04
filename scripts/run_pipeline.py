#!/usr/bin/env python3
"""
Main entry script for Nanopore Plasmid Assembly Pipeline (Docker Container Version).

This script runs INSIDE the Docker container and handles:
1. Initialization and configuration (if not skipped)
2. Fragment splitting
3. AB1 file generation
4. Report generation (PDF + JSON)

Note: Assembly (epi2me workflow) is handled by run_pipeline.sh on the HOST machine
      because Nextflow needs Docker access for process containers.

Usage:
    python run_pipeline.py --input fast_pass/ --output output/ --project-id PROJECT_ID
    (Usually called from run_pipeline.sh)
"""

import argparse
import logging
import os
import sys
import importlib.util
from pathlib import Path

# Import step scripts using importlib to handle relative imports
def import_step_module(module_name):
    """Import a step module dynamically."""
    script_dir = Path(__file__).parent
    module_path = script_dir / f"{module_name}.py"
    
    if not module_path.exists():
        raise ImportError(f"Module not found: {module_path}")
    
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import step modules
try:
    step0 = import_step_module('step0_initialize_analysis')
    step1 = import_step_module('step1_run_epi2me_workflow')
    step2 = import_step_module('step2_split_fragments')
    step3 = import_step_module('step3_generate_ab1')
    step4 = import_step_module('step4_generate_reports')
except ImportError as e:
    print(f"ERROR: Failed to import step scripts: {e}")
    print("Please ensure all step scripts are in the scripts directory")
    sys.exit(1)

def setup_logging(output_dir, verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory
    logs_dir = Path(output_dir) / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / 'pipeline.log'
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file))
        ]
    )

def main():
    parser = argparse.ArgumentParser(
        description='Nanopore Plasmid Assembly Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Input directory containing fast_pass/ folder with sample subdirectories'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        required=True,
        help='Output directory for all results'
    )
    
    parser.add_argument(
        '--project-id',
        type=str,
        default=None,
        help='Project ID (auto-generated if not provided)'
    )
    
    parser.add_argument(
        '--fragment-size',
        type=int,
        default=2000,
        help='Fragment size for splitting (default: 2000 bp)'
    )
    
    parser.add_argument(
        '--approx-size',
        type=int,
        default=5000,
        help='Approximate plasmid size for epi2me workflow (default: 5000 bp)'
    )
    
    parser.add_argument(
        '--coverage',
        type=int,
        default=50,
        help='Target coverage for epi2me workflow (default: 50x)'
    )
    
    parser.add_argument(
        '--skip-assembly',
        action='store_true',
        help='Skip assembly step (use existing assembly results)'
    )
    
    parser.add_argument(
        '--skip-fragments',
        action='store_true',
        help='Skip fragment splitting step'
    )
    
    parser.add_argument(
        '--skip-ab1',
        action='store_true',
        help='Skip AB1 generation step'
    )
    
    parser.add_argument(
        '--skip-reports',
        action='store_true',
        help='Skip report generation step'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Create output directory first
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Setup logging (after output dir is created)
    setup_logging(str(output_path), args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("Nanopore Plasmid Assembly Pipeline")
    logger.info("=" * 80)
    logger.info(f"Input directory: {args.input}")
    logger.info(f"Output directory: {args.output}")
    logger.info(f"Project ID: {args.project_id}")
    logger.info("=" * 80)
    
    # Validate input directory
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {args.input}")
        sys.exit(1)
    
    # Step 0: Initialization
    logger.info("\n[Step 0] Initializing analysis...")
    try:
        config_file = step0.initialize_analysis(
            input_dir=str(input_path),
            output_dir=str(output_path),
            project_id=args.project_id,
            approx_size=args.approx_size,
            coverage=args.coverage,
            fragment_size=args.fragment_size
        )
        logger.info(f"✓ Initialization complete. Config: {config_file}")
    except Exception as e:
        logger.error(f"✗ Initialization failed: {e}")
        sys.exit(1)
    
    # Step 1: Assembly (epi2me workflow)
    # NOTE: Assembly is now handled by run_pipeline.sh on the HOST machine
    # This allows Nextflow to use Docker containers for processes (medaka, flye, etc.)
    if not args.skip_assembly:
        logger.warning("\n[Step 1] Assembly step should be run on HOST using run_pipeline.sh")
        logger.warning("Skipping assembly in Docker container mode")
        logger.info("If you need to run assembly here, use run_pipeline.sh instead")
        assembly_dir = output_path / "01.assembly"
        # Check if assembly results already exist
        if not (assembly_dir / "samplesheet.csv").exists():
            logger.error("Assembly results not found. Please run run_pipeline.sh first.")
            sys.exit(1)
    else:
        logger.info("\n[Step 1] Skipping assembly step")
        assembly_dir = output_path / "01.assembly"
    
    # Step 2: Fragment splitting
    if not args.skip_fragments:
        logger.info("\n[Step 2] Splitting FASTA files into fragments...")
        try:
            fragments_dir = step2.split_fragments(
                input_dir=str(assembly_dir),
                output_dir=str(output_path / "02.fragments"),
                fragment_size=args.fragment_size
            )
            logger.info(f"✓ Fragment splitting complete. Results: {fragments_dir}")
        except Exception as e:
            logger.error(f"✗ Fragment splitting failed: {e}")
            sys.exit(1)
    else:
        logger.info("\n[Step 2] Skipping fragment splitting step")
        fragments_dir = output_path / "02.fragments"
    
    # Step 3: AB1 generation
    if not args.skip_ab1:
        logger.info("\n[Step 3] Generating AB1 files...")
        try:
            ab1_dir = step3.generate_ab1_files(
                input_dir=str(fragments_dir),
                output_dir=str(output_path / "03.ab1_files")
            )
            logger.info(f"✓ AB1 generation complete. Results: {ab1_dir}")
        except Exception as e:
            logger.error(f"✗ AB1 generation failed: {e}")
            sys.exit(1)
    else:
        logger.info("\n[Step 3] Skipping AB1 generation step")
        ab1_dir = output_path / "03.ab1_files"
    
    # Step 4: Report generation
    if not args.skip_reports:
        logger.info("\n[Step 4] Generating reports...")
        try:
            reports_dir = step4.generate_reports(
                fasta_dir=str(assembly_dir),
                fastq_dir=str(assembly_dir),
                output_dir=str(output_path / "04.reports"),
                project_id=args.project_id,
                assembly_dir=str(assembly_dir),  # Pass assembly_dir for reading circularity from GenBank files
                ab1_dir=str(ab1_dir)  # Pass ab1_dir for copying AB1 files to report directories
            )
            logger.info(f"✓ Report generation complete. Results: {reports_dir}")
        except Exception as e:
            logger.error(f"✗ Report generation failed: {e}")
            sys.exit(1)
    else:
        logger.info("\n[Step 4] Skipping report generation step")
    
    logger.info("\n" + "=" * 80)
    logger.info("Pipeline completed successfully!")
    logger.info(f"Results available in: {output_path}")
    logger.info("=" * 80)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

