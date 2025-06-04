#!/bin/bash

# Docker helper script for PDF Analyzer Suite
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Default values
INPUT_DIR="./input"
OUTPUT_DIR="./output"
IMAGE_NAME="pdf-analyzer-suite:latest"

# Show usage
usage() {
    echo -e "${BLUE}PDF Analyzer Suite - Docker Runner${NC}"
    echo
    echo "Usage: $0 [command] [options]"
    echo
    echo "Commands:"
    echo "  build           Build the Docker image"
    echo "  analyze         Analyze a single PDF file"
    echo "  batch           Run batch analysis on a directory"
    echo "  structured      Extract structured data using AI"
    echo "  shell           Start an interactive shell"
    echo "  clean           Remove Docker image and containers"
    echo
    echo "Options:"
    echo "  -i, --input     Input directory or file (default: ./input)"
    echo "  -o, --output    Output directory (default: ./output)"
    echo "  -h, --help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 build                          # Build Docker image"
    echo "  $0 analyze -i document.pdf        # Analyze single PDF"
    echo "  $0 batch -i /path/to/pdfs         # Batch process directory"
    echo "  $0 structured -i form.pdf         # Extract structured data"
    echo "  $0 shell                          # Interactive shell"
}

# Build Docker image
build_image() {
    echo -e "${BLUE}Building PDF Analyzer Suite Docker image...${NC}"
    docker build -t $IMAGE_NAME .
    echo -e "${GREEN}✓ Image built successfully${NC}"
}

# Ensure directories exist
ensure_dirs() {
    mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"
}

# Run single PDF analysis
analyze_pdf() {
    ensure_dirs
    
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Please specify a PDF file${NC}"
        exit 1
    fi
    
    # Copy file to input directory if it's not already there
    if [ -f "$1" ]; then
        cp "$1" "$INPUT_DIR/" 2>/dev/null || true
        filename=$(basename "$1")
    else
        filename="$1"
    fi
    
    echo -e "${BLUE}Analyzing $filename...${NC}"
    docker run --rm \
        -v "$(pwd)/$INPUT_DIR:/input:ro" \
        -v "$(pwd)/$OUTPUT_DIR:/output" \
        $IMAGE_NAME \
        python simple_pdf_analyzer.py "/input/$filename" --output-dir /output
    
    echo -e "${GREEN}✓ Analysis complete. Check $OUTPUT_DIR for results${NC}"
}

# Run batch analysis
batch_analyze() {
    ensure_dirs
    
    input_path="${1:-$INPUT_DIR}"
    
    echo -e "${BLUE}Running batch analysis on $input_path...${NC}"
    docker run --rm \
        -v "$(realpath "$input_path"):/input:ro" \
        -v "$(pwd)/$OUTPUT_DIR:/output" \
        $IMAGE_NAME \
        python analyze_pdf_batch.py /input -o /output/batch_results.json -s -v
    
    echo -e "${GREEN}✓ Batch analysis complete. Results in $OUTPUT_DIR/batch_results.json${NC}"
}

# Run structured extraction
structured_extract() {
    ensure_dirs
    
    if [ -z "$1" ]; then
        echo -e "${RED}Error: Please specify a PDF file${NC}"
        exit 1
    fi
    
    # Check for API key
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo -e "${YELLOW}Warning: ANTHROPIC_API_KEY not set. Using pattern-based extraction.${NC}"
    fi
    
    # Copy file to input directory
    if [ -f "$1" ]; then
        cp "$1" "$INPUT_DIR/" 2>/dev/null || true
        filename=$(basename "$1")
    else
        filename="$1"
    fi
    
    echo -e "${BLUE}Extracting structured data from $filename...${NC}"
    docker run --rm \
        -v "$(pwd)/$INPUT_DIR:/input:ro" \
        -v "$(pwd)/$OUTPUT_DIR:/output" \
        -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
        $IMAGE_NAME \
        python pdf_structured_extractor.py --input "/input/$filename" --output /output
    
    echo -e "${GREEN}✓ Extraction complete. Check $OUTPUT_DIR for results${NC}"
}

# Start interactive shell
start_shell() {
    ensure_dirs
    
    echo -e "${BLUE}Starting interactive shell...${NC}"
    echo -e "${YELLOW}Input files: /input, Output directory: /output${NC}"
    
    docker run --rm -it \
        -v "$(pwd)/$INPUT_DIR:/input:ro" \
        -v "$(pwd)/$OUTPUT_DIR:/output" \
        -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
        $IMAGE_NAME \
        /bin/bash
}

# Clean up Docker resources
clean_docker() {
    echo -e "${BLUE}Cleaning up Docker resources...${NC}"
    
    # Stop and remove containers
    docker stop pdf-analyzer pdf-analyzer-api 2>/dev/null || true
    docker rm pdf-analyzer pdf-analyzer-api 2>/dev/null || true
    
    # Remove image
    docker rmi $IMAGE_NAME 2>/dev/null || true
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Parse command line arguments
COMMAND=""
while [[ $# -gt 0 ]]; do
    case $1 in
        build|analyze|batch|structured|shell|clean)
            COMMAND="$1"
            shift
            ;;
        -i|--input)
            INPUT_ARG="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            if [ -z "$COMMAND" ]; then
                echo -e "${RED}Error: Unknown command '$1'${NC}"
                usage
                exit 1
            else
                # Assume it's an input file/directory for the command
                INPUT_ARG="$1"
                shift
            fi
            ;;
    esac
done

# Execute command
case $COMMAND in
    build)
        build_image
        ;;
    analyze)
        analyze_pdf "$INPUT_ARG"
        ;;
    batch)
        batch_analyze "$INPUT_ARG"
        ;;
    structured)
        structured_extract "$INPUT_ARG"
        ;;
    shell)
        start_shell
        ;;
    clean)
        clean_docker
        ;;
    *)
        echo -e "${RED}Error: No command specified${NC}"
        usage
        exit 1
        ;;
esac