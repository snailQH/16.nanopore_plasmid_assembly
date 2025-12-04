import os
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def run_command(command, log_file):
    """A helper function to run a command and log its output."""
    logger.info(f"Running command: {' '.join(command)}")
    try:
        with open(log_file, 'w') as f:
            process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT, text=True)
            process.communicate()
        if process.returncode != 0:
            logger.error(f"Command failed with exit code {process.returncode}. See log for details: {log_file}")
            raise subprocess.CalledProcessError(process.returncode, command)
        logger.info(f"Command completed successfully. Log file: {log_file}")
    except FileNotFoundError:
        logger.error(f"Error: The command '{command[0]}' was not found.")
        logger.error("Please ensure the tool is installed and in your PATH.")
        raise

def run_flye_assembly(cleaned_reads, assembly_dir, threads, genome_size):
    """
    Runs Flye assembler on the cleaned reads.

    Args:
        cleaned_reads (str): Path to the cleaned FASTQ file.
        assembly_dir (str): Directory to save assembly results.
        threads (int): Number of threads to use.
        genome_size (str, optional): Estimated genome size (e.g., '5k', '2.8m').

    Returns:
        str: Path to the final assembly FASTA file.
    """
    logger.info("Starting Flye assembly...")
    
    flye_out_dir = Path(assembly_dir)
    log_file = flye_out_dir.parent / "flye.log"

    command = [
        "flye",
        "--nano-raw", str(cleaned_reads),
        "--out-dir", str(flye_out_dir),
        "--threads", str(threads),
        "--plasmids"  # Important for plasmid assembly
    ]

    if genome_size:
        command.extend(["--genome-size", genome_size])

    run_command(command, log_file)
    
    assembly_result_path = flye_out_dir / "assembly.fasta"
    
    if not assembly_result_path.exists():
        logger.error(f"Flye assembly failed, output file not found: {assembly_result_path}")
        raise FileNotFoundError(f"Flye assembly failed, output file not found: {assembly_result_path}")

    logger.info(f"Flye assembly finished. Assembly file: {assembly_result_path}")
    return str(assembly_result_path)
