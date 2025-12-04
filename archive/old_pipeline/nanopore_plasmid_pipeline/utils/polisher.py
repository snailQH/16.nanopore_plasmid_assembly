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

def run_medaka_polish(draft_assembly, reads_fastq, output_dir, threads, model):
    """
    Polishes a draft assembly using Medaka.

    Args:
        draft_assembly (str): Path to the draft assembly FASTA file.
        reads_fastq (str): Path to the basecalled reads in FASTQ format.
        output_dir (str): Directory to save polished assembly results.
        threads (int): Number of threads to use.
        model (str): The Medaka consensus model to use.

    Returns:
        str: Path to the polished consensus FASTA file.
    """
    logger.info(f"Starting Medaka polishing for {draft_assembly} using model {model}")
    
    medaka_out_dir = Path(output_dir)
    medaka_out_dir.mkdir(exist_ok=True)
    log_file = medaka_out_dir.parent / "medaka.log"

    command = [
        "medaka_consensus",
        "-i", str(reads_fastq),
        "-d", str(draft_assembly),
        "-o", str(medaka_out_dir),
        "-t", str(threads),
        "-m", model
    ]

    run_command(command, log_file)

    polished_fasta = medaka_out_dir / "consensus.fasta"

    if not polished_fasta.exists():
        logger.error(f"Medaka polishing failed, output file not found: {polished_fasta}")
        raise FileNotFoundError(f"Medaka polishing failed, output file not found: {polished_fasta}")

    logger.info(f"Medaka polishing finished. Polished assembly: {polished_fasta}")
    return str(polished_fasta)
