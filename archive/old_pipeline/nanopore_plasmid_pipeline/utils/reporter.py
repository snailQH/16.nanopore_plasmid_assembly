import os
import base64
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from Bio import SeqIO

logger = logging.getLogger(__name__)

def get_file_content(file_path):
    """Safely read content of a file."""
    if file_path and Path(file_path).exists():
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
    return "Not available"

def encode_image_to_base64(image_path):
    """Encode an image file to a base64 string."""
    if image_path and Path(image_path).exists():
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            logger.warning(f"Could not encode image {image_path}: {e}")
    return None

def generate_html_report(
    input_fastq, cleaned_reads, assembly_result, polished_result, 
    annotation_result, validation_result, viz_result, report_dir, args):
    """
    Generates a single-page HTML report from pipeline results.
    """
    logger.info("Generating HTML report...")
    
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    template = env.get_template("report_template.html")

    # Prepare data for the template
    report_data = {
        "run_args": args,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "assembly_info": get_file_content(Path(assembly_result).parent / "assembly_info.txt"),
        "flagstat_report": get_file_content(validation_result.get("flagstat_report")),
        "read_length_plot_b64": encode_image_to_base64(viz_result.get("read_length_plot")),
        "virtual_gel_plot_b64": encode_image_to_base64(viz_result.get("virtual_gel")),
        "contigs": []
    }

    # Process each contig
    if polished_result and Path(polished_result).exists():
        for record in SeqIO.parse(polished_result, "fasta"):
            contig_id = record.id
            contig_data = {
                "id": contig_id,
                "length": len(record.seq),
                "coverage_plot_b64": None,
                "pileup_plot_b64": None,
                "plasmid_map_b64": None,
                "annotation_gff": "Not available"
            }

            if viz_result.get("coverage_plots"):
                contig_data["coverage_plot_b64"] = encode_image_to_base64(
                    viz_result["coverage_plots"].get(contig_id)
                )

            if viz_result.get("pileup_plots"):
                contig_data["pileup_plot_b64"] = encode_image_to_base64(
                    viz_result["pileup_plots"].get(contig_id)
                )

            if viz_result.get("plasmid_plots"):
                contig_data["plasmid_map_b64"] = encode_image_to_base64(
                    viz_result["plasmid_plots"].get(contig_id)
                )
            
            if annotation_result and annotation_result.get(contig_id):
                 contig_data["annotation_gff"] = get_file_content(
                     annotation_result[contig_id].get("gff")
                 )

            report_data["contigs"].append(contig_data)

    # Render and save the report
    html_content = template.render(report_data)
    report_path = Path(report_dir) / "plasmid_pipeline_report.html"
    with open(report_path, "w") as f:
        f.write(html_content)

    logger.info(f"HTML report saved to {report_path}")
    return str(report_path)
