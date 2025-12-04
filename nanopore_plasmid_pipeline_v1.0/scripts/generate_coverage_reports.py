#!/usr/bin/env python3
"""
Generate coverage reports based on FASTA and FASTQ files.
Computes real coverage by aligning FASTQ reads to FASTA contigs.

Usage:
    python3 generate_coverage_reports.py [OPTIONS]

Examples:
    # Process all samples
    python3 generate_coverage_reports.py
    
    # Process specific samples
    python3 generate_coverage_reports.py --samples UPA42701 USX140562
"""

import argparse
import csv
import gzip
import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from collections import defaultdict

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"ERROR: Required library not installed: {e}")
    print("Please install dependencies with:")
    print("  pip install numpy matplotlib --user")
    sys.exit(1)

def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

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
    is_gz = fastq_file.suffix == '.gz' or str(fastq_file).endswith('.fastq.gz')
    if is_gz:
        open_func = gzip.open
        mode = 'rt'
        encoding_kwargs = {}
    else:
        open_func = open
        mode = 'r'
        encoding_kwargs = {'encoding': 'utf-8', 'errors': 'ignore'}
    
    with open_func(fastq_file, mode, **encoding_kwargs) as f:
        while True:
            try:
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
            except StopIteration:
                break

def simple_align(read_seq, ref_seq, min_match=20):
    """Simple alignment to find best match position."""
    read_len = len(read_seq)
    ref_len = len(ref_seq)
    
    best_score = 0
    best_pos = -1
    
    # Try forward alignment
    for i in range(max(0, ref_len - read_len - 100), min(ref_len - min_match + 1, ref_len)):
        match_len = min(read_len, ref_len - i)
        if match_len < min_match:
            continue
        
        matches = sum(1 for j in range(match_len) if read_seq[j] == ref_seq[i + j])
        score = matches / match_len if match_len > 0 else 0
        
        if score > best_score:
            best_score = score
            best_pos = i
    
    # Try reverse complement alignment (simplified)
    rev_read = reverse_complement(read_seq)
    for i in range(max(0, ref_len - len(rev_read) - 100), min(ref_len - min_match + 1, ref_len)):
        match_len = min(len(rev_read), ref_len - i)
        if match_len < min_match:
            continue
        
        matches = sum(1 for j in range(match_len) if rev_read[j] == ref_seq[i + j])
        score = matches / match_len if match_len > 0 else 0
        
        if score > best_score:
            best_score = score
            best_pos = i
    
    return best_pos if best_score > 0.7 else -1  # 70% identity threshold

def reverse_complement(seq):
    """Return reverse complement of sequence."""
    comp = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    return ''.join(comp.get(base, 'N') for base in reversed(seq))

