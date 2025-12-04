import os
import logging
import subprocess
from pathlib import Path
from Bio import SeqIO

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

def run_prokka_annotation(polished_assembly, annotated_dir, threads):
    """
    Annotates the polished assembly using Prokka.
    It handles multi-FASTA files by annotating each contig separately.

    Args:
        polished_assembly (str): Path to the polished assembly FASTA file.
        annotated_dir (str): Directory to save annotation results.
        threads (int): Number of threads to use.

    Returns:
        dict: A dictionary where keys are contig IDs and values are paths to their annotation results (gff, gbk, faa).
    """
    logger.info(f"Starting Prokka annotation for {polished_assembly}")
    
    annotation_results = {}
    
    # Prokka works best on one contig at a time for plasmids.
    # We'll split the input fasta and run prokka on each contig.
    for record in SeqIO.parse(polished_assembly, "fasta"):
        contig_id = record.id
        logger.info(f"Annotating contig: {contig_id}")
        
        contig_dir = Path(annotated_dir) / contig_id
        contig_dir.mkdir(exist_ok=True)
        
        contig_file = contig_dir / f"{contig_id}.fasta"
        SeqIO.write(record, contig_file, "fasta")

        log_file = contig_dir / f"prokka_{contig_id}.log"
        
        command = [
            "prokka",
            "--outdir", str(contig_dir),
            "--prefix", contig_id,
            "--cpus", str(threads),
            "--kingdom", "Bacteria",
            "--plasmid",
            str(contig_file)
        ]

        run_command(command, log_file)

        gff_file = contig_dir / f"{contig_id}.gff"
        gbk_file = contig_dir / f"{contig_id}.gbk"
        faa_file = contig_dir / f"{contig_id}.faa"

        if gff_file.exists() and gbk_file.exists():
            annotation_results[contig_id] = {
                "gff": str(gff_file),
                "gbk": str(gbk_file),
                "faa": str(faa_file)
            }
            logger.info(f"Successfully annotated {contig_id}")
        else:
            logger.error(f"Annotation failed for {contig_id}. Output files not found.")

    if not annotation_results:
        logger.error("Prokka annotation failed for all contigs.")
        return None

    logger.info("Prokka annotation finished for all contigs.")
    return annotation_results
