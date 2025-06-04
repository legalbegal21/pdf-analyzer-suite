# PDF Analyzer Tools - Comprehensive Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation Requirements](#installation-requirements)
3. [Available Tools](#available-tools)
4. [Usage Examples](#usage-examples)
5. [Common Use Cases & Workflows](#common-use-cases--workflows)
6. [Troubleshooting Tips](#troubleshooting-tips)
7. [Performance Considerations](#performance-considerations)
8. [Integration with Existing Tools](#integration-with-existing-tools)

## Overview

The PDF Analyzer suite provides comprehensive tools for extracting, analyzing, and processing PDF documents with a focus on legal and immigration documentation. These tools leverage multiple technologies including PyMuPDF (fitz), OpenCV, Tesseract OCR, and Claude AI for intelligent data extraction.

### Key Features:
- **Structured Data Extraction**: Extract client information, case details, and form data
- **Computer Vision Integration**: Signature detection and form field recognition
- **OCR Capabilities**: Extract text from scanned documents
- **AI-Powered Analysis**: Use Claude to understand document context and extract relevant information
- **Batch Processing**: Handle multiple PDFs efficiently
- **Multiple Output Formats**: JSON, CSV, and structured text outputs

## Installation Requirements

### Use Existing Virtual Environment
**Primary Environment (RECOMMENDED):**
```bash
source /home/lroc/unified-redaction-hub/venv/bin/activate
```

This environment already has all required packages:
- PyMuPDF (fitz) - PDF manipulation
- OpenCV (cv2) - Computer vision
- pytesseract - OCR functionality
- anthropic - Claude AI integration
- PIL/Pillow - Image processing

### Alternative Environments:
- **Backup PDF Environment**: `/tmp/pdf_env/` (PyMuPDF working)
- **Form Processing**: `/home/lroc/pdf_form_env/` (cv2 available)

### System Requirements:
- Python 3.8+
- Tesseract OCR (already installed system-wide)
- mutool (from mupdf-tools package - already installed)

### Environment Variables:
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Available Tools

### 1. PDF Structured Extractor
**Location**: `/home/lroc/unified-redaction-hub/pdf_structured_extractor.py`

**Purpose**: Extract structured data from PDF files using Claude AI

**Features**:
- Supports multiple schema types (immigration, legal, client, custom)
- Batch processing capabilities
- Intelligent field extraction
- JSON output format

### 2. PDF Form Filler
**Location**: `/home/lroc/fill_i765_fillpdf.py`

**Purpose**: Pre-fill PDF forms with client data

**Features**:
- Fill specific form fields
- Support for I-765 and other USCIS forms
- Validation of field entries

### 3. PDF Text Extractor (System Tool)
**Location**: Available via pdftotext command

**Purpose**: Basic text extraction from PDFs

### 4. MuPDF Tools (System)
**Command**: `mutool`

**Purpose**: Low-level PDF manipulation and extraction

## Usage Examples

### 1. Extract Structured Data from PDFs

```bash
# Activate environment
source /home/lroc/unified-redaction-hub/venv/bin/activate

# Extract client data from a single PDF
python /home/lroc/unified-redaction-hub/pdf_structured_extractor.py \
    --input /path/to/client.pdf \
    --output ./extracted_data \
    --schema client

# Batch process immigration documents
python /home/lroc/unified-redaction-hub/pdf_structured_extractor.py \
    --input /path/to/immigration_docs/ \
    --output ./immigration_data \
    --schema immigration
```

### 2. Fill PDF Forms

```bash
# Fill I-765 form with client data
python /home/lroc/fill_i765_fillpdf.py \
    --template /path/to/i765_blank.pdf \
    --data client_data.json \
    --output filled_i765.pdf
```

### 3. Extract Text with System Tools

```bash
# Basic text extraction
pdftotext input.pdf output.txt

# Extract with layout preservation
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf pages1-5.txt
```

### 4. Use MuTool for Advanced Operations

```bash
# Extract all text
mutool draw -F txt input.pdf

# Extract images from PDF
mutool extract input.pdf

# Get PDF metadata
mutool info input.pdf
```

### 5. Run Extraction Pipeline

```bash
# Use the wrapper script for automated processing
cd /home/lroc/unified-redaction-hub
./run_extractor.sh /path/to/pdfs/
```

## Common Use Cases & Workflows

### Workflow 1: Client Intake Processing
```bash
# 1. Extract data from intake forms
python pdf_structured_extractor.py --input intake_forms/ --schema client

# 2. Validate extracted data
python validate_client_data.py extracted_data/

# 3. Generate summary report
python generate_intake_summary.py extracted_data/ > intake_summary.md
```

### Workflow 2: Immigration Case Analysis
```bash
# 1. Extract all case documents
python pdf_structured_extractor.py --input case_docs/ --schema immigration

# 2. Identify missing documents
python check_case_completeness.py extracted_data/

# 3. Generate case timeline
python create_case_timeline.py extracted_data/ > case_timeline.html
```

### Workflow 3: Batch Form Filling
```bash
# 1. Extract client data from multiple sources
for pdf in client_docs/*.pdf; do
    python pdf_structured_extractor.py --input "$pdf" --output temp_data/
done

# 2. Merge extracted data
python merge_client_data.py temp_data/ > merged_client_data.json

# 3. Fill multiple forms
python batch_form_filler.py --data merged_client_data.json --forms i765,i130,i485
```

### Workflow 4: Document Quality Check
```bash
# 1. Check for scanned vs native PDFs
for pdf in *.pdf; do
    if pdftotext "$pdf" - | grep -q '[a-zA-Z]'; then
        echo "$pdf: Native text"
    else
        echo "$pdf: Scanned - needs OCR"
    fi
done

# 2. Run OCR on scanned documents
python ocr_processor.py --input scanned_docs/ --output ocr_results/
```

## Troubleshooting Tips

### Common Issues and Solutions

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'fitz'
# Solution: Activate the correct environment
source /home/lroc/unified-redaction-hub/venv/bin/activate
```

#### 2. OCR Not Working
```bash
# Error: TesseractNotFoundError
# Solution: Verify Tesseract installation
which tesseract
# If not found:
sudo apt-get install tesseract-ocr
```

#### 3. API Key Issues
```bash
# Error: anthropic.AuthenticationError
# Solution: Set API key
export ANTHROPIC_API_KEY="your-key-here"
# Or add to ~/.bashrc for persistence
```

#### 4. Memory Issues with Large PDFs
```python
# Solution: Process in chunks
def process_large_pdf(pdf_path, chunk_size=10):
    doc = fitz.open(pdf_path)
    for i in range(0, len(doc), chunk_size):
        chunk = doc[i:i+chunk_size]
        process_chunk(chunk)
```

#### 5. Corrupted PDF Files
```bash
# Check PDF integrity
mutool clean -ggg corrupted.pdf fixed.pdf

# Or use qpdf
qpdf --check corrupted.pdf
```

### Debug Mode
Enable verbose logging:
```bash
export PDF_ANALYZER_DEBUG=1
python pdf_structured_extractor.py --verbose --input test.pdf
```

## Performance Considerations

### 1. Batch Size Optimization
- **Small files (<1MB)**: Process 50-100 at once
- **Medium files (1-10MB)**: Process 10-20 at once
- **Large files (>10MB)**: Process 1-5 at once

### 2. Memory Management
```python
# Use context managers to ensure cleanup
with fitz.open(pdf_path) as doc:
    # Process document
    pass  # Document automatically closed

# Clear cache periodically
import gc
gc.collect()
```

### 3. Parallel Processing
```bash
# Use GNU parallel for batch operations
find . -name "*.pdf" | parallel -j 4 python pdf_structured_extractor.py --input {} --output {.}_data.json
```

### 4. Caching Strategies
- Cache extracted text for repeated analysis
- Store OCR results to avoid re-processing
- Use SQLite for metadata storage

### 5. Performance Monitoring
```bash
# Time execution
time python pdf_structured_extractor.py --input large_dataset/

# Monitor memory usage
/usr/bin/time -v python pdf_structured_extractor.py --input test.pdf
```

## Integration with Existing Tools

### 1. Document Processing Pipeline
```bash
# Integrate with existing document_processing workflow
cd /home/lroc/document_processing
./document_import.sh  # Import from Windows
python pdf_analyzer.py  # Extract data
./03_Visualizations/run_all_visualizations.sh  # Visualize results
```

### 2. Redaction Tool Integration
```bash
# Extract sensitive data locations
python pdf_structured_extractor.py --schema legal --mark-sensitive

# Pass to redaction tool
python /home/lroc/redaction_venv/redact_tool.py --sensitive-data extracted_data/sensitive.json
```

### 3. Form Processing Integration
```bash
# Extract -> Validate -> Fill workflow
python pdf_structured_extractor.py --input client_docs/ --output data/
python validate_uscis_data.py data/
python fill_uscis_forms.py --data data/ --forms all
```

### 4. Google Docs Export
```bash
# Convert extracted data to Google Docs format
python pdf_structured_extractor.py --output-format gdoc --input case_file.pdf
```

### 5. API Integration
```python
# Use as a library in other tools
from pdf_structured_extractor import PDFStructuredExtractor

extractor = PDFStructuredExtractor()
data = extractor.extract_from_file("document.pdf", schema="immigration")
```

### 6. Command Line Aliases
Add to `~/.bashrc`:
```bash
alias pdf-extract='source /home/lroc/unified-redaction-hub/venv/bin/activate && python /home/lroc/unified-redaction-hub/pdf_structured_extractor.py'
alias pdf-info='mutool info'
alias pdf-text='pdftotext -layout'
```

## Quick Reference Commands

```bash
# Most common operations
pdf-extract --input file.pdf --schema client     # Extract client data
pdf-text file.pdf -                              # Quick text preview
mutool info file.pdf                             # Get PDF metadata
find . -name "*.pdf" -exec pdf-extract {} \;    # Batch extract all PDFs

# Check PDF for forms
mutool show file.pdf form                        # Show form fields
```

## Future Enhancements

1. **GUI Interface**: Web-based interface for non-technical users
2. **Machine Learning**: Train custom models for specific document types
3. **Cloud Integration**: Direct upload/download from cloud storage
4. **Real-time Processing**: Watch folder for automatic processing
5. **Advanced Analytics**: Statistical analysis of extracted data

## Support and Updates

- Check for updates: `git pull` in `/home/lroc/unified-redaction-hub/`
- Report issues: Create detailed logs with `--verbose` flag
- Performance logs: Located in `~/.pdf_analyzer/logs/`

---
*Last Updated: June 2025*
*Version: 1.0*