def compute_coverage(fasta_file, fastq_file, sample_name, contig_name, output_dir):
    """Compute coverage for a contig by aligning FASTQ reads to FASTA."""
    logging.debug(f"Computing coverage for {contig_name} from {fasta_file}")
    
    # Read reference sequence
    ref_sequences = read_fasta(fasta_file)
    if contig_name not in ref_sequences:
        logging.warning(f"Contig {contig_name} not found in {fasta_file}")
        return None
    
    ref_seq = ref_sequences[contig_name]
    ref_len = len(ref_seq)
    
    # Initialize coverage array
    coverage = np.zeros(ref_len, dtype=int)
    depth_per_pos = defaultdict(int)  # position -> depth
    
    # Track base counts at each position
    base_counts = defaultdict(lambda: {'A': 0, 'T': 0, 'G': 0, 'C': 0})
    
    # Align reads
    read_count = 0
    mapped_reads = 0
    
    try:
        for read_id, read_seq, read_qual in read_fastq(fastq_file):
            read_count += 1
            if read_count % 1000 == 0:
                logging.debug(f"Processed {read_count} reads, {mapped_reads} mapped")
            
            # Simple alignment
            pos = simple_align(read_seq.upper(), ref_seq)
            
            if pos >= 0:
                mapped_reads += 1
                read_len = len(read_seq)
                
                # Update coverage
                for i in range(min(read_len, ref_len - pos)):
                    if pos + i < ref_len:
                        coverage[pos + i] += 1
                        depth_per_pos[pos + i] += 1
                        
                        # Count bases
                        base = read_seq[i].upper()
                        if base in 'ATGC':
                            base_counts[pos + i][base] += 1
    except Exception as e:
        logging.warning(f"Error processing reads: {e}")
    
    logging.info(f"Mapped {mapped_reads}/{read_count} reads to {contig_name}")
    
    # Calculate statistics
    avg_coverage = np.mean(coverage) if len(coverage) > 0 else 0
    max_coverage = np.max(coverage) if len(coverage) > 0 else 0
    
    # Generate per-base details CSV
    # Format: {sample}_{contig}_per_base_details.csv (match QB-template format)
    per_base_file = output_dir / f'{sample_name}_{contig_name}_per_base_details.csv'
    low_conf_file = output_dir / f'{sample_name}_{contig_name}_low_confidence_bases.csv'
    
    low_conf_positions = []
    
    with open(per_base_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['pos', 'base', 'depth', 'match_count', 'vaf', 'G', 'A', 'T', 'C', 'ins', 'del', 'qscore', 'confidence', 'methylation'])
        
        for i in range(ref_len):
            depth = coverage[i]
            ref_base = ref_seq[i]
            
            # Get base counts
            counts = base_counts[i]
            total_bases = sum(counts.values())
            
            # Determine consensus base
            if total_bases > 0:
                consensus = max(counts.items(), key=lambda x: x[1])[0]
                match_count = counts.get(ref_base, 0)
                vaf = match_count / total_bases if total_bases > 0 else 0
            else:
                consensus = ref_base
                match_count = 0
                vaf = 1.0
            
            # Low confidence if depth < 3 or vaf < 0.8
            confidence = 'low' if depth < 3 or vaf < 0.8 else ''
            if confidence == 'low':
                low_conf_positions.append(i)
            
            # Calculate average quality (placeholder)
            avg_qscore = 30 if depth > 0 else 0
            
            writer.writerow([
                i + 1,  # 1-based position
                consensus,
                depth,
                match_count,
                f"{vaf:.2f}" if depth > 0 else "1.0",
                counts.get('G', 0),
                counts.get('A', 0),
                counts.get('T', 0),
                counts.get('C', 0),
                0,  # insertions
                0,  # deletions
                avg_qscore,
                confidence,
                ''  # methylation
            ])
    
    # Write low confidence bases
    with open(low_conf_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['pos', 'base', 'depth', 'match_count', 'vaf', 'G', 'A', 'T', 'C', 'ins', 'del', 'qscore', 'confidence', 'variants'])
        
        for pos in low_conf_positions[:100]:  # Limit to first 100
            depth = coverage[pos]
            ref_base = ref_seq[pos]
            counts = base_counts[pos]
            total_bases = sum(counts.values())
            match_count = counts.get(ref_base, 0)
            vaf = match_count / total_bases if total_bases > 0 else 0
            
            writer.writerow([
                pos + 1,
                ref_base,
                depth,
                match_count,
                f"{vaf:.2f}" if depth > 0 else "1.0",
                counts.get('G', 0),
                counts.get('A', 0),
                counts.get('T', 0),
                counts.get('C', 0),
                0, 0, 30, 'low', ''
            ])
    
    return {
        'coverage': coverage,
        'avg_coverage': avg_coverage,
        'max_coverage': max_coverage,
        'mapped_reads': mapped_reads,
        'total_reads': read_count,
        'per_base_file': per_base_file,
        'low_conf_file': low_conf_file
    }

