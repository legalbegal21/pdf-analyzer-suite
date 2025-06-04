#!/bin/bash

# PDF Analyzer Suite - Batch Processing Example
# =============================================
#
# This script demonstrates various batch processing scenarios
# for the PDF Analyzer Suite.

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INPUT_DIR="${1:-./pdfs}"  # Default to ./pdfs if no argument provided
OUTPUT_DIR="${2:-./results}"  # Default to ./results if no argument provided

echo -e "${BLUE}PDF Analyzer Suite - Batch Processing Examples${NC}"
echo "=============================================="
echo ""

# Function to check if Python script exists
check_script() {
    if [ ! -f "$PROJECT_ROOT/$1" ]; then
        echo -e "${RED}Error: $1 not found in $PROJECT_ROOT${NC}"
        echo "Please ensure you're running this from the examples directory"
        exit 1
    fi
}

# Check required scripts exist
check_script "pdf_batch_processor.py"
check_script "pdf_analyzer.py"

# Example 1: Basic batch processing of all PDFs in a directory
example1() {
    echo -e "${GREEN}Example 1: Basic Batch Processing${NC}"
    echo "Processing all PDFs in $INPUT_DIR..."
    echo ""
    
    python3 "$PROJECT_ROOT/pdf_batch_processor.py" \
        --input-dir "$INPUT_DIR" \
        --output-dir "$OUTPUT_DIR/example1" \
        --modules all \
        --format json
    
    echo -e "${GREEN}✓ Results saved to $OUTPUT_DIR/example1${NC}"
    echo ""
}

# Example 2: Process only specific modules for faster processing
example2() {
    echo -e "${GREEN}Example 2: Selective Module Processing${NC}"
    echo "Extracting only metadata and text from PDFs..."
    echo ""
    
    python3 "$PROJECT_ROOT/pdf_batch_processor.py" \
        --input-dir "$INPUT_DIR" \
        --output-dir "$OUTPUT_DIR/example2" \
        --modules metadata text \
        --format json
    
    echo -e "${GREEN}✓ Results saved to $OUTPUT_DIR/example2${NC}"
    echo ""
}

# Example 3: Process with HTML report generation
example3() {
    echo -e "${GREEN}Example 3: HTML Report Generation${NC}"
    echo "Creating HTML reports for each PDF..."
    echo ""
    
    python3 "$PROJECT_ROOT/pdf_batch_processor.py" \
        --input-dir "$INPUT_DIR" \
        --output-dir "$OUTPUT_DIR/example3" \
        --modules all \
        --format html \
        --generate-summary
    
    echo -e "${GREEN}✓ HTML reports saved to $OUTPUT_DIR/example3${NC}"
    echo ""
}

# Example 4: Process with filtering (only PDFs modified in last 7 days)
example4() {
    echo -e "${GREEN}Example 4: Process Recent PDFs Only${NC}"
    echo "Processing PDFs modified in the last 7 days..."
    echo ""
    
    # Find PDFs modified in last 7 days and process them
    find "$INPUT_DIR" -name "*.pdf" -type f -mtime -7 | while read -r pdf; do
        filename=$(basename "$pdf")
        echo "Processing: $filename"
        
        python3 "$PROJECT_ROOT/pdf_analyzer.py" \
            "$pdf" \
            --output "$OUTPUT_DIR/example4/${filename%.pdf}_analysis.json" \
            --modules all
    done
    
    echo -e "${GREEN}✓ Results saved to $OUTPUT_DIR/example4${NC}"
    echo ""
}

# Example 5: Parallel processing for better performance
example5() {
    echo -e "${GREEN}Example 5: Parallel Processing${NC}"
    echo "Processing PDFs in parallel (4 workers)..."
    echo ""
    
    python3 "$PROJECT_ROOT/pdf_batch_processor.py" \
        --input-dir "$INPUT_DIR" \
        --output-dir "$OUTPUT_DIR/example5" \
        --modules all \
        --format json \
        --workers 4
    
    echo -e "${GREEN}✓ Results saved to $OUTPUT_DIR/example5${NC}"
    echo ""
}

