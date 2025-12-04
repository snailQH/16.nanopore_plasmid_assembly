import os
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

def run_command(command, log_file, shell=False):
    """A helper function to run a command and log its output."""
    logger.info(f"Running command: {' '.join(command)}")
    try:
        # Using a file for stdout/stderr
        with open(log_file, 'w') as f:
            if shell:
                # For commands with pipes
                process = subprocess.Popen(" ".join(command), stdout=f, stderr=subprocess.STDOUT, text=True, shell=True)
            else:
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

def validate_assembly(polished_assembly, cleaned_reads, validation_dir, threads):
    """
    Validates the assembly by aligning reads back to it and generating stats.

    Args:
        polished_assembly (str): Path to the polished assembly FASTA.
        cleaned_reads (str): Path to the cleaned reads FASTQ.
        validation_dir (str): Directory to save validation results.
        threads (int): Number of threads.

    Returns:
        dict: A dictionary of paths to key validation files.
    """
    logger.info(f"Starting assembly validation for {polished_assembly}")
    val_dir = Path(validation_dir)
    val_dir.mkdir(exist_ok=True)

    bam_file = val_dir / "alignment.bam"
    sorted_bam_file = val_dir / "alignment.sorted.bam"
    coverage_file = val_dir / "coverage.tsv"
    flagstat_file = val_dir / "flagstat.txt"
    log_file = val_dir / "validation.log"

    # 1. Align reads with minimap2 and pipe to samtools for BAM conversion
    logger.info("Aligning reads to assembly with minimap2...")
    map_cmd = [
        "minimap2", "-ax", "map-ont", "-t", str(threads),
        str(polished_assembly), str(cleaned_reads),
        "|", "samtools", "view", "-bS", "-",
        ">", str(bam_file)
    ]
    run_command(map_cmd, log_file, shell=True)
    
    # 2. Sort the BAM file
    logger.info("Sorting BAM file...")
    sort_cmd = ["samtools", "sort", "-@", str(threads), "-o", str(sorted_bam_file), str(bam_file)]
    run_command(sort_cmd, log_file)
    
    # 3. Index the sorted BAM file
    logger.info("Indexing sorted BAM file...")
    index_cmd = ["samtools", "index", str(sorted_bam_file)]
    run_command(index_cmd, log_file)
    
    # 4. Calculate per-base coverage
    logger.info("Calculating coverage...")
    cov_cmd = ["samtools", "depth", "-a", str(sorted_bam_file), ">", str(coverage_file)]
    run_command(cov_cmd, log_file, shell=True)

    # 5. Generate alignment stats
    logger.info("Generating flagstat...")
    stat_cmd = ["samtools", "flagstat", str(sorted_bam_file), ">", str(flagstat_file)]
    run_command(stat_cmd, log_file, shell=True)
    
    # Clean up intermediate file
    os.remove(bam_file)

    validation_results = {
        "sorted_bam": str(sorted_bam_file),
        "bam_index": f"{sorted_bam_file}.bai",
        "coverage_report": str(coverage_file),
        "flagstat_report": str(flagstat_file)
    }

    logger.info("Assembly validation finished.")
    return validation_results
