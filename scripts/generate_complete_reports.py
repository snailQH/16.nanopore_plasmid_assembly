#!/usr/bin/env python3
"""
Generate complete reports in QB-template format.
Integrates coverage calculation, per-base breakdown, and PDF report generation.

Output structure:
- {project_id}_FASTA_FILES/
- {project_id}_RAW_FASTQ_FILES/
- {project_id}_PER_BASE_BREAKDOWN/
- {project_id}_QC_REPORTS/
- {project_id}_summary.csv

Usage:
    python3 generate_complete_reports.py [OPTIONS]
"""

import argparse
import csv
import gzip
import json
import logging
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError as e:
    print(f"ERROR: Required library not installed: {e}")
    print("Please install dependencies with:")
    print("  pip install reportlab matplotlib numpy --user")
    sys.exit(1)

# Import coverage calculation functions
try:
    from generate_coverage_reports import (
        read_fasta, read_fastq, simple_align, reverse_complement,
        compute_coverage, create_coverage_plot
    )
except ImportError:
    # Fallback: define functions here if import fails
    logging.warning("Could not import from generate_coverage_reports, using inline definitions")
    
    def read_fasta(fasta_file):
        """Read FASTA file and return sequences as dict."""
        sequences = {}
        current_seq = ""
        current_id = ""
        
        with open(fasta_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('>'):
                    if current_id:
                        sequences[current_id] = current_seq.upper()
                    current_id = line[1:].strip().split()[0]
                    current_seq = ""
                else:
                    current_seq += line.strip()
            
            if current_id:
                sequences[current_id] = current_seq.upper()
        
        return sequences
    
    def read_fastq(fastq_file):
        """Read FASTQ file (supports .gz) and yield (id, sequence, quality) tuples."""
        if str(fastq_file).endswith('.gz'):
            open_func = gzip.open
            mode = 'rt'
            encoding_kwargs = {}
        else:
            open_func = open
            mode = 'r'
            encoding_kwargs = {'encoding': 'utf-8', 'errors': 'ignore'}
        
        with open_func(fastq_file, mode, **encoding_kwargs) as f:
            while True:
                header = f.readline().strip()
                if not header:
                    break
                if not header.startswith('@'):
                    continue
                
                seq = f.readline().strip()
                plus = f.readline().strip()
                qual = f.readline().strip()
                
                if not seq or not qual:
                    break
                
                yield (header[1:], seq, qual)
    
    def simple_align(read_seq, ref_seq, min_match=20):
        """Simple alignment to find best match position."""
        read_len = len(read_seq)
        ref_len = len(ref_seq)
        
        best_score = 0
        best_pos = -1
        
        for i in range(max(0, ref_len - read_len - 100), min(ref_len - min_match + 1, ref_len)):
            match_len = min(read_len, ref_len - i)
            if match_len < min_match:
                continue
            
            matches = sum(1 for j in range(match_len) if read_seq[j] == ref_seq[i + j])
            score = matches / match_len if match_len > 0 else 0
            
            if score > best_score:
                best_score = score
                best_pos = i
        
        return best_pos if best_score > 0.7 else -1
    
    def reverse_complement(seq):
        """Return reverse complement of sequence."""
        comp = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
        return ''.join(comp.get(base, 'N') for base in reversed(seq))
    
    # Import compute_coverage and create_coverage_plot from generate_coverage_reports
    import importlib.util
    coverage_script = Path(__file__).parent / 'generate_coverage_reports.py'
    if coverage_script.exists():
        spec = importlib.util.spec_from_file_location("coverage_module", coverage_script)
        coverage_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(coverage_module)
        compute_coverage = coverage_module.compute_coverage
        create_coverage_plot = coverage_module.create_coverage_plot
    else:
        logging.error("generate_coverage_reports.py not found")
        sys.exit(1)

def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

COMPANY_NAME = "AmpSeq"
COMPANY_WEBSITE = "www.ampseq.com"

def get_all_samples(data_dir):
    """Get all sample names from FASTA files."""
    fasta_files = list(Path(data_dir).glob('*.final.fasta'))
    samples = [f.stem.replace('.final', '') for f in fasta_files]
    return sorted(samples)

def find_fasta_files(data_dir):
    """Find all FASTA files in data directory (supports multiple patterns)."""
    fasta_files = []
    data_path = Path(data_dir)
    
    # Try different patterns
    patterns = ['*.final.fasta', '*.fa', '*.fasta']
    for pattern in patterns:
        fasta_files.extend(list(data_path.glob(pattern)))
    
    return list(set(fasta_files))  # Remove duplicates

def find_fastq_files(data_dir, sample_name=None):
    """
    Find FASTQ files for a sample (supports multiple patterns).
    Can match files where sample_name is contained in the filename.
    Examples:
    - USX140904.final.fastq -> matches USX140904
    - PBE94302_pass_USX140904_6ebb3c45_d6847234_0.fastq.gz -> matches USX140904 (contains sample_name)
    """
    fastq_files = []
    data_path = Path(data_dir)
    
    if sample_name:
        # First try exact patterns (most common cases)
        exact_patterns = [
            f'{sample_name}.final.fastq',
            f'{sample_name}.final.fastq.gz',
            f'{sample_name}_reads.fastq',
            f'{sample_name}_reads.fastq.gz',
            f'{sample_name}.fastq',
            f'{sample_name}.fastq.gz'
        ]
        
        for pattern in exact_patterns:
            found = list(data_path.glob(pattern))
            if found:
                logging.debug(f"  Found FASTQ using exact pattern: {pattern}")
                fastq_files.extend(found)
                return list(set(fastq_files))  # Return early if exact match found
        
        # If no exact match, try to find files containing sample_name in filename
        logging.info(f"  No exact match found, searching for files containing '{sample_name}' in filename...")
        all_fastq_patterns = [
            '*.fastq',
            '*.fastq.gz',
            '*.fq',
            '*.fq.gz'
        ]
        
        for pattern in all_fastq_patterns:
            for fastq_file in data_path.glob(pattern):
                # Check if filename contains sample_name
                # Make sure it's a real match (not substring, e.g., USX1409 matching USX140904)
                if sample_name in fastq_file.name:
                    # Additional check: sample_name should not be part of a longer identifier
                    # This helps avoid false matches, but allows patterns like "PBE94302_pass_USX140904_..."
                    logging.info(f"  Found FASTQ containing sample name: {fastq_file.name}")
                    fastq_files.append(fastq_file)
        
        # Prefer .final.fastq files if both exist
        final_files = [f for f in fastq_files if '.final.' in f.name]
        if final_files:
            return list(set(final_files))
        
    else:
        # Find all fastq files
        patterns = ['*.final.fastq', '*.final.fastq.gz', '*_reads.fastq', '*_reads.fastq.gz', '*.fastq', '*.fastq.gz']
        for pattern in patterns:
            fastq_files.extend(list(data_path.glob(pattern)))
    
    return list(set(fastq_files))

def organize_files_by_sample_per_sample_structure(data_dir, output_base_dir, project_id=None, fasta_dir=None, fastq_dir=None, ab1_dir=None):
    """
    Organize files by sample - each sample gets its own folder with subdirectories.
    Structure: {sample_name}/
                    FASTA_FILES/
                    RAW_FASTQ_FILES/
                    PER_BASE_BREAKDOWN/
                    QC_REPORTS/
                    CHROMATOGRAM_FILES_ab1/  (empty for now)
    """
    # Determine samples
    if fasta_dir:
        # Use provided FASTA directory
        # Exclude .insert.fasta files (these are insert sequences, not main assemblies)
        fasta_files = [f for f in find_fasta_files(fasta_dir) if '.insert.fasta' not in f.name]
        samples = []
        for f in fasta_files:
            # Extract sample name from filename
            # Patterns: {sample}_contig{num}.fa, {sample}.final.fasta, etc.
            name = f.stem
            if '_contig' in name:
                sample = name.split('_contig')[0]
            elif '.final' in name:
                sample = name.replace('.final', '')
            else:
                sample = name
            
            if sample not in samples:
                samples.append(sample)
        samples = sorted(set(samples))
    else:
        # Find samples from data_dir
        samples = get_all_samples(data_dir)
    
    sample_dirs = {}
    
    for sample in samples:
        # Create sample-specific directory structure
        sample_dir = output_base_dir / sample
        
        # Create subdirectories
        sample_fasta_dir = sample_dir / 'FASTA_FILES'
        sample_fastq_dir = sample_dir / 'RAW_FASTQ_FILES'
        sample_per_base_dir = sample_dir / 'PER_BASE_BREAKDOWN'
        sample_reports_dir = sample_dir / 'QC_REPORTS'
        sample_ab1_dir = sample_dir / 'CHROMATOGRAM_FILES_ab1'  # Empty for now
        
        for dir_path in [sample_fasta_dir, sample_fastq_dir, sample_per_base_dir, sample_reports_dir, sample_ab1_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Find and copy FASTA files for this sample
        # Exclude .insert.fasta files (these are insert sequences, not main assemblies)
        if fasta_dir:
            sample_fasta_files = [
                f for f in find_fasta_files(fasta_dir) 
                if sample in f.name and '.insert.fasta' not in f.name
            ]
        else:
            sample_fasta_files = [Path(data_dir) / f'{sample}.final.fasta']
        
        sample_contigs = []
        
        for fasta_file in sample_fasta_files:
            if not fasta_file.exists():
                continue
            
            contigs = read_fasta(fasta_file)
            for contig_name, seq in contigs.items():
                # Write individual contig FASTA file
                contig_fasta = sample_fasta_dir / f'{sample}_{contig_name}.fa'
                with open(contig_fasta, 'w') as f:
                    f.write(f'>{contig_name}\n{seq}\n')
                
                sample_contigs.append({
                    'name': contig_name,
                    'file': contig_fasta,
                    'length': len(seq)
                })
        
        # Find and copy FASTQ files for this sample
        logging.debug(f"  Finding FASTQ files for sample: {sample}")
        if fastq_dir:
            sample_fastq_files = find_fastq_files(fastq_dir, sample)
        else:
            sample_fastq_files = find_fastq_files(data_dir, sample)
        
        fastq_file_to_use = None
        if sample_fastq_files:
            logging.info(f"  Found {len(sample_fastq_files)} FASTQ file(s) for {sample}: {[f.name for f in sample_fastq_files]}")
        else:
            logging.warning(f"  No FASTQ file found for sample: {sample}")
        
        for fastq_file in sample_fastq_files:
            if fastq_file.exists():
                logging.debug(f"    Using FASTQ file: {fastq_file}")
                # Copy to sample directory
                if fastq_file.suffix == '.gz' or fastq_file.name.endswith('.fastq.gz') or fastq_file.name.endswith('.fq.gz'):
                    target = sample_fastq_dir / f'{sample}_reads.fastq.gz'
                    shutil.copy2(fastq_file, target)
                    fastq_file_to_use = target
                    logging.debug(f"    Copied to: {target}")
                else:
                    # Only create .gz version (don't keep uncompressed .fastq)
                    with open(fastq_file, 'rb') as f_in:
                        target = sample_fastq_dir / f'{sample}_reads.fastq.gz'
                        with gzip.open(target, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    fastq_file_to_use = target
                    logging.debug(f"    Created .gz version: {target}")
                break
        
        # Copy AB1 files to CHROMATOGRAM_FILES_ab1 directory if ab1_dir is provided
        if ab1_dir:
            ab1_source_dir = Path(ab1_dir)
            # Look for sample-specific AB1 directory (e.g., sample02_ab1/)
            sample_ab1_source = ab1_source_dir / f'{sample}_ab1'
            if sample_ab1_source.exists() and sample_ab1_source.is_dir():
                ab1_files = list(sample_ab1_source.glob('*.ab1'))
                if ab1_files:
                    logging.info(f"  Copying {len(ab1_files)} AB1 files for {sample}...")
                    for ab1_file in ab1_files:
                        target_ab1 = sample_ab1_dir / ab1_file.name
                        shutil.copy2(ab1_file, target_ab1)
                        logging.debug(f"    Copied AB1: {ab1_file.name}")
                    logging.info(f"  ✓ Copied {len(ab1_files)} AB1 files to {sample_ab1_dir.name}")
                else:
                    logging.debug(f"  No AB1 files found in {sample_ab1_source}")
            else:
                logging.debug(f"  AB1 source directory not found: {sample_ab1_source}")
        
        sample_dirs[sample] = {
            'sample_dir': sample_dir,
            'fasta_dir': sample_fasta_dir,
            'fastq_dir': sample_fastq_dir,
            'per_base_dir': sample_per_base_dir,
            'reports_dir': sample_reports_dir,
            'ab1_dir': sample_ab1_dir,
            'contigs': sample_contigs,
            'fastq_file': fastq_file_to_use
        }
    
    return sample_dirs

def organize_files_by_sample(data_dir, output_base_dir, project_id):
    """Organize FASTA and FASTQ files by sample into QB-template structure."""
    samples = get_all_samples(data_dir)
    
    # Create directory structure
    fasta_dir = output_base_dir / f'{project_id}_FASTA_FILES'
    fastq_dir = output_base_dir / f'{project_id}_RAW_FASTQ_FILES'
    per_base_dir = output_base_dir / f'{project_id}_PER_BASE_BREAKDOWN'
    reports_dir = output_base_dir / f'{project_id}_QC_REPORTS'
    
    for dir_path in [fasta_dir, fastq_dir, per_base_dir, reports_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Copy FASTA files (split by contig if multiple)
    sample_contigs = {}
    
    for sample in samples:
        fasta_file = Path(data_dir) / f'{sample}.final.fasta'
        if not fasta_file.exists():
            continue
        
        contigs = read_fasta(fasta_file)
        sample_contigs[sample] = []
        
        for contig_name, seq in contigs.items():
            # Write individual contig FASTA file
            contig_fasta = fasta_dir / f'{sample}_{contig_name}.fa'
            with open(contig_fasta, 'w') as f:
                f.write(f'>{contig_name}\n{seq}\n')
            
            sample_contigs[sample].append({
                'name': contig_name,
                'file': contig_fasta,
                'length': len(seq)
            })
        
        # Copy FASTQ file if exists
        fastq_file = Path(data_dir) / f'{sample}.final.fastq'
        if fastq_file.exists():
            fastq_target = fastq_dir / f'{sample}_reads.fastq'
            shutil.copy2(fastq_file, fastq_target)
            
            # Also create .gz version if needed
            with open(fastq_file, 'rb') as f_in:
                with gzip.open(fastq_dir / f'{sample}_reads.fastq.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
    
    return {
        'fasta_dir': fasta_dir,
        'fastq_dir': fastq_dir,
        'per_base_dir': per_base_dir,
        'reports_dir': reports_dir,
        'samples': samples,
        'sample_contigs': sample_contigs
    }

def process_sample_complete(sample_name, sample_dirs, verbose=False):
    """Process a single sample completely: coverage, per-base breakdown, and PDF."""
    logging.info(f"Processing sample: {sample_name}")
    
    dirs = sample_dirs[sample_name]
    fastq_file = dirs['fastq_file']
    
    if not fastq_file or not fastq_file.exists():
        logging.warning(f"FASTQ file not found for {sample_name}")
        # Try to find in sample directory
        fastq_files = list(dirs['fastq_dir'].glob(f'{sample_name}_reads.fastq*'))
        if fastq_files:
            fastq_file = fastq_files[0]
        else:
            logging.warning(f"Missing FASTQ file for {sample_name}")
            return None
    
    # Get FASTA files from sample directory
    fasta_files = list(dirs['fasta_dir'].glob('*.fa'))
    if not fasta_files:
        logging.warning(f"No FASTA files found for {sample_name}")
        return None
    
    # Read contigs from all FASTA files
    all_contigs = {}
    for fasta_file in fasta_files:
        contigs = read_fasta(fasta_file)
        all_contigs.update(contigs)
    
    if not all_contigs:
        logging.warning(f"No contigs found for {sample_name}")
        return None
    
    # Process each contig
    contig_results = []
    
    # Use the first FASTA file as reference for coverage calculation
    reference_fasta = fasta_files[0]
    
    for contig_name, ref_seq in all_contigs.items():
        logging.info(f"  Processing contig: {contig_name} ({len(ref_seq)} bp)")
        logging.info(f"    Computing coverage and per-base breakdown...")
        
        # Compute coverage and per-base breakdown
        cov_data = compute_coverage(
            reference_fasta, fastq_file, sample_name, contig_name, dirs['per_base_dir']
        )
        
        if cov_data:
            logging.info(f"    ✓ Coverage computed: avg={cov_data['avg_coverage']:.1f}x, mapped={cov_data['mapped_reads']:,}/{cov_data['total_reads']:,} reads")
            # Create coverage plot
            plot_file = dirs['per_base_dir'] / f'{sample_name}_{contig_name}_coverage.png'
            # Check if coverage plot was already created, if not create it
            if not plot_file.exists():
                logging.info(f"    Creating coverage plot...")
                create_coverage_plot(cov_data, contig_name, str(plot_file))
                logging.info(f"    ✓ Coverage plot saved: {plot_file.name}")
            else:
                logging.info(f"    Coverage plot already exists: {plot_file.name}")
            
            contig_results.append({
                'name': contig_name,
                'length': len(ref_seq),
                'coverage_data': cov_data,
                'plot_file': plot_file
            })
    
    # Count reads and bases from FASTQ
    logging.info(f"  Counting reads and bases from FASTQ: {fastq_file.name}")
    total_reads = 0
    total_bases = 0
    
    try:
        for idx, (read_id, seq, qual) in enumerate(read_fastq(fastq_file)):
            total_reads += 1
            total_bases += len(seq)
            # Progress update every 10000 reads
            if (idx + 1) % 10000 == 0:
                logging.info(f"    Processed {idx + 1:,} reads...")
        logging.info(f"  ✓ Total: {total_reads:,} reads, {total_bases:,} bases")
    except Exception as e:
        logging.warning(f"Error counting reads: {e}")
    
    # Calculate FASTA statistics (Host Genomic DNA)
    logging.info(f"  Calculating FASTA statistics...")
    # Contig count = number of sequences in FASTA
    host_reads = len(all_contigs)  # Number of contigs/sequences in FASTA
    
    # Total bases in all contigs
    host_bases = sum(len(seq) for seq in all_contigs.values())
    logging.info(f"  ✓ Host Genomic DNA: {host_reads} contigs, {host_bases:,} bases")
    
    # Generate PDF report
    logging.info(f"  Generating PDF report...")
    pdf_file = dirs['reports_dir'] / f'{sample_name}_report.pdf'
    generate_sample_pdf(sample_name, contig_results, dirs, fastq_file, pdf_file, verbose, 
                       total_reads, total_bases, host_reads, host_bases)
    logging.info(f"  ✓ PDF report saved: {pdf_file.name}")
    
    return {
        'sample': sample_name,
        'total_reads': total_reads,
        'total_bases': total_bases,
        'contigs': contig_results
    }

def generate_sample_pdf(sample_name, contig_results, dirs, fastq_file, output_file, verbose=False, 
                        total_reads=0, total_bases=0, host_reads=0, host_bases=0):
    """Generate PDF report for a sample."""
    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1.0*inch,
        bottomMargin=0.75*inch
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#0079a4'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#0079a4'),
        spaceAfter=10,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph(f"Whole Plasmid Sequencing Report: {sample_name}", title_style)
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # Basic Statistics
    # Count reads and bases from FASTQ file
    total_reads = 0
    total_bases = 0
    
    try:
        for read_id, seq, qual in read_fastq(fastq_file):
            total_reads += 1
            total_bases += len(seq)
    except Exception as e:
        logging.warning(f"Error counting reads from FASTQ: {e}")
        # Fallback: use coverage data if available
        if contig_results:
            total_reads = contig_results[0]['coverage_data'].get('total_reads', 0)
            total_bases = contig_results[0]['coverage_data'].get('total_bases', 0)
    
    story.append(Paragraph("Basic Information Statistics", heading_style))
    
    # Calculate percentages for Host Genomic DNA
    host_reads_pct = (host_reads / total_reads * 100) if total_reads > 0 else 0.0
    host_bases_pct = (host_bases / total_bases * 100) if total_bases > 0 else 0.0
    
    basic_stats = [
        ['Name', 'Reads', 'Bases'],
        ['Total DNA', f'{total_reads:,}', f'{total_bases:,}'],
        ['Host Genomic DNA', f'{host_reads:,} ({host_reads_pct:.2f}%)', f'{host_bases:,} ({host_bases_pct:.2f}%)']
    ]
    
    basic_table = Table(basic_stats, colWidths=[2.5*inch, 2*inch, 2*inch])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0079a4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    
    story.append(basic_table)
    story.append(Spacer(1, 0.4*inch))
    
    # Assembly Status
    if contig_results:
        story.append(Paragraph("Assembly Status", heading_style))
        
        status_note = "more than 1 contig, contamination?" if len(contig_results) > 1 else "single contig"
        story.append(Paragraph(f"<i>Assembly Status: {status_note}</i>", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        # Assembly status table
        assembly_data = [['Contig', 'Length (bp)', 'Reads Mapped', 'Bases Mapped', 'Multimer', 'Coverage', 'Is Circular']]
        
        for contig in contig_results:
            cov_data = contig['coverage_data']
            reads_mapped = cov_data['mapped_reads']
            bases_mapped = int(cov_data['avg_coverage'] * contig['length'])
            coverage = int(cov_data['avg_coverage'])
            
            # Calculate percentages relative to total reads/bases from FASTQ
            reads_mapped_pct = (reads_mapped / total_reads * 100) if total_reads > 0 else 0.0
            bases_mapped_pct = (bases_mapped / total_bases * 100) if total_bases > 0 else 0.0
            
            reads_mapped_str = f"{reads_mapped:,} ({reads_mapped_pct:.2f}%)"
            bases_mapped_str = f"{bases_mapped:,} ({bases_mapped_pct:.2f}%)"
            
            assembly_data.append([
                contig['name'],
                f"{contig['length']:,}",
                reads_mapped_str,
                bases_mapped_str,
                "0.00%",
                f"{coverage}x",
                "False"
            ])
        
        assembly_table = Table(assembly_data, colWidths=[1.5*inch, 0.9*inch, 1*inch, 1*inch, 0.8*inch, 0.7*inch, 0.9*inch])
        assembly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0079a4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        
        story.append(assembly_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Coverage Plots for each contig
        for i, contig in enumerate(contig_results):
            if i > 0:
                story.append(PageBreak())
            
            story.append(Paragraph(f"{contig['name']} Coverage Map", heading_style))
            story.append(Paragraph("<i>low confidence positions are marked with orange 'x'</i>", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            plot_file = contig['plot_file']
            if plot_file.exists():
                try:
                    img = Image(str(plot_file), width=6.5*inch, height=3*inch)
                    story.append(img)
                except Exception as e:
                    logging.warning(f"Failed to add coverage plot: {e}")
                    story.append(Paragraph("<i>Coverage plot could not be generated</i>", styles['Normal']))
            else:
                story.append(Paragraph("<i>Coverage plot could not be generated</i>", styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
        
        # Read Length Distribution
        story.append(PageBreak())
        story.append(Paragraph("Read Length Distribution", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Generate read length distribution using existing script
        script_dir = Path(__file__).parent
        length_dist_script = script_dir / 'get_length_dist_from_fastq.py'
        
        length_dist_img_file = None  # Store the file path to keep it alive
        
        if length_dist_script.exists():
            temp_dir = tempfile.mkdtemp(prefix=f'{sample_name}_')
            try:
                result = subprocess.run(
                    [sys.executable, str(length_dist_script), str(fastq_file), '--output-dir', temp_dir],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # Wait a moment to ensure files are written
                    import time
                    time.sleep(0.2)
                    
                    # The script generates files with format: {fastq_filename}.length_dist.{ext}
                    # Look for the actual generated files
                    found_file = None
                    
                    # Search for any .length_dist files in temp_dir
                    length_dist_files = list(Path(temp_dir).glob('*.length_dist.png'))
                    if not length_dist_files:
                        length_dist_files = list(Path(temp_dir).glob('*.length_dist.pdf'))
                    if length_dist_files:
                        found_file = length_dist_files[0]
                    
                    if found_file and found_file.suffix == '.png':
                        # Copy to a more permanent location to avoid deletion issues
                        length_dist_img_file = dirs['per_base_dir'] / f'{sample_name}_read_length_dist.png'
                        try:
                            shutil.copy2(found_file, length_dist_img_file)
                            length_dist_img_file = str(length_dist_img_file)  # Use copied file
                            
                            # Verify file exists and has content
                            if Path(length_dist_img_file).exists() and Path(length_dist_img_file).stat().st_size > 0:
                                img = Image(length_dist_img_file, width=6.5*inch, height=4*inch)
                                story.append(img)
                            else:
                                raise FileNotFoundError(f"Copied file not found or empty: {length_dist_img_file}")
                        except Exception as e:
                            logging.warning(f"Failed to add read length distribution plot: {e}")
                            story.append(Paragraph("<i>Read length distribution plot could not be generated</i>", styles['Normal']))
                    elif found_file and found_file.suffix == '.pdf':
                        story.append(Paragraph("<i>Read length distribution PDF generated (image extraction needed)</i>", styles['Normal']))
                    else:
                        # Debug: list what files were actually created
                        actual_files = list(Path(temp_dir).glob('*'))
                        logging.warning(f"Read length dist files not found. Actual files in temp_dir: {[f.name for f in actual_files]}")
                        if verbose and result.stdout:
                            logging.debug(f"Script stdout: {result.stdout}")
                        if verbose and result.stderr:
                            logging.debug(f"Script stderr: {result.stderr}")
                        story.append(Paragraph("<i>Read length distribution plot could not be generated</i>", styles['Normal']))
                else:
                    logging.warning(f"Read length distribution script failed: {result.stderr}")
                    if verbose:
                        logging.debug(f"Script stdout: {result.stdout}")
                    story.append(Paragraph("<i>Read length distribution plot could not be generated</i>", styles['Normal']))
            finally:
                # Cleanup temp directory (but keep copied file if it exists)
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
        else:
            story.append(Paragraph("<i>Read length distribution script not found</i>", styles['Normal']))
    
    # Build PDF (build before cleaning up temp directory)
    def create_header_footer(canvas_obj, doc):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.setFillColor(colors.HexColor('#0079a4'))
        canvas_obj.drawString(inch, 10.5*inch, COMPANY_NAME)
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.setFillColor(colors.HexColor('#666666'))
        canvas_obj.drawString(7*inch, 10.5*inch, COMPANY_WEBSITE)
        canvas_obj.drawRightString(8*inch, 10.2*inch, datetime.now().strftime('%Y-%m-%d'))
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(colors.HexColor('#999999'))
        footer_text = f"Generated by {COMPANY_NAME} | {COMPANY_WEBSITE}"
        canvas_obj.drawCentredString(4.25*inch, 0.5*inch, footer_text)
        canvas_obj.drawRightString(8*inch, 0.5*inch, f"Page {doc.page}")
        canvas_obj.restoreState()
    
    doc.build(story, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    
    return output_file

def read_circularity_from_gbk(gbk_file):
    """Read circularity information from GenBank file."""
    if not gbk_file or not gbk_file.exists():
        return None
    
    try:
        with open(gbk_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'LOCUS' in line:
                    # GenBank LOCUS line format: LOCUS       <name>              <length> bp    DNA     <circular/linear>    UNK
                    if 'circular' in line.lower():
                        return True
                    elif 'linear' in line.lower():
                        return False
        return None
    except Exception as e:
        logging.debug(f"Error reading circularity from {gbk_file}: {e}")
        return None

def generate_summary_csv(output_base_dir, project_id, all_results, assembly_dir=None):
    """Generate summary CSV file."""
    summary_file = output_base_dir / f'{project_id}_summary.csv'
    
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Sample Name', 'Total Read Count', 'Total Base Count',
            'E-coli Read Count', 'E-coli Base Count', 'Contig Name',
            'Contig Length (bp)', 'Reads Mapped to Contig', 'Bases Mapped to Contig',
            'Multimer (by mass)', 'Coverage', 'Is Circular', 'Reaction Status'
        ])
        
        for result in all_results:
            if not result:
                continue
            
            sample_name = result['sample']
            total_reads = result['total_reads']
            total_bases = result['total_bases']
            
            # Try to read circularity from GenBank file if available
            is_circular = False
            if assembly_dir:
                gbk_file = Path(assembly_dir) / f'{sample_name}.annotations.gbk'
                circularity = read_circularity_from_gbk(gbk_file)
                if circularity is not None:
                    is_circular = circularity
            
            for contig in result['contigs']:
                cov_data = contig['coverage_data']
                
                # Calculate coverage (ensure it's at least 0)
                coverage = max(0, int(cov_data.get('avg_coverage', 0)))
                
                writer.writerow([
                    sample_name,
                    total_reads,
                    total_bases,
                    0,  # E-coli reads
                    0,  # E-coli bases
                    contig['name'],
                    contig['length'],
                    cov_data.get('mapped_reads', 0),
                    int(coverage * contig['length']),
                    '0.00%',  # Multimer
                    f"{coverage}x",
                    str(is_circular),  # Is Circular (read from GenBank if available)
                    'SUCCESS'
                ])
    
    logging.info(f"Summary CSV written to: {summary_file}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate complete reports in QB-template format',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-d', '--data-dir',
        type=str,
        default=None,
        help='Data directory containing .final.fasta and .final.fastq files (default: ../output)'
    )
    
    parser.add_argument(
        '--fasta-dir',
        type=str,
        default=None,
        help='Directory containing FASTA files (overrides data-dir for FASTA files)'
    )
    
    parser.add_argument(
        '--fastq-dir',
        type=str,
        default=None,
        help='Directory containing FASTQ files (overrides data-dir for FASTQ files)'
    )
    
    parser.add_argument(
        '--assembly-dir',
        type=str,
        default=None,
        help='Directory containing assembly output files (for reading circularity from GenBank files)'
    )
    
    parser.add_argument(
        '--ab1-dir',
        type=str,
        default=None,
        help='Directory containing AB1 files (for copying to report directories)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output base directory (default: ../results)'
    )
    
    parser.add_argument(
        '--project-id',
        type=str,
        default=None,
        help='Project ID for summary CSV filename (default: auto-generated from date)'
    )
    
    parser.add_argument(
        '--per-sample-folders',
        action='store_true',
        default=True,
        help='Create separate folder for each sample (default: True)'
    )
    
    parser.add_argument(
        '--samples',
        nargs='+',
        help='Specific sample names to process (default: all samples found)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    # Determine default paths
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    
    # Determine data directories
    if args.fasta_dir:
        fasta_dir = Path(args.fasta_dir).resolve()
    else:
        fasta_dir = None
    
    if args.fastq_dir:
        fastq_dir = Path(args.fastq_dir).resolve()
    else:
        fastq_dir = None
    
    if args.data_dir is None:
        data_dir = project_root / 'output'
    else:
        data_dir = Path(args.data_dir).resolve()
    
    # Use data_dir as fallback for fasta/fastq if not specified
    if fasta_dir is None:
        fasta_dir = data_dir
    if fastq_dir is None:
        fastq_dir = data_dir
    
    # Assembly directory for reading GenBank files (defaults to fasta_dir)
    if args.assembly_dir:
        assembly_dir = Path(args.assembly_dir).resolve()
    else:
        assembly_dir = fasta_dir  # Use fasta_dir as default
    
    # AB1 directory for copying AB1 files to report directories
    if args.ab1_dir:
        ab1_dir = Path(args.ab1_dir).resolve()
    else:
        ab1_dir = None
    
    if args.output is None:
        output_base_dir = project_root / 'results'
    else:
        output_base_dir = Path(args.output).resolve()
    
    if args.project_id is None:
        project_id = datetime.now().strftime('%Y%m%d')
    else:
        project_id = args.project_id
    
    # Organize files by sample (each sample gets its own folder)
    logging.info("=" * 60)
    logging.info(f"Organizing files by sample...")
    logging.info(f"  Data directory: {data_dir}")
    if fasta_dir != data_dir:
        logging.info(f"  FASTA directory: {fasta_dir}")
    if fastq_dir != data_dir:
        logging.info(f"  FASTQ directory: {fastq_dir}")
    if ab1_dir:
        logging.info(f"  AB1 directory: {ab1_dir}")
    logging.info(f"  Output directory: {output_base_dir}")
    logging.info(f"  Project ID: {project_id}")
    sample_dirs = organize_files_by_sample_per_sample_structure(
        str(data_dir), output_base_dir, project_id, 
        str(fasta_dir) if fasta_dir != data_dir else None,
        str(fastq_dir) if fastq_dir != data_dir else None,
        str(ab1_dir) if ab1_dir else None
    )
    logging.info(f"  Found {len(sample_dirs)} samples")
    
    # Get samples to process
    if args.samples:
        samples = [s for s in args.samples if s in sample_dirs]
        if len(samples) < len(args.samples):
            missing = set(args.samples) - set(samples)
            logging.warning(f"Some samples not found: {', '.join(missing)}")
    else:
        samples = list(sample_dirs.keys())
    
    if not samples:
        logging.error("No samples found to process!")
        return 1
    
    logging.info(f"Processing {len(samples)} samples...")
    
    # Process each sample
    all_results = []
    
    for sample in samples:
        try:
            result = process_sample_complete(sample, sample_dirs, args.verbose)
            if result:
                all_results.append(result)
                logging.info(f"  ✓ Successfully processed {sample}")
            else:
                logging.warning(f"  ⚠ No results generated for {sample}")
        except Exception as e:
            logging.error(f"  ✗ Failed to process {sample}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    # Generate summary CSV
    if all_results:
        logging.info("Generating summary CSV...")
        # Pass assembly_dir to read circularity from GenBank files
        generate_summary_csv(output_base_dir, project_id, all_results, assembly_dir=assembly_dir)
    
    logging.info(f"\n✓ Successfully processed {len(all_results)} samples")
    logging.info(f"Output structure: {output_base_dir}/{{sample_name}}/{{subdirectories}}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

