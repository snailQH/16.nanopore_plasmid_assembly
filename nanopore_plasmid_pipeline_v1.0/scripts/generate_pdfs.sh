#!/bin/bash
# Generate PDF files from all HTML reports
# Usage: generate_pdfs.sh [HTML_DIR] [OUTPUT_DIR]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default paths
HTML_DIR="${1:-$PROJECT_ROOT/results/individual_reports}"
OUTPUT_DIR="${2:-$PROJECT_ROOT/results/individual_reports}"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Check if Chrome exists
if [ ! -f "$CHROME" ]; then
    echo "Error: Chrome not found at $CHROME"
    exit 1
fi

# Check if HTML directory exists
if [ ! -d "$HTML_DIR" ]; then
    echo "Error: HTML directory not found: $HTML_DIR"
    exit 1
fi

echo "Converting HTML reports to PDF..."
echo "Input directory: $HTML_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Create output directory if needed
mkdir -p "$OUTPUT_DIR"
count=0

for html_file in "$HTML_DIR"/*.html; do
    if [ -f "$html_file" ]; then
        base_name=$(basename "$html_file" .html)
        pdf_file="$OUTPUT_DIR/${base_name}.pdf"
        
        echo "Converting: $base_name"
        "$CHROME" --headless --disable-gpu --print-to-pdf="$pdf_file" "file://$html_file" 2>/dev/null
        
        if [ -f "$pdf_file" ]; then
            echo "  ✓ Created: $pdf_file"
            ((count++))
        else
            echo "  ✗ Failed: $pdf_file"
        fi
    fi
done

echo ""
echo "✓ Successfully converted $count PDF files"