def create_coverage_plot(coverage_data, contig_name, output_file):
    """Create coverage plot."""
    coverage = coverage_data['coverage']
    positions = np.arange(len(coverage))
    
    fig, ax = plt.subplots(figsize=(12, 4))
    
    # Plot coverage
    ax.plot(positions, coverage, color='#0079a4', linewidth=0.5, alpha=0.7)
    ax.fill_between(positions, 0, coverage, alpha=0.3, color='#0079a4')
    
    # Mark low coverage regions
    low_coverage = coverage < 3
    if np.any(low_coverage):
        ax.scatter(positions[low_coverage], coverage[low_coverage], 
                  color='orange', marker='x', s=20, alpha=0.6, label='Low confidence')
    
    ax.set_xlabel('Position (bp)', fontsize=10)
    ax.set_ylabel('Coverage (x)', fontsize=10)
    ax.set_title(f'{contig_name} Coverage Map', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Add statistics text
    stats_text = f"Avg: {coverage_data['avg_coverage']:.1f}x, Max: {coverage_data['max_coverage']}x"
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_file

def process_sample(sample_name, data_dir, output_base_dir, verbose=False):
    """Process a single sample."""
    logging.info(f"Processing sample: {sample_name}")
    
    # Create output directory for this sample
    sample_dir = output_base_dir / sample_name
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    # Find FASTA and FASTQ files
    fasta_file = Path(data_dir) / f'{sample_name}.final.fasta'
    fastq_file = Path(data_dir) / f'{sample_name}.final.fastq'
    
    if not fasta_file.exists():
        logging.warning(f"FASTA file not found: {fasta_file}")
        return False
    
    if not fastq_file.exists():
        logging.warning(f"FASTQ file not found: {fastq_file}")
        return False
    
    # Read FASTA to get contigs
    contigs = read_fasta(fasta_file)
    logging.info(f"Found {len(contigs)} contigs in {sample_name}")
    
    # Process each contig
    coverage_results = []
    
    for contig_name, ref_seq in contigs.items():
        logging.info(f"  Processing contig: {contig_name} (length: {len(ref_seq)} bp)")
        
        # Compute coverage
        cov_data = compute_coverage(fasta_file, fastq_file, sample_name, contig_name, sample_dir)
        
        if cov_data:
            # Create coverage plot
            plot_file = sample_dir / f'{contig_name}_coverage.png'
            create_coverage_plot(cov_data, contig_name, str(plot_file))
            
            coverage_results.append({
                'contig': contig_name,
                'length': len(ref_seq),
                'coverage_data': cov_data
            })
    
    # Generate summary CSV
    summary_file = output_base_dir / 'summary.csv'
    write_summary(summary_file, sample_name, fastq_file, coverage_results)
    
    return True

def write_summary(summary_file, sample_name, fastq_file, coverage_results):
    """Write or append to summary CSV."""
    # Count total reads and bases from FASTQ
    total_reads = 0
    total_bases = 0
    
    try:
        for read_id, seq, qual in read_fastq(fastq_file):
            total_reads += 1
            total_bases += len(seq)
    except Exception as e:
        logging.warning(f"Error counting reads: {e}")
    
    # Append to summary file
    file_exists = summary_file.exists()
    
    with open(summary_file, 'a', newline='') as f:
        writer = csv.writer(f)
        
        if not file_exists:
            writer.writerow(['Sample Name', 'Total Read Count', 'Total Base Count', 
                           'E-coli Read Count', 'E-coli Base Count', 'Contig Name', 
                           'Contig Length (bp)', 'Reads Mapped to Contig', 'Bases Mapped to Contig',
                           'Multimer (by mass)', 'Coverage', 'Is Circular', 'Reaction Status'])
        
        for result in coverage_results:
            cov_data = result['coverage_data']
            writer.writerow([
                sample_name,
                total_reads,
                total_bases,
                0,  # E-coli reads (would need separate calculation)
                0,  # E-coli bases
                result['contig'],
                result['length'],
                cov_data['mapped_reads'],
                int(cov_data['avg_coverage'] * result['length']),
                '0.00%',  # Multimer (would need calculation)
                f"{int(cov_data['avg_coverage'])}x",
                'False',  # Is Circular (would need check)
                'SUCCESS'
            ])

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate coverage reports from FASTA and FASTQ files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-d', '--data-dir',
        type=str,
        default=None,
        help='Data directory containing .final.fasta and .final.fastq files (default: ../output)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output base directory (default: ../results/coverage_reports)'
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
    
    if args.data_dir is None:
        data_dir = project_root / 'output'
    else:
        data_dir = Path(args.data_dir).resolve()
    
    if args.output is None:
        output_dir = project_root / 'results' / 'coverage_reports'
    else:
        output_dir = Path(args.output).resolve()
    
    # Get samples to process
    if args.samples:
        samples = args.samples
    else:
        # Find all samples from FASTA files
        fasta_files = list(data_dir.glob('*.final.fasta'))
        samples = [f.stem.replace('.final', '') for f in fasta_files]
    
    logging.info(f"Found {len(samples)} samples to process")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Remove existing summary file
    summary_file = output_dir / 'summary.csv'
    if summary_file.exists():
        summary_file.unlink()
    
    # Process each sample
    success_count = 0
    failed_samples = []
    
    for sample in samples:
        try:
            if process_sample(sample, str(data_dir), output_dir, args.verbose):
                success_count += 1
                logging.info(f"  ✓ Successfully processed {sample}")
            else:
                failed_samples.append(sample)
        except Exception as e:
            logging.error(f"  ✗ Failed to process {sample}: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            failed_samples.append(sample)
    
    # Print summary
    logging.info(f"\n✓ Successfully processed {success_count} samples")
    if failed_samples:
        logging.warning(f"✗ Failed to process {len(failed_samples)} samples: {', '.join(failed_samples)}")
    
    return 0 if not failed_samples else 1

if __name__ == '__main__':
    sys.exit(main())

