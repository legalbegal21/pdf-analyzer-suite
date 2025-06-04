#!/bin/bash

# PDF Analyzer Launcher - Easy access to all PDF analysis tools
# Created: $(date)

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Show main menu
show_menu() {
    echo -e "${BLUE}=== PDF Document Analyzer Suite ===${NC}"
    echo
    echo "1) Analyze single PDF"
    echo "2) Batch analyze PDFs in directory"
    echo "3) Extract structured data (AI-powered)"
    echo "4) Fill PDF forms"
    echo "5) View quick reference"
    echo "6) View full documentation"
    echo "7) Test analyzer on sample PDFs"
    echo "8) Exit"
    echo
    echo -n "Select option [1-8]: "
}

# Main loop
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1)
            echo -e "\n${GREEN}Single PDF Analyzer${NC}"
            echo -n "Enter PDF path: "
            read -r pdf_path
            echo -n "Extract text? [y/N]: "
            read -r extract_text
            
            if [[ "$extract_text" =~ ^[Yy]$ ]]; then
                /home/lroc/analyze_pdf.sh "$pdf_path" --text
            else
                /home/lroc/analyze_pdf.sh "$pdf_path"
            fi
            echo -e "\n${YELLOW}Press Enter to continue...${NC}"
            read -r
            ;;
            
        2)
            echo -e "\n${GREEN}Batch PDF Analyzer${NC}"
            echo -n "Enter directory path: "
            read -r dir_path
            echo -n "Output file (default: results.json): "
            read -r output_file
            output_file=${output_file:-results.json}
            echo -n "Output format [json/csv]: "
            read -r format
            format=${format:-json}
            
            /home/lroc/run_pdf_batch_analyzer.sh "$dir_path" -o "$output_file" -f "$format" -s -v
            echo -e "\n${YELLOW}Results saved to: $output_file${NC}"
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read -r
            ;;
            
        3)
            echo -e "\n${GREEN}Structured Data Extractor (AI-Powered)${NC}"
            echo "Extract structured data from PDFs using Claude AI"
            echo
            echo "Schema options:"
            echo "  1) Client case information (default)"
            echo "  2) Immigration documents"
            echo "  3) Legal memos"
            echo
            echo -n "Select schema [1-3]: "
            read -r schema_choice
            
            case $schema_choice in
                2) schema="immigration" ;;
                3) schema="legal" ;;
                *) schema="client" ;;
            esac
            
            echo -n "Enter PDF path or directory: "
            read -r pdf_path
            echo -n "Output directory (default: ./extracted_data): "
            read -r output_dir
            output_dir=${output_dir:-./extracted_data}
            
            # Get the directory of this script
            SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
            
            # Run the structured extractor
            "$SCRIPT_DIR/analyze_pdf_structured.sh" -s "$schema" -o "$output_dir" "$pdf_path"
            
            echo -e "\n${YELLOW}Press Enter to continue...${NC}"
            read -r
            ;;
            
        4)
            echo -e "\n${GREEN}PDF Form Filler${NC}"
            echo -n "Enter PDF form path: "
            read -r pdf_path
            echo -n "Enter output path: "
            read -r output_path
            
            source /home/lroc/unified-redaction-hub/venv/bin/activate
            python /home/lroc/integrated_form_processor.py "$pdf_path" "$output_path"
            deactivate
            
            echo -e "\n${YELLOW}Press Enter to continue...${NC}"
            read -r
            ;;
            
        5)
            echo -e "\n${GREEN}Quick Reference${NC}"
            cat /home/lroc/pdf_analyzer_cheatsheet.txt | less
            ;;
            
        6)
            echo -e "\n${GREEN}Full Documentation${NC}"
            less /home/lroc/PDF_ANALYZER_GUIDE.md
            ;;
            
        7)
            echo -e "\n${GREEN}Testing Analyzer${NC}"
            echo "Running test on OneDrive PDFs..."
            /home/lroc/run_pdf_batch_analyzer.sh /mnt/c/Users/ramon/OneDrive -o test_results.json -f json -s
            echo -e "\n${YELLOW}Test results saved to: test_results.json${NC}"
            echo -e "${YELLOW}Press Enter to continue...${NC}"
            read -r
            ;;
            
        8)
            echo -e "${GREEN}Goodbye!${NC}"
            exit 0
            ;;
            
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            sleep 2
            ;;
    esac
    
    clear
done