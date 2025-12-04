#!/usr/bin/env python3
"""
Step 1: Run epi2me wf-clone-validation workflow (Host Execution Version).

This script runs the epi2me workflow on the HOST machine (not inside Docker),
allowing Nextflow to use Docker containers for processes (medaka, flye, etc.).

This is a wrapper that can be called from inside Docker to execute Nextflow
on the host system.
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

def generate_samplesheet(fast_pass_dir, output_file, logger=None):
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
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Failed to generate samplesheet: {result.stderr}")
        raise RuntimeError("Samplesheet generation failed")
    
    return output_file

def run_epi2me_workflow_on_host(fast_pass_dir, samplesheet_file, output_dir, config, verbose=False, logger=None):
    """
    Run epi2me workflow on HOST machine using Docker container.
    
    This function executes Nextflow in a separate Docker container that has
    access to the host's Docker socket, allowing Nextflow to run processes
    in Docker containers (medaka, flye, etc.).
    """
    if logger is None:
        logger = logging.getLogger('step1')
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    fast_pass_path = Path(fast_pass_dir)
    
    # Use official workflow reference
    workflow_ref = 'epi2me-labs/wf-clone-validation'
    workflow_version = 'v1.8.3'
    
    # Set Nextflow version environment variable
    env = os.environ.copy()
    env['NXF_VER'] = '23.10.0'
    
    # Build Docker command to run Nextflow on host
    # This container will use host's Docker to run process containers
    # Use absolute paths for volume mounts
    fast_pass_abs = str(fast_pass_path.absolute())
    output_abs = str(output_path.absolute())
    samplesheet_abs = str(Path(samplesheet_file).absolute())
    samplesheet_dir_abs = str(Path(samplesheet_file).absolute().parent)
    
    docker_cmd = [
        'docker', 'run', '--rm',
        '-v', f'{fast_pass_abs}:/data/input/fast_pass:ro',
        '-v', f'{output_abs}:/data/output',
        '-v', f'{samplesheet_dir_abs}:/data/samplesheet:ro',
        '-v', '/var/run/docker.sock:/var/run/docker.sock',  # Mount Docker socket
        '-e', 'NXF_VER=23.10.0',
        '--workdir', '/data/output',
        'nextflowio/nextflow:23.10.0',  # Official Nextflow Docker image
        'nextflow', 'run',
        workflow_ref,
        '-r', workflow_version,
        '--fastq', '/data/input/fast_pass',
        '--sample_sheet', f'/data/samplesheet/{Path(samplesheet_file).name}',
        '--out_dir', '/data/output',
        '--approx_size', str(config['assembly']['approx_size']),
        '--assm_coverage', str(config['assembly']['coverage']),
        '--assembly_tool', config['assembly']['assembly_tool'],
        '-profile', 'standard',
        '-resume'
    ]
    
    # Add primers if specified
    if 'primers' in config.get('assembly', {}) and config['assembly'].get('primers'):
        primers_path = Path(config['assembly']['primers']).absolute()
        docker_cmd.insert(-10, '-v')  # Insert before --workdir
        docker_cmd.insert(-10, f'{primers_path}:/data/primers/{primers_path.name}:ro')
        docker_cmd.insert(-1, '--primers')
        docker_cmd.insert(-1, f'/data/primers/{primers_path.name}')
    
    logger.info("Running epi2me wf-clone-validation workflow on HOST...")
    logger.info(f"  Samplesheet: {samplesheet_file}")
    logger.info(f"  Output directory: {output_path}")
    logger.info(f"  Nextflow version: 23.10.0")
    logger.info(f"  Using separate Docker container for Nextflow execution")
    logger.debug(f"Command: {' '.join(docker_cmd)}")
    
    # Run Docker command
    result = subprocess.run(
        docker_cmd,
        capture_output=True,
        text=True,
        env=env
    )
    
    if result.returncode != 0:
        logger.error("epi2me workflow failed")
        if result.stderr:
            logger.error(f"Error output:\n{result.stderr}")
        if result.stdout:
            stdout_lines = result.stdout.split('\n')
            logger.error(f"Nextflow output (last 50 lines):\n" + '\n'.join(stdout_lines[-50:]))
        raise RuntimeError("epi2me workflow failed")
    else:
        if verbose and result.stdout:
            logger.debug(f"Nextflow output:\n{result.stdout}")
    
    logger.info("✓ Completed epi2me workflow")
    return str(output_path)

def run_epi2me_workflow(config_file, input_dir, output_dir, verbose=False):
    """Run epi2me workflow for all samples."""
    logger = setup_logging(output_dir, verbose)
    
    logger.info("=" * 80)
    logger.info("Step 1: Running epi2me wf-clone-validation Workflow (Host Execution)")
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
    
    # Generate samplesheet
    samplesheet_file = output_path / 'samplesheet.csv'
    logger.info("Generating samplesheet...")
    generate_samplesheet(str(fast_pass), str(samplesheet_file), logger=logger)
    
    # Run epi2me workflow on host
    try:
        assembly_output = run_epi2me_workflow_on_host(
            fast_pass_dir=str(fast_pass),
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
    parser = argparse.ArgumentParser(description='Step 1: Run epi2me workflow (Host Execution)')
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

