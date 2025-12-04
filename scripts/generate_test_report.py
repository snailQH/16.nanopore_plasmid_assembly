#!/usr/bin/env python3
"""
Generate comprehensive test report for pipeline execution.

This script analyzes pipeline execution logs and outputs to generate
a detailed test report in Markdown format.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def analyze_log_file(log_file):
    """Analyze a log file and extract key information."""
    if not log_file.exists():
        return None
    
    info = {
        'file': str(log_file),
        'size': log_file.stat().st_size,
        'lines': 0,
        'errors': [],
        'warnings': [],
        'key_events': []
    }
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            info['lines'] = len(lines)
            
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                if 'error' in line_lower or 'failed' in line_lower:
                    info['errors'].append((i, line.strip()))
                elif 'warning' in line_lower or 'warn' in line_lower:
                    info['warnings'].append((i, line.strip()))
                elif any(keyword in line_lower for keyword in ['completed', 'success', 'finished', 'done']):
                    info['key_events'].append((i, line.strip()))
    except Exception as e:
        logging.warning(f"Error reading log file {log_file}: {e}")
    
    return info

def count_files(directory, pattern="*"):
    """Count files matching pattern in directory."""
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))

def analyze_step_outputs(output_dir):
    """Analyze outputs from each pipeline step."""
    output_path = Path(output_dir)
    analysis = {
        'step0_initialization': {},
        'step1_assembly': {},
        'step2_fragments': {},
        'step3_ab1': {},
        'step4_reports': {}
    }
    
    # Step 0: Initialization
    config_file = output_path / 'config.yaml'
    if config_file.exists():
        analysis['step0_initialization']['config_exists'] = True
        analysis['step0_initialization']['config_size'] = config_file.stat().st_size
    
    # Step 1: Assembly
    assembly_dir = output_path / '01.assembly'
    if assembly_dir.exists():
        fasta_files = list(assembly_dir.glob('*.final.fasta'))
        analysis['step1_assembly']['fasta_count'] = len(fasta_files)
        analysis['step1_assembly']['fasta_files'] = [f.name for f in fasta_files]
        
        # Check for Nextflow work directory
        work_dir = assembly_dir / 'work'
        if work_dir.exists():
            analysis['step1_assembly']['work_dir_exists'] = True
        
        # Check for samplesheet
        samplesheet = assembly_dir / 'samplesheet.csv'
        if samplesheet.exists():
            analysis['step1_assembly']['samplesheet_exists'] = True
    
    # Step 2: Fragments
    fragments_dir = output_path / '02.fragments'
    if fragments_dir.exists():
        fragment_dirs = [d for d in fragments_dir.iterdir() if d.is_dir() and '_fragmented' in d.name]
        analysis['step2_fragments']['sample_count'] = len(fragment_dirs)
        analysis['step2_fragments']['samples'] = [d.name for d in fragment_dirs]
        
        total_fragments = 0
        for frag_dir in fragment_dirs:
            frag_count = count_files(frag_dir, "*.fasta")
            total_fragments += frag_count
        analysis['step2_fragments']['total_fragments'] = total_fragments
    
    # Step 3: AB1 files
    ab1_dir = output_path / '03.ab1_files'
    if ab1_dir.exists():
        ab1_dirs = [d for d in ab1_dir.iterdir() if d.is_dir() and '_ab1' in d.name]
        analysis['step3_ab1']['sample_count'] = len(ab1_dirs)
        analysis['step3_ab1']['samples'] = [d.name for d in ab1_dirs]
        
        total_ab1 = 0
        for ab1_sample_dir in ab1_dirs:
            ab1_count = count_files(ab1_sample_dir, "*.ab1")
            total_ab1 += ab1_count
        analysis['step3_ab1']['total_ab1_files'] = total_ab1
    
    # Step 4: Reports
    reports_dir = output_path / '04.reports'
    if reports_dir.exists():
        pdf_files = list(reports_dir.glob('*.pdf'))
        json_files = list(reports_dir.glob('*.json'))
        analysis['step4_reports']['pdf_count'] = len(pdf_files)
        analysis['step4_reports']['json_count'] = len(json_files)
        analysis['step4_reports']['pdf_files'] = [f.name for f in pdf_files]
        analysis['step4_reports']['json_files'] = [f.name for f in json_files]
    
    return analysis

def generate_markdown_report(output_dir, report_file):
    """Generate comprehensive test report in Markdown format."""
    output_path = Path(output_dir)
    report_path = Path(report_file)
    
    # Analyze outputs
    analysis = analyze_step_outputs(output_dir)
    
    # Analyze log files
    logs_dir = output_path / 'logs'
    log_files = {}
    if logs_dir.exists():
        for log_file in logs_dir.glob('*.log'):
            log_files[log_file.stem] = analyze_log_file(log_file)
    
    # Generate report
    report_lines = []
    report_lines.append("# Pipeline Test Report")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Output Directory:** `{output_dir}`")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Executive Summary
    report_lines.append("## Executive Summary")
    report_lines.append("")
    
    # Check pipeline completion
    all_steps_complete = (
        analysis['step1_assembly'].get('fasta_count', 0) > 0 and
        analysis['step2_fragments'].get('total_fragments', 0) > 0 and
        analysis['step3_ab1'].get('total_ab1_files', 0) > 0
    )
    
    if all_steps_complete:
        report_lines.append("✅ **Pipeline Status:** SUCCESS - All steps completed successfully")
    else:
        report_lines.append("⚠️ **Pipeline Status:** INCOMPLETE - Some steps may not have completed")
    
    report_lines.append("")
    
    # Step-by-step analysis
    report_lines.append("## Step-by-Step Analysis")
    report_lines.append("")
    
    # Step 0: Initialization
    report_lines.append("### Step 0: Initialization")
    report_lines.append("")
    if analysis['step0_initialization'].get('config_exists'):
        report_lines.append(f"- ✅ Configuration file generated: `config.yaml` ({analysis['step0_initialization']['config_size']} bytes)")
    else:
        report_lines.append("- ❌ Configuration file not found")
    report_lines.append("")
    
    # Step 1: Assembly
    report_lines.append("### Step 1: Assembly (epi2me wf-clone-validation)")
    report_lines.append("")
    fasta_count = analysis['step1_assembly'].get('fasta_count', 0)
    if fasta_count > 0:
        report_lines.append(f"- ✅ **FASTA files generated:** {fasta_count}")
        report_lines.append(f"- **Files:**")
        for fasta_file in analysis['step1_assembly'].get('fasta_files', [])[:10]:
            report_lines.append(f"  - `{fasta_file}`")
        if fasta_count > 10:
            report_lines.append(f"  - ... and {fasta_count - 10} more")
    else:
        report_lines.append("- ❌ No FASTA files found")
    
    if analysis['step1_assembly'].get('samplesheet_exists'):
        report_lines.append("- ✅ Samplesheet generated")
    
    report_lines.append("")
    
    # Step 2: Fragment Splitting
    report_lines.append("### Step 2: Fragment Splitting")
    report_lines.append("")
    fragment_count = analysis['step2_fragments'].get('total_fragments', 0)
    sample_count = analysis['step2_fragments'].get('sample_count', 0)
    if fragment_count > 0:
        report_lines.append(f"- ✅ **Total fragments generated:** {fragment_count}")
        report_lines.append(f"- **Samples processed:** {sample_count}")
        report_lines.append(f"- **Average fragments per sample:** {fragment_count / sample_count if sample_count > 0 else 0:.1f}")
    else:
        report_lines.append("- ❌ No fragments found")
    report_lines.append("")
    
    # Step 3: AB1 Generation
    report_lines.append("### Step 3: AB1 File Generation")
    report_lines.append("")
    ab1_count = analysis['step3_ab1'].get('total_ab1_files', 0)
    ab1_sample_count = analysis['step3_ab1'].get('sample_count', 0)
    if ab1_count > 0:
        report_lines.append(f"- ✅ **Total AB1 files generated:** {ab1_count}")
        report_lines.append(f"- **Samples processed:** {ab1_sample_count}")
        report_lines.append(f"- **Average AB1 files per sample:** {ab1_count / ab1_sample_count if ab1_sample_count > 0 else 0:.1f}")
    else:
        report_lines.append("- ❌ No AB1 files found")
    report_lines.append("")
    
    # Step 4: Reports
    report_lines.append("### Step 4: Report Generation")
    report_lines.append("")
    pdf_count = analysis['step4_reports'].get('pdf_count', 0)
    json_count = analysis['step4_reports'].get('json_count', 0)
    if pdf_count > 0:
        report_lines.append(f"- ✅ **PDF reports generated:** {pdf_count}")
        for pdf_file in analysis['step4_reports'].get('pdf_files', [])[:5]:
            report_lines.append(f"  - `{pdf_file}`")
    else:
        report_lines.append("- ⚠️ No PDF reports found")
    
    if json_count > 0:
        report_lines.append(f"- ✅ **JSON files generated:** {json_count}")
    else:
        report_lines.append("- ⚠️ No JSON files found")
    report_lines.append("")
    
    # Log Analysis
    report_lines.append("## Log Analysis")
    report_lines.append("")
    
    if log_files:
        for log_name, log_info in sorted(log_files.items()):
            if log_info:
                report_lines.append(f"### {log_name}")
                report_lines.append("")
                report_lines.append(f"- **File:** `{log_info['file']}`")
                report_lines.append(f"- **Size:** {log_info['size']:,} bytes")
                report_lines.append(f"- **Lines:** {log_info['lines']:,}")
                
                if log_info['errors']:
                    report_lines.append(f"- ⚠️ **Errors:** {len(log_info['errors'])}")
                    for line_num, error_line in log_info['errors'][:5]:
                        report_lines.append(f"  - Line {line_num}: `{error_line[:100]}...`")
                
                if log_info['warnings']:
                    report_lines.append(f"- ⚠️ **Warnings:** {len(log_info['warnings'])}")
                
                if log_info['key_events']:
                    report_lines.append(f"- ✅ **Key events:** {len(log_info['key_events'])}")
                    for line_num, event_line in log_info['key_events'][-3:]:
                        report_lines.append(f"  - Line {line_num}: `{event_line[:100]}...`")
                
                report_lines.append("")
    else:
        report_lines.append("No log files found in `logs/` directory.")
        report_lines.append("")
    
    # File Structure
    report_lines.append("## Output Directory Structure")
    report_lines.append("")
    report_lines.append("```")
    
    def print_tree(path, prefix="", max_depth=3, current_depth=0):
        """Print directory tree structure."""
        if current_depth >= max_depth:
            return []
        
        lines = []
        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                lines.append(f"{prefix}{current_prefix}{item.name}")
                
                if item.is_dir() and current_depth < max_depth - 1:
                    extension = "    " if is_last else "│   "
                    lines.extend(print_tree(item, prefix + extension, max_depth, current_depth + 1))
        except PermissionError:
            pass
        
        return lines
    
    tree_lines = print_tree(output_path, max_depth=3)
    report_lines.extend(tree_lines)
    report_lines.append("```")
    report_lines.append("")
    
    # Statistics Summary
    report_lines.append("## Statistics Summary")
    report_lines.append("")
    report_lines.append("| Metric | Value |")
    report_lines.append("|--------|-------|")
    report_lines.append(f"| FASTA files | {analysis['step1_assembly'].get('fasta_count', 0)} |")
    report_lines.append(f"| Fragment directories | {analysis['step2_fragments'].get('sample_count', 0)} |")
    report_lines.append(f"| Total fragments | {analysis['step2_fragments'].get('total_fragments', 0)} |")
    report_lines.append(f"| AB1 sample directories | {analysis['step3_ab1'].get('sample_count', 0)} |")
    report_lines.append(f"| Total AB1 files | {analysis['step3_ab1'].get('total_ab1_files', 0)} |")
    report_lines.append(f"| PDF reports | {analysis['step4_reports'].get('pdf_count', 0)} |")
    report_lines.append(f"| JSON files | {analysis['step4_reports'].get('json_count', 0)} |")
    report_lines.append(f"| Log files | {len(log_files)} |")
    report_lines.append("")
    
    # Write report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    logging.info(f"Test report generated: {report_path}")
    return report_path

def main():
    parser = argparse.ArgumentParser(description='Generate pipeline test report')
    parser.add_argument('--output-dir', '-o', required=True, help='Pipeline output directory')
    parser.add_argument('--report-file', '-r', default='test_report.md', help='Output report file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    
    try:
        report_path = generate_markdown_report(args.output_dir, args.report_file)
        print(f"\n✅ Test report generated: {report_path}")
        return 0
    except Exception as e:
        logging.error(f"Failed to generate test report: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

