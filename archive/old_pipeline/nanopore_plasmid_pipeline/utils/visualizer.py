import os
import logging
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from Bio import SeqIO
from dna_features_viewer import GraphicRecord
import pysam

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

def plot_coverage(coverage_file, output_dir, polished_assembly):
    """Plots coverage per contig."""
    logger.info(f"Plotting coverage from {coverage_file}")
    coverage_plots = {}
    try:
        df = pd.read_csv(coverage_file, sep='\\t', header=None, names=['contig', 'position', 'depth'])
        contigs = df['contig'].unique()

        for contig in contigs:
            contig_df = df[df['contig'] == contig]
            plt.figure(figsize=(15, 5))
            plt.fill_between(contig_df['position'], contig_df['depth'], color='skyblue')
            plt.title(f'Coverage for {contig}')
            plt.xlabel('Position')
            plt.ylabel('Depth')
            plt.tight_layout()
            plot_path = Path(output_dir) / f"coverage_{contig}.png"
            plt.savefig(plot_path)
            plt.close()
            coverage_plots[contig] = str(plot_path)
            logger.info(f"Saved coverage plot for {contig} to {plot_path}")
            
    except Exception as e:
        logger.error(f"Failed to plot coverage: {e}")
    return coverage_plots

def plot_virtual_gel(polished_assembly, output_dir):
    """Creates a virtual gel plot from a FASTA file."""
    logger.info("Creating virtual gel plot...")
    try:
        sizes = [len(rec) for rec in SeqIO.parse(polished_assembly, "fasta")]
        names = [rec.id for rec in SeqIO.parse(polished_assembly, "fasta")]

        fig, ax = plt.subplots(figsize=(4, 6))
        ax.set_title('Virtual Gel')
        ax.set_ylabel('Fragment Size (bp)')
        ax.set_xticks([])
        ax.set_yscale('log')
        
        for i, (name, size) in enumerate(zip(names, sizes)):
            ax.plot([i + 1], [size], 's', markersize=10, label=f"{name} ({size} bp)")
            ax.text(i + 1.1, size, f"{size} bp")

        ax.set_xlim(0, len(sizes) + 1)
        ax.legend()
        plt.tight_layout()
        gel_plot_path = Path(output_dir) / "virtual_gel.png"
        plt.savefig(gel_plot_path)
        plt.close()
        logger.info(f"Saved virtual gel plot to {gel_plot_path}")
        return str(gel_plot_path)
    except Exception as e:
        logger.error(f"Failed to create virtual gel: {e}")
        return None

def plot_alignment_pileup(bam_file, fasta_file, output_dir):
    """Generates a pileup image for each contig using pysam."""
    logger.info("Generating alignment pileup images...")
    pileup_plots = {}
    try:
        samfile = pysam.AlignmentFile(bam_file, "rb")
        for rec in SeqIO.parse(fasta_file, "fasta"):
            contig_id = rec.id
            start = 0
            end = len(rec.seq)

            # Generate pileup
            pileup = samfile.pileup(contig_id, start, end, truncate=True)
            
            # Simple visualization of coverage depth
            positions = []
            depths = []
            for pileupcolumn in pileup:
                positions.append(pileupcolumn.pos)
                depths.append(pileupcolumn.n)
            
            if not positions:
                logger.warning(f"No alignment data for contig {contig_id} to generate pileup plot.")
                continue

            plt.figure(figsize=(15, 5))
            plt.fill_between(positions, depths, color='lightgreen')
            plt.title(f'Alignment Pileup for {contig_id}')
            plt.xlabel('Position')
            plt.ylabel('Read Depth')
            plt.xlim(start, end)
            plt.tight_layout()
            
            plot_path = Path(output_dir) / f"pileup_{contig_id}.png"
            plt.savefig(plot_path)
            plt.close()
            pileup_plots[contig_id] = str(plot_path)
            logger.info(f"Saved pileup plot for {contig_id} to {plot_path}")
            
        samfile.close()
    except Exception as e:
        logger.error(f"Failed to generate pileup plots: {e}")
    return pileup_plots

def create_visualizations(polished_assembly, cleaned_reads, annotation_results, validation_results, viz_dir, threads):
    """
    Generates all requested visualizations for the pipeline.
    """
    logger.info("Starting visualization step...")
    viz_dir = Path(viz_dir)
    viz_dir.mkdir(exist_ok=True)
    log_file = viz_dir / "visualization.log"
    
    viz_outputs = {}

    # 1. NanoPlot for read length stats
    logger.info("Running NanoPlot...")
    nanoplot_dir = viz_dir / "nanoplot"
    nanoplot_cmd = [
        "NanoPlot",
        "--fastq", cleaned_reads,
        "-o", str(nanoplot_dir),
        "--threads", str(threads),
        "--loglength"
    ]
    try:
        run_command(nanoplot_cmd, log_file)
        viz_outputs["nanoplot_report"] = str(nanoplot_dir / "NanoPlot-report.html")
        viz_outputs["read_length_plot"] = str(nanoplot_dir / "Log-transformed_read_length_histogram.png")
    except Exception as e:
        logger.error(f"NanoPlot failed: {e}")

    # 2. Coverage plot
    if validation_results and "coverage_report" in validation_results:
        coverage_plots = plot_coverage(validation_results["coverage_report"], viz_dir, polished_assembly)
        viz_outputs["coverage_plots"] = coverage_plots

    # 3. Virtual Gel
    gel_plot = plot_virtual_gel(polished_assembly, viz_dir)
    if gel_plot:
        viz_outputs["virtual_gel"] = gel_plot

    # 4. Alignment pileup plots
    if validation_results and "sorted_bam" in validation_results:
        pileup_plots = plot_alignment_pileup(
            validation_results["sorted_bam"], 
            polished_assembly, 
            viz_dir
        )
        viz_outputs["pileup_plots"] = pileup_plots

    # 5. Plasmid circular plots from Prokka annotations
    logger.info("Generating plasmid maps...")
    plasmid_plots = {}
    if annotation_results:
        for contig_id, anno_files in annotation_results.items():
            gbk_file = anno_files.get("gbk")
            if gbk_file and Path(gbk_file).exists():
                try:
                    graphic_record = GraphicRecord.from_genbank(gbk_file)
                    ax, _ = graphic_record.plot(figure_width=8, circular=True, strand_in_label_threshold=7)
                    ax.set_title(f"Plasmid Map for {contig_id}", loc="left", fontsize=14)
                    
                    plot_path = viz_dir / f"plasmid_map_{contig_id}.png"
                    ax.figure.savefig(plot_path, bbox_inches='tight', dpi=150)
                    plt.close(ax.figure)
                    plasmid_plots[contig_id] = str(plot_path)
                    logger.info(f"Generated plasmid map for {contig_id}")
                except Exception as e:
                    logger.error(f"Failed to generate plasmid map for {contig_id}: {e}")
    viz_outputs["plasmid_plots"] = plasmid_plots

    logger.info("Visualization step completed.")
    return viz_outputs
