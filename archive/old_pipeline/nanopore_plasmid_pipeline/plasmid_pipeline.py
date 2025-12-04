#!/usr/bin/env python3
"""
Nanopore Plasmid Assembly Pipeline
A comprehensive pipeline for analyzing nanopore-derived plasmid sequencing data.
"""

import os
import sys
import argparse
import subprocess
import logging
import shutil
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Import our custom modules
from utils.dependency_checker import check_dependencies
from utils.data_cleaner import clean_reads
from utils.assembler import run_flye_assembly
from utils.polisher import run_medaka_polish
from utils.annotator import run_prokka_annotation
from utils.visualizer import create_visualizations
from utils.validator import validate_assembly
from utils.reporter import generate_html_report

def setup_logging(output_dir):
    """Setup logging configuration"""
    log_file = os.path.join(output_dir, "pipeline.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def create_output_structure(output_dir):
    """Create the output directory structure"""
    subdirs = [
        "01_cleaned_reads",
        "02_assembly", 
        "03_polished",
        "04_annotated",
        "05_validation",
        "06_visualization",
        "07_reports"
    ]
    
    for subdir in subdirs:
        os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)
    
    return output_dir

def main():
    parser = argparse.ArgumentParser(
        description="Nanopore Plasmid Assembly Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python plasmid_pipeline.py --input reads.fastq.gz --output results
  python plasmid_pipeline.py --input reads.fastq.gz --output results --threads 16 --expected-plasmids 5
        """
    )
    
    # Required arguments
    parser.add_argument("--input", required=True, help="Input FASTQ file (gzipped)")
    parser.add_argument("--output", required=True, help="Output directory")
    
    # Optional arguments
    parser.add_argument("--threads", type=int, default=4, help="Number of threads (default: 4)")
    parser.add_argument("--expected-plasmids", type=int, default=1, help="Expected number of plasmids (default: 1)")
    parser.add_argument("--min-read-length", type=int, default=1000, help="Minimum read length to keep (default: 1000)")
    parser.add_argument("--genome-size", help="Estimated genome size for Flye (e.g., 5m, 10k)")
    parser.add_argument("--medaka-model", type=str, default="r1041_e81_fast_g5015", help="Medaka model to use for polishing (default: r1041_e81_fast_g5015)")
    parser.add_argument("--skip-cleaning", action="store_true", help="Skip read cleaning step")
    parser.add_argument("--skip-polishing", action="store_true", help="Skip Medaka polishing step")
    parser.add_argument("--skip-annotation", action="store_true", help="Skip Prokka annotation step")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        sys.exit(1)
    
    # Create output directory structure
    output_dir = create_output_structure(args.output)
    
    # Setup logging
    logger = setup_logging(output_dir)
    logger.info("Starting Nanopore Plasmid Assembly Pipeline")
    logger.info(f"Input file: {args.input}")
    logger.info(f"Output directory: {args.output}")
    logger.info(f"Threads: {args.threads}")
    logger.info(f"Expected plasmids: {args.expected_plasmids}")
    
    try:
        # Step 1: Check dependencies
        logger.info("Step 1: Checking dependencies...")
        missing_tools = check_dependencies()
        if missing_tools:
            logger.error(f"Missing required tools: {', '.join(missing_tools)}")
            logger.error("Please install missing tools and try again")
            sys.exit(1)
        logger.info("All dependencies found")
        
        # Step 2: Data cleaning
        if not args.skip_cleaning:
            logger.info("Step 2: Cleaning reads...")
            cleaned_reads = clean_reads(
                args.input, 
                output_dir, 
                min_length=args.min_read_length,
                threads=args.threads
            )
            logger.info(f"Cleaned reads saved to: {cleaned_reads}")
        else:
            logger.info("Skipping read cleaning step")
            cleaned_reads = args.input
        
        # Step 3: Assembly
        logger.info("Step 3: Running Flye assembly...")
        assembly_dir = os.path.join(output_dir, "02_assembly")
        assembly_result = run_flye_assembly(
            cleaned_reads,
            assembly_dir,
            threads=args.threads,
            genome_size=args.genome_size
        )
        logger.info(f"Assembly completed: {assembly_result}")
        
        # Step 4: Polishing
        if not args.skip_polishing:
            logger.info("Step 4: Running Medaka polishing...")
            polished_dir = os.path.join(output_dir, "03_polished")
            polished_result = run_medaka_polish(
                assembly_result,
                cleaned_reads,
                polished_dir,
                threads=args.threads,
                model=args.medaka_model
            )
            logger.info(f"Polishing completed: {polished_result}")
        else:
            logger.info("Skipping polishing step")
            polished_result = assembly_result
        
        # Step 5: Annotation
        if not args.skip_annotation:
            logger.info("Step 5: Running Prokka annotation...")
            annotated_dir = os.path.join(output_dir, "04_annotated")
            annotation_result = run_prokka_annotation(
                polished_result,
                annotated_dir,
                threads=args.threads
            )
            logger.info(f"Annotation completed: {annotation_result}")
        else:
            logger.info("Skipping annotation step")
            annotation_result = None
        
        # Step 6: Validation
        logger.info("Step 6: Validating assembly...")
        validation_dir = os.path.join(output_dir, "05_validation")
        validation_result = validate_assembly(
            polished_result,
            cleaned_reads,
            validation_dir,
            threads=args.threads
        )
        logger.info(f"Validation completed: {validation_result}")
        
        # Step 7: Visualization
        logger.info("Step 7: Creating visualizations...")
        viz_dir = os.path.join(output_dir, "06_visualization")
        viz_result = create_visualizations(
            polished_result,
            cleaned_reads,
            validation_result,
            viz_dir,
            threads=args.threads
        )
        logger.info(f"Visualizations completed: {viz_result}")
        
        # Step 8: Generate HTML report
        logger.info("Step 8: Generating HTML report...")
        report_dir = os.path.join(output_dir, "07_reports")
        report_file = generate_html_report(
            args.input,
            cleaned_reads,
            assembly_result,
            polished_result,
            annotation_result,
            validation_result,
            viz_result,
            report_dir,
            args
        )
        logger.info(f"HTML report generated: {report_file}")
        
        logger.info("Pipeline completed successfully!")
        logger.info(f"Results available in: {args.output}")
        logger.info(f"View the report at: {report_file}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 