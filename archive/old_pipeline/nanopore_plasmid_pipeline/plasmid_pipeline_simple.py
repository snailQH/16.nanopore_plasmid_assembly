#!/usr/bin/env python3
"""
Simplified Nanopore Plasmid Assembly Pipeline
A version that works with available tools.
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
import gzip

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
        "04_validation",
        "05_visualization",
        "06_reports"
    ]
    
    for subdir in subdirs:
        os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)
    
    return output_dir

def check_dependencies():
    """Check for available tools"""
    required_tools = ['minimap2', 'samtools', 'bedtools']
    missing_tools = []
    
    for tool in required_tools:
        if not shutil.which(tool):
            missing_tools.append(tool)
        else:
            logging.info(f"✓ {tool} found")
    
    return missing_tools

def clean_reads(input_file, output_dir, min_length=1000):
    """Clean and filter reads"""
    logging.info(f"Cleaning reads from {input_file}")
    
    cleaned_dir = os.path.join(output_dir, "01_cleaned_reads")
    os.makedirs(cleaned_dir, exist_ok=True)
    
    base_name = Path(input_file).stem.replace('.fastq', '').replace('.fq', '')
    output_file = os.path.join(cleaned_dir, f"{base_name}_cleaned.fastq.gz")
    
    with gzip.open(input_file, 'rt') as f_in, gzip.open(output_file, 'wt') as f_out:
        reads_written = 0
        total_reads = 0
        
        while True:
            header = f_in.readline()
            if not header:
                break
            
            seq = f_in.readline()
            plus = f_in.readline()
            qual = f_in.readline()
            
            total_reads += 1
            
            if len(seq.strip()) >= min_length:
                f_out.write(header)
                f_out.write(seq)
                f_out.write(plus)
                f_out.write(qual)
                reads_written += 1
    
    logging.info(f"Read cleaning completed: {reads_written}/{total_reads} reads kept")
    return output_file

def run_minimap2_assembly(reads_file, output_dir, threads=4):
    """Run minimap2 for assembly-like analysis"""
    logging.info("Running minimap2 analysis")
    
    assembly_dir = os.path.join(output_dir, "02_assembly")
    os.makedirs(assembly_dir, exist_ok=True)
    
    # For now, we'll just create a simple analysis since we don't have Flye
    # We'll use minimap2 to find overlaps and create a basic assembly
    
    # First, let's create a simple consensus from the reads
    consensus_file = os.path.join(assembly_dir, "consensus.fasta")
    
    # For demonstration, we'll create a simple consensus
    # In a real scenario, you'd want to use a proper assembler
    logging.info("Creating simple consensus (placeholder for proper assembly)")
    
    # Read the first few reads to create a simple consensus
    sequences = []
    with gzip.open(reads_file, 'rt') as f:
        for i, line in enumerate(f):
            if i % 4 == 1:  # Sequence line
                sequences.append(line.strip())
                if len(sequences) >= 100:  # Limit for demo
                    break
    
    if sequences:
        # Create a simple consensus (this is just a placeholder)
        consensus_seq = sequences[0][:1000]  # Take first 1000 bp as consensus
        
        with open(consensus_file, 'w') as f:
            f.write(f">consensus_assembly\n{consensus_seq}\n")
        
        logging.info(f"Simple consensus created: {consensus_file}")
        return consensus_file
    else:
        logging.error("No sequences found in input file")
        return None

def run_medaka_polish(assembly_file, reads_file, output_dir, threads=4):
    """Run Medaka polishing if available"""
    logging.info("Attempting Medaka polishing")
    
    polished_dir = os.path.join(output_dir, "03_polished")
    os.makedirs(polished_dir, exist_ok=True)
    
    # Check if medaka_consensus is available
    if shutil.which('medaka_consensus'):
        try:
            # Create BAM file first
            bam_file = os.path.join(polished_dir, "reads_to_assembly.bam")
            
            # Run minimap2 alignment
            minimap2_cmd = [
                'minimap2', '-ax', 'map-ont', '-t', str(threads),
                assembly_file, reads_file
            ]
            
            samtools_cmd = ['samtools', 'sort', '-o', bam_file]
            
            minimap2_process = subprocess.Popen(minimap2_cmd, stdout=subprocess.PIPE)
            subprocess.run(samtools_cmd, stdin=minimap2_process.stdout, check=True)
            
            # Index BAM
            subprocess.run(['samtools', 'index', bam_file], check=True)
            
            # Run Medaka
            medaka_cmd = [
                'medaka_consensus', '-i', bam_file, '-d', assembly_file,
                '-o', polished_dir, '-t', str(threads)
            ]
            
            subprocess.run(medaka_cmd, check=True)
            
            polished_file = os.path.join(polished_dir, "consensus.fasta")
            if os.path.exists(polished_file):
                logging.info(f"Medaka polishing completed: {polished_file}")
                return polished_file
            
        except subprocess.CalledProcessError as e:
            logging.warning(f"Medaka polishing failed: {e}")
    
    # If Medaka is not available or failed, copy the original assembly
    logging.info("Medaka not available, using original assembly")
    polished_file = os.path.join(polished_dir, "consensus.fasta")
    shutil.copy2(assembly_file, polished_file)
    return polished_file

def validate_assembly(assembly_file, reads_file, output_dir, threads=4):
    """Validate assembly by mapping reads back"""
    logging.info("Validating assembly")
    
    validation_dir = os.path.join(output_dir, "04_validation")
    os.makedirs(validation_dir, exist_ok=True)
    
    # Align reads to assembly
    bam_file = os.path.join(validation_dir, "validation_alignment.bam")
    
    try:
        # Run minimap2 alignment
        minimap2_cmd = [
            'minimap2', '-ax', 'map-ont', '-t', str(threads),
            assembly_file, reads_file
        ]
        
        samtools_cmd = ['samtools', 'sort', '-o', bam_file]
        
        minimap2_process = subprocess.Popen(minimap2_cmd, stdout=subprocess.PIPE)
        subprocess.run(samtools_cmd, stdin=minimap2_process.stdout, check=True)
        
        # Index BAM
        subprocess.run(['samtools', 'index', bam_file], check=True)
        
        # Get alignment statistics
        flagstat_cmd = ['samtools', 'flagstat', bam_file]
        result = subprocess.run(flagstat_cmd, capture_output=True, text=True, check=True)
        
        logging.info("Alignment statistics:")
        logging.info(result.stdout)
        
        return {
            'bam_file': bam_file,
            'flagstat': result.stdout,
            'output_dir': validation_dir
        }
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Validation failed: {e}")
        return None

def create_visualizations(assembly_file, reads_file, validation_result, output_dir):
    """Create basic visualizations"""
    logging.info("Creating visualizations")
    
    viz_dir = os.path.join(output_dir, "05_visualization")
    os.makedirs(viz_dir, exist_ok=True)
    
    # Create read length distribution
    lengths = []
    with gzip.open(reads_file, 'rt') as f:
        for i, line in enumerate(f):
            if i % 4 == 1:  # Sequence line
                lengths.append(len(line.strip()))
    
    if lengths:
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        plt.hist(lengths, bins=50, alpha=0.7, edgecolor='black')
        plt.title('Read Length Distribution')
        plt.xlabel('Read Length (bp)')
        plt.ylabel('Frequency')
        plt.yscale('log')
        
        length_file = os.path.join(viz_dir, "read_length_distribution.png")
        plt.savefig(length_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"Read length plot created: {length_file}")
    
    return viz_dir

def generate_html_report(input_file, cleaned_reads, assembly_result, polished_result, 
                        validation_result, viz_result, report_dir, args):
    """Generate HTML report"""
    logging.info("Generating HTML report")
    
    os.makedirs(report_dir, exist_ok=True)
    
    # Simple HTML report
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Plasmid Assembly Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Nanopore Plasmid Assembly Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>Analysis Summary</h2>
        <p><strong>Input File:</strong> {os.path.basename(input_file)}</p>
        <p><strong>Cleaned Reads:</strong> {os.path.basename(cleaned_reads) if cleaned_reads else 'N/A'}</p>
        <p><strong>Expected Plasmids:</strong> {args.expected_plasmids}</p>
        <p><strong>Threads Used:</strong> {args.threads}</p>
    </div>
    
    <div class="section">
        <h2>Results</h2>
        <p><strong>Assembly:</strong> {assembly_result if assembly_result else 'N/A'}</p>
        <p><strong>Polished Assembly:</strong> {polished_result if polished_result else 'N/A'}</p>
        <p><strong>Validation:</strong> {'Completed' if validation_result else 'Failed'}</p>
    </div>
    
    <div class="section">
        <h2>Note</h2>
        <p>This is a simplified analysis. For full assembly capabilities, please install Flye, Prokka, and other bioinformatics tools.</p>
    </div>
</body>
</html>
"""
    
    report_file = os.path.join(report_dir, "plasmid_assembly_report.html")
    with open(report_file, 'w') as f:
        f.write(html_content)
    
    logging.info(f"HTML report generated: {report_file}")
    return report_file

