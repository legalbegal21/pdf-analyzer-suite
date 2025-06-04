#!/bin/bash
# PDF Structured Data Extraction Wrapper
# Part of the PDF Analyzer Suite
# Extracts structured data from PDFs using Claude AI

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Help function
show_help() {
    cat << EOF
PDF Structured Data Extractor - Extract structured data from PDFs using AI

Usage: $0 [OPTIONS] <input_path>

OPTIONS:
    -o, --output DIR     Output directory for extracted data (default: ./extracted_data)
    -s, --schema TYPE    Schema type: immigration, legal, client (default: client)
    -k, --api-key KEY    Anthropic API key (uses ANTHROPIC_API_KEY env var if not set)
    -m, --model MODEL    Claude model to use (default: claude-3-haiku-20240307)
    -v, --verbose        Enable verbose output
    -h, --help           Show this help message

EXAMPLES:
    # Extract data from a single PDF
    $0 document.pdf

    # Process a directory of immigration documents
    $0 --schema immigration --output ./immigration_data ./immigration_docs/

    # Extract from legal memos with custom output
    $0 -s legal -o ./memo_extracts ./legal_memos/

    # Use with specific API key and model
    $0 --api-key sk-ant-... --model claude-3-opus-20240229 ./pdfs/

SCHEMA TYPES:
    client      - General client case information (default)
    immigration - Immigration documents (I-130, I-589, etc.)
    legal       - Legal memos and briefs

OUTPUT:
    Creates JSON files with extracted structured data in the output directory.
    Each PDF generates a corresponding _extracted.json file.
    A summary report is created as extraction_summary.json.

EOF
}

# Default values
OUTPUT_DIR="./extracted_data"
SCHEMA_TYPE="client"
API_KEY=""
MODEL=""
VERBOSE=""
INPUT_PATH=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -s|--schema)
            SCHEMA_TYPE="$2"
            shift 2
            ;;
        -k|--api-key)
            API_KEY="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            INPUT_PATH="$1"
            shift
            ;;
    esac
done

# Check if input path provided
if [ -z "$INPUT_PATH" ]; then
    echo -e "${RED}Error: No input path provided${NC}"
    echo "Use -h or --help for usage information"
    exit 1
fi

# Check if input exists
if [ ! -e "$INPUT_PATH" ]; then
    echo -e "${RED}Error: Input path does not exist: $INPUT_PATH${NC}"
    exit 1
fi

# Build Python command
PYTHON_CMD="python3 ${SCRIPT_DIR}/pdf_structured_extractor.py"

# Add input path
if [ -f "$INPUT_PATH" ]; then
    # Single file - use parent directory as input and specific output
    PARENT_DIR=$(dirname "$INPUT_PATH")
    PYTHON_CMD="$PYTHON_CMD --input \"$PARENT_DIR\""
    echo -e "${YELLOW}Processing single file: $INPUT_PATH${NC}"
else
    # Directory
    PYTHON_CMD="$PYTHON_CMD --input \"$INPUT_PATH\""
    echo -e "${YELLOW}Processing directory: $INPUT_PATH${NC}"
fi

# Add other options
PYTHON_CMD="$PYTHON_CMD --output \"$OUTPUT_DIR\" --schema $SCHEMA_TYPE"

if [ -n "$API_KEY" ]; then
    PYTHON_CMD="$PYTHON_CMD --api-key \"$API_KEY\""
fi

if [ -n "$MODEL" ]; then
    PYTHON_CMD="$PYTHON_CMD --model \"$MODEL\""
fi

if [ -n "$VERBOSE" ]; then
    PYTHON_CMD="$PYTHON_CMD $VERBOSE"
fi

# Show configuration
echo -e "${GREEN}Configuration:${NC}"
echo "  Schema Type: $SCHEMA_TYPE"
echo "  Output Directory: $OUTPUT_DIR"
if [ -n "$MODEL" ]; then
    echo "  Model: $MODEL"
fi
echo ""

# Check for API key
if [ -z "$API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}Warning: No Anthropic API key found.${NC}"
    echo "Structured extraction will use basic pattern matching only."
    echo "For full AI-powered extraction, set ANTHROPIC_API_KEY environment variable"
    echo "or use --api-key option."
    echo ""
fi

# Execute extraction
echo -e "${GREEN}Starting extraction...${NC}"
eval $PYTHON_CMD

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}Extraction completed successfully!${NC}"
    echo "Results saved to: $OUTPUT_DIR"
    
    # Show summary if exists
    if [ -f "$OUTPUT_DIR/extraction_summary.json" ]; then
        echo ""
        echo "Summary:"
        python3 -c "
import json
with open('$OUTPUT_DIR/extraction_summary.json', 'r') as f:
    summary = json.load(f)
    print(f'  Total files: {summary[\"total_files\"]}')
    print(f'  Processed: {len(summary[\"processed_files\"])}')
    print(f'  Failed: {len(summary[\"failed_files\"])}')
"
    fi
else
    echo -e "${RED}Extraction failed!${NC}"
    exit 1
fi