#!/usr/bin/env python3
"""
Step 1: Run epi2me wf-clone-validation workflow.

This script wraps the epi2me wf-clone-validation Nextflow workflow
to process each sample in the fast_pass directory.
"""

import argparse
import logging
import os
import subprocess
import sys
import yaml
from pathlib import Path

def setup_logging(output_dir, verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory
    logs_dir = Path(output_dir) / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / 'step1_epi2me_workflow.log'
    
    # Get or create logger for this step
    logger = logging.getLogger('step1')
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Add handlers
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.addHandler(logging.FileHandler(str(log_file)))
    
    # Set format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    for handler in logger.handlers:
        handler.setFormatter(formatter)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def load_config(config_file):
    """Load configuration from YAML file."""
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def generate_samplesheet(fast_pass_dir, output_file, work_dir=None, logger=None):
    """Generate samplesheet CSV for epi2me workflow."""
    if logger is None:
        logger = logging.getLogger('step1')
    
    import importlib.util
    script_dir = Path(__file__).parent
    samplesheet_script = script_dir / 'generate_samplesheet.py'
    
    if not samplesheet_script.exists():
        raise FileNotFoundError(f"generate_samplesheet.py not found: {samplesheet_script}")
    
    cmd = [
        'python3', str(samplesheet_script),
        '--fast-pass', str(fast_pass_dir),
        '--out', str(output_file)
    ]
    
    # Add work-dir if provided (for read-only input directories)
    if work_dir:
        cmd.extend(['--work-dir', str(work_dir)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Failed to generate samplesheet: {result.stderr}")
        raise RuntimeError("Samplesheet generation failed")
    
    return output_file

def run_epi2me_workflow_batch(fast_pass_dir, samplesheet_file, output_dir, config, verbose=False, logger=None):
    """Run epi2me workflow for all samples using samplesheet."""
    if logger is None:
        logger = logging.getLogger('step1')
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Prepare Nextflow command according to epi2me wf-clone-validation documentation
    # Reference: https://github.com/epi2me-labs/wf-clone-validation
    # For case (iii): directory with subdirectories containing FASTQ files
    # Use --fastq pointing to the parent directory and --sample_sheet for mapping
    fast_pass_path = Path(fast_pass_dir)
    
    # Check if running inside Docker container
    # User confirmed successful test command:
    # NXF_VER=23.10.0 nextflow run epi2me-labs/wf-clone-validation -r v1.8.3 \
    #   --fastq '...' --sample_sheet '...' --out_dir '...' -profile standard
    # Note: -profile standard uses Docker containers for processes (medaka, flye, etc.)
    # So we need Docker socket mounted when running inside Docker
    is_docker = os.path.exists('/.dockerenv')
    profile = 'standard'  # Always use 'standard' profile as per user's successful test
    
    # Use short form workflow reference (works same as full URL)
    workflow_ref = 'epi2me-labs/wf-clone-validation'
    workflow_version = 'v1.8.3'  # Latest stable version
    
    # Set Nextflow version environment variable for compatibility
    # This is critical: NXF_VER=23.10.0 is required for v1.8.3 to work
    env = os.environ.copy()
    env['NXF_VER'] = '23.10.0'
    
    # Set Nextflow work directory inside output directory
    # This ensures work directory is in a writable location
    nextflow_work_dir = output_path / 'work'
    nextflow_work_dir.mkdir(parents=True, exist_ok=True)
    env['NXF_WORK'] = str(nextflow_work_dir)
    logger.info(f"Setting Nextflow work directory: {nextflow_work_dir}")
    
    # Set Nextflow temp directory
    nextflow_temp_dir = output_path / '.nextflow' / 'tmp'
    nextflow_temp_dir.mkdir(parents=True, exist_ok=True)
    env['NXF_TEMP'] = str(nextflow_temp_dir)
    
    # Set matplotlib config directory for Docker containers
    matplotlib_dir = output_path / '.nextflow' / 'matplotlib'
    matplotlib_dir.mkdir(parents=True, exist_ok=True)
    env['MPLCONFIGDIR'] = str(matplotlib_dir)
    
    # Pull workflow first
    logger.info(f"Pulling epi2me workflow {workflow_version}...")
    pull_cmd = ['nextflow', 'pull', workflow_ref, '-r', workflow_version]
    pull_result = subprocess.run(pull_cmd, capture_output=True, text=True, env=env)
    if pull_result.returncode != 0:
        logger.warning(f"Failed to pull {workflow_version}: {pull_result.stderr}")
    
    # Change to output directory before running Nextflow
    # This ensures Nextflow creates work directory in the correct location
    # Convert paths to absolute before changing directory
    output_path_abs = output_path.resolve()
    fast_pass_path_abs = fast_pass_path.resolve()
    samplesheet_file_abs = Path(samplesheet_file).resolve()
    
    original_cwd = os.getcwd()
    try:
        os.chdir(str(output_path_abs))
        
        # Build command matching user's successful test command
        # Use absolute paths to avoid issues after changing directory
        cmd = [
            'nextflow', 'run',
            workflow_ref,
            '-r', workflow_version,  # Use v1.8.3 (latest stable)
            '--fastq', str(fast_pass_path_abs),  # Parent directory containing sample subdirectories
            '--sample_sheet', str(samplesheet_file_abs),  # CSV mapping barcodes to aliases
            '--out_dir', str(output_path_abs),  # Note: --out_dir (not --outdir) per workflow help output
            '--approx_size', str(config['assembly']['approx_size']),
            '--assm_coverage', str(config['assembly']['coverage']),  # Note: parameter is assm_coverage, not coverage
            '--assembly_tool', config['assembly']['assembly_tool'],
            '-profile', profile,  # Use 'standard' profile (requires Docker for processes)
            '-work-dir', str(nextflow_work_dir),  # Explicitly set work directory
            '-resume'  # Allow resume if interrupted
        ]
        
        # Add primers if specified in config (optional)
        if 'primers' in config.get('assembly', {}) and config['assembly'].get('primers'):
            cmd.extend(['--primers', str(config['assembly']['primers'])])
        
        logger.info("Running epi2me wf-clone-validation workflow...")
        logger.info(f"  Samplesheet: {samplesheet_file_abs}")
        logger.info(f"  Output directory: {output_path_abs}")
        logger.info(f"  Fastq directory: {fast_pass_path_abs}")
        logger.info(f"  Profile: {profile}")
        logger.info(f"  Nextflow version: {env.get('NXF_VER', 'default')}")
        logger.info(f"  Work directory: {nextflow_work_dir}")
        logger.info(f"  Note: Running inside Docker - ensure Docker socket is mounted for -profile standard")
        logger.debug(f"Command: {' '.join(cmd)}")
        
        # Run Nextflow workflow with NXF_VER environment variable
        # Always capture output to get error details
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env  # Pass environment with NXF_VER=23.10.0
        )
        
        if result.returncode != 0:
            logger.error("epi2me workflow failed")
            if result.stderr:
                logger.error(f"Error output:\n{result.stderr}")
            if result.stdout:
                # Log last 50 lines of stdout for debugging
                stdout_lines = result.stdout.split('\n')
                logger.error(f"Nextflow output (last 50 lines):\n" + '\n'.join(stdout_lines[-50:]))
            raise RuntimeError("epi2me workflow failed")
        else:
            # Log success output if verbose
            if verbose and result.stdout:
                logger.debug(f"Nextflow output:\n{result.stdout}")
        
        logger.info("✓ Completed epi2me workflow")
        return str(output_path)
    finally:
        # Restore original working directory
        os.chdir(original_cwd)

def run_epi2me_workflow(config_file, input_dir, output_dir, verbose=False):
    """Run epi2me workflow for all samples."""
    logger = setup_logging(output_dir, verbose)
    
    logger.info("=" * 80)
    logger.info("Step 1: Running epi2me wf-clone-validation Workflow")
    logger.info("=" * 80)
    
    # Load config
    config = load_config(config_file)
    
    # Find fast_pass directory
    input_path = Path(input_dir)
    fast_pass = input_path / 'fast_pass'
    if not fast_pass.exists():
        fast_pass = input_path
    
    if not fast_pass.exists():
        raise FileNotFoundError(f"fast_pass directory not found: {fast_pass}")
    
    # Create output directory
    output_path = Path(output_dir) / '01.assembly'
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create work directory for barcode directories (in case input is read-only)
    # This will contain the processed fastq files with barcode naming
    work_dir = output_path / 'fastq_processed'
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate samplesheet
    # Use work_dir for creating barcode directories (allows read-only input)
    samplesheet_file = output_path / 'samplesheet.csv'
    logger.info("Generating samplesheet...")
    logger.info(f"Using work directory for barcode directories: {work_dir}")
    generate_samplesheet(str(fast_pass), str(samplesheet_file), work_dir=str(work_dir), logger=logger)
    
    # Run epi2me workflow with samplesheet
    # Use work_dir as fast_pass_dir if it contains barcode directories, otherwise use original fast_pass
    # Check if work_dir has barcode directories
    barcode_dirs = list(work_dir.glob('barcode*'))
    if barcode_dirs:
        # Use work_dir as the fastq directory for Nextflow
        fastq_dir_for_nextflow = str(work_dir)
        logger.info(f"Using processed fastq directory: {fastq_dir_for_nextflow}")
    else:
        # No barcode directories in work_dir, use original fast_pass
        fastq_dir_for_nextflow = str(fast_pass)
        logger.info(f"Using original fast_pass directory: {fastq_dir_for_nextflow}")
    
    try:
        assembly_output = run_epi2me_workflow_batch(
            fast_pass_dir=fastq_dir_for_nextflow,
            samplesheet_file=str(samplesheet_file),
            output_dir=str(output_path),
            config=config,
            verbose=verbose,
            logger=logger
        )
        
        logger.info("\n" + "=" * 80)
        logger.info("epi2me workflow completed successfully!")
        logger.info("=" * 80)
        
        return assembly_output
    except Exception as e:
        logger.error(f"epi2me workflow failed: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Step 1: Run epi2me workflow')
    parser.add_argument('--config', '-c', required=True, help='Config YAML file')
    parser.add_argument('--input', '-i', required=True, help='Input directory')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    try:
        output_dir = run_epi2me_workflow(
            config_file=args.config,
            input_dir=args.input,
            output_dir=args.output,
            verbose=args.verbose
        )
        print(f"Assembly results: {output_dir}")
        return 0
    except Exception as e:
        logging.error(f"Workflow failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

