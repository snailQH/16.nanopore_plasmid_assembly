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

def clean_reads(input_fastq, output_dir, min_length, threads):
    """
    Cleans raw FASTQ reads using chopper.

    Args:
        input_fastq (str): Path to the input FASTQ file.
        output_dir (str): Directory to save cleaned reads.
        min_length (int): Minimum read length to keep.
        threads (int): Number of threads to use.

    Returns:
        str: Path to the cleaned FASTQ file.
    """
    logger.info(f"Starting read cleaning for {input_fastq}")
    
    cleaned_reads_dir = Path(output_dir) / "01_cleaned_reads"
    cleaned_reads_dir.mkdir(exist_ok=True)
    
    output_fastq = cleaned_reads_dir / f"{Path(input_fastq).stem}.cleaned.fastq.gz"
    log_file = cleaned_reads_dir / "chopper.log"

    # Using default quality filtering of Q > 7. Can be parameterized if needed.
    command = [
        "chopper",
        "-i", str(input_fastq),
        "-o", str(output_fastq),
        "-l", str(min_length),
        "-t", str(threads),
        "-q", "7"
    ]

    run_command(command, log_file)
    
    logger.info(f"Read cleaning finished. Cleaned reads are in {output_fastq}")
    return str(output_fastq)
