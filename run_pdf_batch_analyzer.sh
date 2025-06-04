#!/bin/bash
# PDF Batch Analyzer Wrapper Script
# Activates the proper virtual environment and runs the analyzer

set -x  # Enable verbose output

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== PDF Batch Analyzer ===${NC}"
echo "Processes multiple PDFs in parallel with comprehensive analysis"
echo ""

# Check if we're in WSL
if [ ! -f /proc/version ] || ! grep -qi microsoft /proc/version; then
    echo -e "${YELLOW}Warning: This script is optimized for WSL environments${NC}"
fi

# Virtual environment path
VENV_PATH="/home/lroc/unified-redaction-hub/venv"

# Check if virtual environment exists
if [ -d "$VENV_PATH" ]; then
    echo -e "${GREEN}Using virtual environment: $VENV_PATH${NC}"
    # Run with venv python
    PYTHON_CMD="$VENV_PATH/bin/python"
else
    echo -e "${YELLOW}Virtual environment not found at $VENV_PATH${NC}"
    echo "Using system Python instead"
    PYTHON_CMD="python3"
fi

# Script location
SCRIPT_PATH="$(dirname "$0")/analyze_pdf_batch.py"

# Check if script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}Error: analyze_pdf_batch.py not found at $SCRIPT_PATH${NC}"
    exit 1
fi

# Show help if no arguments
if [ $# -eq 0 ]; then
    echo "Usage examples:"
    echo ""
    echo "  # Process all PDFs in a directory:"
    echo "  $0 /path/to/pdfs -o results.json"
    echo ""
    echo "  # Process with CSV output and statistics:"
    echo "  $0 /path/to/pdfs -o results.csv -f csv -s"
    echo ""
    echo "  # Process specific files with OCR:"
    echo "  $0 file1.pdf file2.pdf -o results.json --ocr"
    echo ""
    echo "  # Process with 8 parallel workers and verbose output:"
    echo "  $0 /path/to/pdfs -o results.json -w 8 -v"
    echo ""
    echo "  # Process recursively with custom pattern:"
    echo "  $0 /path/to/pdfs -o results.json -r -p '*.PDF'"
    echo ""
    echo "Run with -h for full help"
    echo ""
    exec $PYTHON_CMD "$SCRIPT_PATH" -h
fi

# Run the analyzer with all arguments
echo -e "${GREEN}Starting PDF batch analysis...${NC}"
$PYTHON_CMD "$SCRIPT_PATH" "$@"

# Check exit status
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Analysis completed successfully!${NC}"
else
    echo -e "${RED}Analysis failed. Check the error messages above.${NC}"
    exit 1
fi