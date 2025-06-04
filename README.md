# PDF Analyzer Suite

A comprehensive collection of Python and shell scripts for analyzing PDF documents, extracting metadata, processing forms, and performing batch operations.

## Features

- **Single PDF Analysis**: Detailed analysis of individual PDF files including metadata, text content, images, and form fields
- **Batch Processing**: Process multiple PDFs in parallel with up to 8 workers for maximum performance
- **Form Detection**: Automatically detect and analyze PDF form fields
- **Text Extraction**: Extract and preview text content from PDFs
- **AI-Powered Structured Extraction**: Use Claude AI to extract structured data from legal documents, immigration forms, and client cases
- **Multiple Output Formats**: Export results as JSON or CSV
- **OCR Support**: Optional OCR processing for scanned documents
- **Schema-Based Extraction**: Pre-defined schemas for immigration documents, legal memos, and client case details

## Quick Start

```bash
# Analyze a single PDF
./analyze_pdf.sh document.pdf

# Batch analyze a directory
./run_pdf_batch_analyzer.sh /path/to/pdfs -o results.json

# Extract structured data with AI
./analyze_pdf_structured.sh --schema client document.pdf

# Interactive menu
./pdf_analyzer_launcher.sh
```

## Installation

This suite uses an existing Python virtual environment with PyMuPDF (fitz) and other PDF libraries. No additional installation required if you have the environment at `/home/lroc/unified-redaction-hub/venv/`.

For new installations:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# For AI-powered extraction, set your Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Tools Included

1. **simple_pdf_analyzer.py** - Core PDF analysis script
2. **analyze_pdf.sh** - Shell wrapper with environment activation
3. **analyze_pdf_batch.py** - Batch processing with parallel execution
4. **run_pdf_batch_analyzer.sh** - Batch processing wrapper
5. **pdf_structured_extractor.py** - AI-powered structured data extraction
6. **analyze_pdf_structured.sh** - Structured extraction wrapper
7. **pdf_analyzer_launcher.sh** - Interactive menu-driven interface

## Structured Data Extraction

The AI-powered structured extractor uses Claude to intelligently extract data from PDFs into structured JSON format. It supports three pre-defined schemas:

### Client Schema (Default)
Extracts client case information including:
- Personal details (name, DOB, country of origin, A-number)
- Case details (type, number, filing date, court)
- PD (Prosecutorial Discretion) factors
- Family ties and medical conditions
- Legal representatives

### Immigration Schema
Specialized for immigration documents (I-130, I-589, etc.):
- Document type and personal information
- Contact details and application info
- Family member information
- Receipt numbers and priority dates

### Legal Memo Schema
For legal memorandums and briefs:
- Title, date, author, and recipients
- Key facts and legal issues
- Analysis and conclusions
- Recommendations and cited sources

### Usage Examples

```bash
# Extract client case data
./analyze_pdf_structured.sh --schema client case_file.pdf

# Process immigration documents
./analyze_pdf_structured.sh -s immigration -o ./imm_data /path/to/i130s/

# Extract from legal memos with verbose output
./analyze_pdf_structured.sh --schema legal --verbose memo.pdf
```

## Documentation

- [PDF Analyzer Guide](PDF_ANALYZER_GUIDE.md) - Comprehensive documentation
- [Batch Analyzer README](PDF_BATCH_ANALYZER_README.md) - Batch processing details
- [Quick Reference](pdf_analyzer_cheatsheet.txt) - Command cheatsheet

## Performance

- Processes up to 44.63 files/second in batch mode
- Supports parallel processing with configurable workers (1-8)
- Efficient memory usage with streaming processing

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.