# Example 6: Extract specific data and create CSV summary
example6() {
    echo -e "${GREEN}Example 6: Extract Data to CSV${NC}"
    echo "Creating CSV summary of all PDFs..."
    echo ""
    
    # Create CSV header
    CSV_FILE="$OUTPUT_DIR/example6/pdf_summary.csv"
    mkdir -p "$OUTPUT_DIR/example6"
    echo "Filename,Pages,Size(MB),Title,Author,Created,Modified,Encrypted,Form Fields,Images,Tables" > "$CSV_FILE"
    
    # Process each PDF and extract key information
    find "$INPUT_DIR" -name "*.pdf" -type f | while read -r pdf; do
        filename=$(basename "$pdf")
        echo "Analyzing: $filename"
        
        # Run analyzer and extract to temporary JSON
        temp_json=$(mktemp)
        python3 "$PROJECT_ROOT/pdf_analyzer.py" "$pdf" \
            --output "$temp_json" \
            --modules metadata structure images forms tables
        
        # Extract data from JSON and append to CSV
        if [ -f "$temp_json" ]; then
            # Use Python to parse JSON and create CSV row
            python3 -c "
import json
import csv
import sys

with open('$temp_json', 'r') as f:
    data = json.load(f)

# Extract relevant fields
row = [
    '$filename',
    data['file_info'].get('page_count', 0),
    round(data['file_info'].get('size_mb', 0), 2),
    data['metadata'].get('title', '').replace(',', ';'),
    data['metadata'].get('author', '').replace(',', ';'),
    data['metadata'].get('creation_date', ''),
    data['metadata'].get('mod_date', ''),
    'Yes' if data['metadata'].get('encrypted', False) else 'No',
    data.get('forms', {}).get('field_count', 0),
    data.get('images', {}).get('count', 0),
    data.get('tables', {}).get('count', 0)
]

# Append to CSV
with open('$CSV_FILE', 'a', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(row)
"
            rm "$temp_json"
        fi
    done
    
    echo -e "${GREEN}✓ CSV summary saved to $CSV_FILE${NC}"
    echo ""
}

# Example 7: Process and archive results
example7() {
    echo -e "${GREEN}Example 7: Process and Archive${NC}"
    echo "Processing PDFs and creating archive..."
    echo ""
    
    # Process PDFs
    python3 "$PROJECT_ROOT/pdf_batch_processor.py" \
        --input-dir "$INPUT_DIR" \
        --output-dir "$OUTPUT_DIR/example7/analysis" \
        --modules all \
        --format json
    
    # Create archive with timestamp
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    ARCHIVE_NAME="pdf_analysis_${TIMESTAMP}.tar.gz"
    
    cd "$OUTPUT_DIR/example7" || exit
    tar -czf "$ARCHIVE_NAME" analysis/
    
    echo -e "${GREEN}✓ Archive created: $OUTPUT_DIR/example7/$ARCHIVE_NAME${NC}"
    echo ""
}

# Example 8: Custom processing pipeline
example8() {
    echo -e "${GREEN}Example 8: Custom Processing Pipeline${NC}"
    echo "Running custom analysis pipeline..."
    echo ""
    
    mkdir -p "$OUTPUT_DIR/example8"
    
    # Step 1: Quick scan for basic info
    echo "Step 1: Quick scan..."
    find "$INPUT_DIR" -name "*.pdf" -type f | head -5 | while read -r pdf; do
        filename=$(basename "$pdf")
        python3 "$PROJECT_ROOT/pdf_analyzer.py" "$pdf" \
            --output "$OUTPUT_DIR/example8/quick_scan/${filename%.pdf}.json" \
            --modules metadata structure
    done
    
    # Step 2: Full analysis for PDFs with forms
    echo "Step 2: Full analysis of PDFs with forms..."
    find "$INPUT_DIR" -name "*.pdf" -type f | while read -r pdf; do
        # Check if PDF has forms
        if python3 -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from pdf_form_analyzer import PDFFormAnalyzer
analyzer = PDFFormAnalyzer()
result = analyzer.analyze_forms('$pdf')
sys.exit(0 if result['is_form'] else 1)
" 2>/dev/null; then
            filename=$(basename "$pdf")
            echo "  - Processing form PDF: $filename"
            python3 "$PROJECT_ROOT/pdf_analyzer.py" "$pdf" \
                --output "$OUTPUT_DIR/example8/forms/${filename%.pdf}_full.json" \
                --modules all
        fi
    done
    
    echo -e "${GREEN}✓ Custom pipeline results saved to $OUTPUT_DIR/example8${NC}"
    echo ""
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [input_directory] [output_directory]"
    echo ""
    echo "Examples:"
    echo "  $0                    # Use default directories (./pdfs and ./results)"
    echo "  $0 /path/to/pdfs      # Specify input directory"
    echo "  $0 /path/to/pdfs /path/to/output  # Specify both directories"
    echo ""
    echo "Available examples:"
    echo "  1. Basic batch processing"
    echo "  2. Selective module processing"
    echo "  3. HTML report generation"
    echo "  4. Process recent PDFs only"
    echo "  5. Parallel processing"
    echo "  6. Extract data to CSV"
    echo "  7. Process and archive"
    echo "  8. Custom processing pipeline"
    echo ""
}

# Main execution
main() {
    # Check if input directory exists
    if [ ! -d "$INPUT_DIR" ]; then
        echo -e "${RED}Error: Input directory '$INPUT_DIR' does not exist${NC}"
        echo ""
        show_usage
        exit 1
    fi
    
    # Check if there are PDFs to process
    PDF_COUNT=$(find "$INPUT_DIR" -name "*.pdf" -type f 2>/dev/null | wc -l)
    if [ "$PDF_COUNT" -eq 0 ]; then
        echo -e "${YELLOW}Warning: No PDF files found in '$INPUT_DIR'${NC}"
        echo ""
        show_usage
        exit 1
    fi
    
    echo "Found $PDF_COUNT PDF files in $INPUT_DIR"
    echo ""
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Ask which example to run
    echo "Which example would you like to run?"
    echo "1-8: Run specific example"
    echo "9: Run all examples"
    echo "0: Exit"
    echo ""
    read -p "Enter your choice (0-9): " choice
    
    case $choice in
        1) example1 ;;
        2) example2 ;;
        3) example3 ;;
        4) example4 ;;
        5) example5 ;;
        6) example6 ;;
        7) example7 ;;
        8) example8 ;;
        9)
            echo -e "${BLUE}Running all examples...${NC}"
            echo ""
            example1
            example2
            example3
            example4
            example5
            example6
            example7
            example8
            echo -e "${GREEN}✓ All examples completed!${NC}"
            ;;
        0)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please run the script again.${NC}"
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${BLUE}Batch processing complete!${NC}"
    echo "Results are available in: $OUTPUT_DIR"
    echo ""
    echo "Tips:"
    echo "- View JSON results: cat $OUTPUT_DIR/example1/*.json | jq ."
    echo "- Open HTML reports: open $OUTPUT_DIR/example3/*.html"
    echo "- Check CSV summary: cat $OUTPUT_DIR/example6/pdf_summary.csv"
}

# Run main function
main