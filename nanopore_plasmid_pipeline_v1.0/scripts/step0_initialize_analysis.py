#!/usr/bin/env python3
"""
Step 0: Initialize analysis and generate configuration.

This script:
- Validates input data structure
- Checks software dependencies
- Generates config.yaml
- Creates output directory structure
"""

import argparse
import logging
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)

def setup_logging(output_dir, verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory
    logs_dir = Path(output_dir) / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / 'step0_initialize.log'
    
    # Get or create logger for this step
    logger = logging.getLogger('step0')
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

def check_dependency(cmd, name):
    """Check if a command-line tool is available."""
    logger = logging.getLogger('step0')
    if shutil.which(cmd):
        version = subprocess.run([cmd, '--version'], capture_output=True, text=True)
        logger.info(f"  ✓ {name}: {version.stdout.split()[0] if version.returncode == 0 else 'installed'}")
        return True
    else:
        logger.warning(f"  ✗ {name}: not found")
        return False

def check_dependencies():
    """Check all required dependencies."""
    logger = logging.getLogger('step0')
    logger.info("Checking dependencies...")
    deps = {
        'nextflow': 'Nextflow',
        'python3': 'Python 3',
        'stack': 'Haskell Stack'
    }
    
    all_ok = True
    for cmd, name in deps.items():
        if not check_dependency(cmd, name):
            all_ok = False
    
    # Check Python packages
    try:
        import Bio
        logger.info("  ✓ BioPython: installed")
    except ImportError:
        logger.warning("  ✗ BioPython: not installed")
        all_ok = False
    
    try:
        import reportlab
        logger.info("  ✓ ReportLab: installed")
    except ImportError:
        logger.warning("  ✗ ReportLab: not installed")
        all_ok = False
    
    return all_ok

def validate_input_structure(input_dir):
    """Validate input directory structure."""
    logger = logging.getLogger('step0')
    input_path = Path(input_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    
    # Check for fast_pass subdirectory or direct sample folders
    fast_pass = input_path / 'fast_pass'
    if fast_pass.exists():
        sample_dirs = [d for d in fast_pass.iterdir() if d.is_dir()]
    else:
        # Assume input_dir contains sample subdirectories directly
        sample_dirs = [d for d in input_path.iterdir() if d.is_dir()]
    
    if not sample_dirs:
        raise ValueError(f"No sample subdirectories found in {input_dir}")
    
    logger.info(f"Found {len(sample_dirs)} sample directories:")
    for sample_dir in sample_dirs[:5]:  # Show first 5
        logger.info(f"  - {sample_dir.name}")
    if len(sample_dirs) > 5:
        logger.info(f"  ... and {len(sample_dirs) - 5} more")
    
    return sample_dirs

def generate_config(input_dir, output_dir, project_id=None, approx_size=5000, 
                   coverage=50, fragment_size=2000):
    """Generate config.yaml file."""
    if project_id is None:
        project_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    config = {
        'project': {
            'project_id': project_id,
            'input_dir': str(input_dir),
            'output_dir': str(output_dir),
            'created_at': datetime.now().isoformat()
        },
        'assembly': {
            'tool': 'epi2me_wf_clone_validation',
            'workflow_version': 'latest',
            'approx_size': approx_size,
            'coverage': coverage,
            'assembly_tool': 'flye'
        },
        'fragmentation': {
            'fragment_size': fragment_size,
            'tool': 'split_plasmid_fasta.py'
        },
        'ab1_generation': {
            'tool': 'hyraxAbif',
            'executable': '/opt/hyraxAbif/hyraxAbif-exe'
        },
        'reporting': {
            'tool': 'generate_complete_reports.py',
            'format': 'pdf',
            'include_coverage': True,
            'include_length_dist': True,
            'generate_json': True,
            'generate_html': False  # User requested: no HTML reports
        }
    }
    
    logger = logging.getLogger('step0')
    config_file = Path(output_dir) / 'config.yaml'
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    logger.info(f"Generated config file: {config_file}")
    return str(config_file)

def create_output_structure(output_dir):
    """Create output directory structure."""
    logger = logging.getLogger('step0')
    output_path = Path(output_dir)
    
    dirs = [
        '01.assembly',
        '02.fragments',
        '03.ab1_files',
        '04.reports',
        '05.summary',
        'logs'
    ]
    
    for dir_name in dirs:
        (output_path / dir_name).mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Created output directory structure: {output_dir}")

def initialize_analysis(input_dir, output_dir, project_id=None, approx_size=5000,
                      coverage=50, fragment_size=2000, verbose=False):
    """Main initialization function."""
    logger = setup_logging(output_dir, verbose)
    
    logger.info("=" * 80)
    logger.info("Step 0: Initializing Analysis")
    logger.info("=" * 80)
    
    # Check dependencies
    if not check_dependencies():
        logger.warning("Some dependencies are missing. Pipeline may fail.")
    
    # Validate input structure
    logger.info("\nValidating input structure...")
    sample_dirs = validate_input_structure(input_dir)
    
    # Create output structure
    logger.info("\nCreating output directory structure...")
    create_output_structure(output_dir)
    
    # Generate config
    logger.info("\nGenerating configuration file...")
    config_file = generate_config(
        input_dir=input_dir,
        output_dir=output_dir,
        project_id=project_id,
        approx_size=approx_size,
        coverage=coverage,
        fragment_size=fragment_size
    )
    
    logger.info("\n" + "=" * 80)
    logger.info("Initialization complete!")
    logger.info("=" * 80)
    
    return config_file

def main():
    parser = argparse.ArgumentParser(description='Step 0: Initialize analysis')
    parser.add_argument('--input', '-i', required=True, help='Input directory')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('--project-id', help='Project ID')
    parser.add_argument('--approx-size', type=int, default=5000, help='Approximate plasmid size')
    parser.add_argument('--coverage', type=int, default=50, help='Target coverage')
    parser.add_argument('--fragment-size', type=int, default=2000, help='Fragment size')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    try:
        config_file = initialize_analysis(
            input_dir=args.input,
            output_dir=args.output,
            project_id=args.project_id,
            approx_size=args.approx_size,
            coverage=args.coverage,
            fragment_size=args.fragment_size,
            verbose=args.verbose
        )
        print(f"Config file: {config_file}")
        return 0
    except Exception as e:
        logging.error(f"Initialization failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

