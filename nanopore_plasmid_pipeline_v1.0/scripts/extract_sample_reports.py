#!/usr/bin/env python3
"""
Extract individual sample reports from a multi-sample HTML report.
For each sample, creates an HTML file and optionally converts to PDF.

Usage:
    python3 extract_sample_reports.py [OPTIONS]
    
    python3 extract_sample_reports.py -i wf-clone-validation-report.html -o reports
    
    python3 extract_sample_reports.py -i report.html -o output_dir --samples UPA42701 UPA42703
    
    python3 extract_sample_reports.py -i report.html --verbose

Examples:
    # Extract all samples from default report file
    python3 extract_sample_reports.py
    
    # Specify input and output directories
    python3 extract_sample_reports.py -i my_report.html -o my_output
    
    # Process specific samples only
    python3 extract_sample_reports.py --samples UPA42701 USX140562
    
    # Show detailed logs
    python3 extract_sample_reports.py --verbose
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# Configure logging
def setup_logging(verbose=False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def get_all_samples(input_dir=None):
    """
    Get all sample names from the directory.
    
    Args:
        input_dir: Directory to search for .final.fasta files. Defaults to current directory.
        
    Returns:
        List of sample names (sorted)
    """
    if input_dir is None:
        input_dir = Path('.')
    else:
        input_dir = Path(input_dir)
    
    if not input_dir.exists():
        logging.error(f"Directory not found: {input_dir}")
        return []
    
    samples = []
    for fasta_file in input_dir.glob('*.final.fasta'):
        # Remove .final from the stem
        sample_name = fasta_file.stem.replace('.final', '')
        samples.append(sample_name)
    
    return sorted(samples)

def create_sample_report(original_html, sample_name):
    """
    Create a focused report for a single sample.
    Strategy: Use string replacement to modify tab classes directly
    """
    # Use string replacement approach which is more reliable
    modified_html = original_html
    
    # Update title
    modified_html = re.sub(
        r'<title>[^<]+</title>',
        f'<title>Clone Validation Report - {sample_name}</title>',
        modified_html
    )
    
    # Update main heading
    modified_html = re.sub(
        r'<h1[^>]*>[^<]+</h1>',
        f'<h1>Clone Validation Report - {sample_name}</h1>',
        modified_html,
        count=1
    )
    
    # Update all dropdown toggle buttons to show the sample name
    modified_html = re.sub(
        r'<button[^>]*class="[^"]*dropdown-toggle[^"]*"[^>]*>Dropdown</button>',
        f'<button class="nav-link px-0 me-4 text-muted dropdown-toggle">{sample_name}</button>',
        modified_html
    )
    
    # Find all dropdown items and make only the target sample active
    # First, remove 'active' from all dropdown items
    modified_html = re.sub(
        r'class="dropdown-item active"',
        r'class="dropdown-item"',
        modified_html
    )
    
    # Then add 'active' back to the target sample's dropdown items
    # Match button with sample name, regardless of attribute order
    modified_html = re.sub(
        f'(<button[^>]*>{sample_name}</button>)',
        lambda m: m.group(1).replace('class="dropdown-item"', 'class="dropdown-item active"') if 'dropdown-item' in m.group(1) else m.group(1),
        modified_html
    )
    
    # Now handle tab panes: activate tabs using the aria-controls from dropdown items
    # The strategy: Find the dropdown item button for this sample, get its aria-controls value,
    # then activate the tab-pane with matching ID
    
    # First, remove 'active' and 'show' from all tab-panes
    modified_html = re.sub(
        r'class="tab-pane fade(?: show active| active show| show| active)"',
        r'class="tab-pane fade"',
        modified_html
    )
    
    # Find dropdown item buttons with this sample name and extract their aria-controls
    dropdown_pattern = rf'<button[^>]*aria-controls="([^"]+)"[^>]*>{re.escape(sample_name)}</button>'
    matches = re.findall(dropdown_pattern, modified_html)
    
    # Activate tabs with matching IDs
    for tab_id in matches:
        # Escape special regex chars in the tab_id
        escaped_tab_id = re.escape(tab_id)
        # Pattern to find the tab-pane div with this id (handles any attributes)
        tab_pattern = rf'(<div[^>]*class="tab-pane fade"[^>]*id="{escaped_tab_id}"[^>]*>|<div[^>]*id="{escaped_tab_id}"[^>]*class="tab-pane fade"[^>]*>)'
        
        def activate_tab(match):
            attrs = match.group(1)
            # Replace class="tab-pane fade" with class="tab-pane fade show active"
            attrs = attrs.replace('class="tab-pane fade"', 'class="tab-pane fade show active"')
            return attrs
        
        modified_html = re.sub(tab_pattern, activate_tab, modified_html)
    
    # Now use BeautifulSoup to filter the Sample status table
    # This is cleaner than complex regex for HTML table manipulation
    soup = BeautifulSoup(modified_html, 'html.parser')
    
    # Find the Sample status table
    sample_status_section = soup.find('section', id='Section_3bdef24a96d84a65b198530ee48c71cc')
    if sample_status_section:
        # Find the table within the Sample status section
        table = sample_status_section.find('table')
        if table:
            # Find all tbody rows
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                # Keep only the row with the target sample
                for row in rows:
                    first_cell = row.find('td')
                    if first_cell and first_cell.get_text().strip() != sample_name:
                        # Remove this row if it's not the target sample
                        row.decompose()
    
    return str(soup)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Extract individual sample reports from a multi-sample HTML report',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all samples from default report file
  %(prog)s
  
  # Specify input and output directories
  %(prog)s -i my_report.html -o my_output
  
  # Process specific samples only
  %(prog)s --samples UPA42701 USX140562
  
  # Show detailed logs
  %(prog)s --verbose
  
  # Get help
  %(prog)s -h
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        default='wf-clone-validation-report.html',
        help='Input HTML report file (default: wf-clone-validation-report.html)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output directory for individual reports (default: ../results/individual_reports)'
    )
    
    parser.add_argument(
        '-d', '--data-dir',
        type=str,
        default=None,
        help='Directory containing .final.fasta files (default: ../output)'
    )
    
    parser.add_argument(
        '--samples',
        nargs='+',
        help='Specific sample names to process (default: all samples found in data directory)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--no-pdf-hint',
        action='store_true',
        help='Do not show PDF conversion hints at the end'
    )
    
    return parser.parse_args()

def main():
    """Main extraction function."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Determine default paths relative to script location
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent
    
    # Set default paths
    if args.data_dir is None:
        args.data_dir = project_root / 'output'
    else:
        args.data_dir = Path(args.data_dir).resolve()
    
    if args.output is None:
        args.output = project_root / 'results' / 'individual_reports'
    else:
        args.output = Path(args.output).resolve()
    
    # Validate input file
    html_file = Path(args.input)
    if not html_file.is_absolute():
        html_file = args.data_dir / html_file.name
    
    if not html_file.exists():
        logging.error(f"Input file not found: {html_file.absolute()}")
        logging.info("Please specify the correct input file with -i option")
        return 1
    
    logging.info(f"Input file: {html_file.absolute()}")
    
    # Get samples to process
    if args.samples:
        samples = args.samples
        logging.info(f"Processing specified samples: {', '.join(samples)}")
    else:
        samples = get_all_samples(str(args.data_dir))
        if not samples:
            logging.error("No samples found! Make sure .final.fasta files exist in the data directory.")
            logging.info(f"Data directory: {args.data_dir.absolute()}")
            logging.info("You can also use --samples to specify sample names manually")
            return 1
        logging.info(f"Found {len(samples)} samples in data directory: {', '.join(samples)}")
    
    # Read original HTML once
    try:
        logging.debug("Reading input HTML file...")
        with open(str(html_file), 'r', encoding='utf-8') as f:
            original_html = f.read()
        logging.debug(f"Read {len(original_html):,} characters from input file")
    except Exception as e:
        logging.error(f"Failed to read input file: {e}")
        return 1
    
    # Create output directory
    output_dir = Path(args.output)
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Output directory: {output_dir.absolute()}")
    except Exception as e:
        logging.error(f"Failed to create output directory: {e}")
        return 1
    
    # Process each sample
    success_count = 0
    failed_samples = []
    
    for sample in samples:
        logging.info(f"Processing {sample}...")
        
        try:
            # Create individual HTML
            logging.debug(f"  Creating focused report for {sample}...")
            individual_html = create_sample_report(original_html, sample)
            
            # Save HTML file
            html_output = output_dir / f'{sample}_report.html'
            with open(html_output, 'w', encoding='utf-8') as f:
                f.write(individual_html)
            
            file_size = html_output.stat().st_size / 1024 / 1024  # Size in MB
            logging.info(f"  ✓ Created: {html_output.name} ({file_size:.2f} MB)")
            success_count += 1
            
        except Exception as e:
            logging.error(f"  ✗ Failed to process {sample}: {e}")
            failed_samples.append(sample)
    
    # Print summary
    print("")
    if success_count > 0:
        logging.info(f"✓ Successfully created {success_count} HTML reports in {output_dir}/")
    
    if failed_samples:
        logging.warning(f"✗ Failed to process {len(failed_samples)} samples: {', '.join(failed_samples)}")
        return 1
    
    # Print PDF conversion hints
    if not args.no_pdf_hint:
        print("")
        logging.info("💡 To create PDF files from HTML:")
        logging.info("   1. Use the generate_pdfs.sh script: ./generate_pdfs.sh")
        logging.info("   2. Or use Chrome headless: chrome --headless --print-to-pdf=output.pdf input.html")
        logging.info("   3. Or use weasyprint: pip install weasyprint && weasyprint input.html output.pdf")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