def main():
    parser = argparse.ArgumentParser(description="Simplified Nanopore Plasmid Assembly Pipeline")
    parser.add_argument("--input", required=True, help="Input FASTQ file (gzipped)")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads")
    parser.add_argument("--expected-plasmids", type=int, default=1, help="Expected number of plasmids")
    parser.add_argument("--min-read-length", type=int, default=1000, help="Minimum read length")
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        sys.exit(1)
    
    # Create output directory structure
    output_dir = create_output_structure(args.output)
    
    # Setup logging
    logger = setup_logging(output_dir)
    logger.info("Starting Simplified Nanopore Plasmid Assembly Pipeline")
    logger.info(f"Input file: {args.input}")
    logger.info(f"Output directory: {args.output}")
    
    try:
        # Check dependencies
        logger.info("Checking dependencies...")
        missing_tools = check_dependencies()
        if missing_tools:
            logger.warning(f"Missing tools: {', '.join(missing_tools)}")
            logger.warning("Pipeline will run with limited functionality")
        
        # Clean reads
        logger.info("Cleaning reads...")
        cleaned_reads = clean_reads(args.input, output_dir, args.min_read_length)
        
        # Assembly (simplified)
        logger.info("Running assembly analysis...")
        assembly_result = run_minimap2_assembly(cleaned_reads, output_dir, args.threads)
        
        # Polishing
        logger.info("Running polishing...")
        polished_result = run_medaka_polish(assembly_result, cleaned_reads, output_dir, args.threads)
        
        # Validation
        logger.info("Validating assembly...")
        validation_result = validate_assembly(polished_result, cleaned_reads, output_dir, args.threads)
        
        # Visualizations
        logger.info("Creating visualizations...")
        viz_result = create_visualizations(polished_result, cleaned_reads, validation_result, output_dir)
        
        # Generate report
        logger.info("Generating HTML report...")
        report_file = generate_html_report(
            args.input, cleaned_reads, assembly_result, polished_result,
            validation_result, viz_result, os.path.join(output_dir, "06_reports"), args
        )
        
        logger.info("Pipeline completed successfully!")
        logger.info(f"Results available in: {args.output}")
        logger.info(f"View the report at: {report_file}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 