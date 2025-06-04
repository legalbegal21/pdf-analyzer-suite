# PDF Analyzer Suite - Examples

This directory contains examples to help you get started with the PDF Analyzer Suite.

## Contents

### 1. `example_usage.py`
A comprehensive Python script demonstrating how to use each tool in the suite:
- Basic PDF analysis
- Text extraction (with advanced filtering)
- Metadata extraction
- Structure analysis
- Image extraction
- Form field analysis
- Table extraction
- Security analysis
- Batch processing
- Custom analysis with specific modules
- HTML report generation

**Usage:**
```bash
python3 example_usage.py
```

To run specific examples, uncomment the desired function calls in the `main()` function.

### 2. `sample_output.json`
A complete example of the JSON output produced by the analyzer. This shows:
- All available data fields
- Structure of the output
- Sample values for each type of data
- Processing information and metadata

This file serves as a reference for understanding the output format when building applications that consume the analyzer's results.

### 3. `batch_example.sh`
An interactive shell script with 8 different batch processing examples:

1. **Basic batch processing** - Process all PDFs with all modules
2. **Selective module processing** - Extract only specific data for speed
3. **HTML report generation** - Create visual reports
4. **Recent files only** - Process PDFs modified in last 7 days
5. **Parallel processing** - Use multiple workers for speed
6. **CSV export** - Create summary spreadsheet
7. **Process and archive** - Create timestamped archives
8. **Custom pipeline** - Multi-step conditional processing

**Usage:**
```bash
# Use default directories
./batch_example.sh

# Specify input directory
./batch_example.sh /path/to/pdfs

# Specify both input and output directories
./batch_example.sh /path/to/pdfs /path/to/results
```

## Quick Start

1. **Single PDF Analysis:**
   ```python
   from pdf_analyzer import PDFAnalyzer
   
   analyzer = PDFAnalyzer()
   results = analyzer.analyze("document.pdf")
   print(f"Pages: {results['file_info']['page_count']}")
   ```

2. **Extract Text Only:**
   ```python
   from pdf_text_extractor import PDFTextExtractor
   
   extractor = PDFTextExtractor()
   text = extractor.extract_text("document.pdf", page_numbers=[1, 2])
   print(text)
   ```

3. **Batch Process Directory:**
   ```bash
   python3 pdf_batch_processor.py --input-dir ./pdfs --output-dir ./results
   ```

## Common Use Cases

### Legal Document Processing
```python
# Extract text with layout preservation for legal documents
extractor = PDFTextExtractor()
text = extractor.extract_text(
    "legal_document.pdf",
    preserve_layout=True,
    remove_headers_footers=True
)

# Check for form fields
form_analyzer = PDFFormAnalyzer()
forms = form_analyzer.analyze_forms("legal_document.pdf")
if forms['is_form']:
    print(f"Found {forms['field_count']} form fields")
```

### Document Organization
```python
# Extract metadata for cataloging
metadata_extractor = PDFMetadataExtractor()
metadata = metadata_extractor.extract_metadata("document.pdf")

# Check document structure
structure_analyzer = PDFStructureAnalyzer()
structure = structure_analyzer.analyze_structure("document.pdf")
bookmarks = structure['bookmarks']
```

### Security Compliance
```python
# Check document security
security_analyzer = PDFSecurityAnalyzer()
security = security_analyzer.analyze_security("document.pdf")

if security['is_encrypted']:
    print("Document is encrypted")
if not security['permissions']['copy']:
    print("Text copying is restricted")
```

## Tips

1. **Performance**: For large batches, use parallel processing:
   ```bash
   python3 pdf_batch_processor.py --workers 4
   ```

2. **Memory Usage**: For very large PDFs, process specific pages:
   ```python
   text = extractor.extract_text("large.pdf", start_page=1, end_page=10)
   ```

3. **Error Handling**: Always wrap operations in try-except blocks:
   ```python
   try:
       results = analyzer.analyze("document.pdf")
   except Exception as e:
       print(f"Error: {e}")
   ```

4. **Custom Modules**: Process only what you need:
   ```python
   results = analyzer.analyze("document.pdf", modules=['metadata', 'text'])
   ```

## Output Formats

The suite supports multiple output formats:
- **JSON**: Structured data, easy to parse
- **HTML**: Visual reports with formatting
- **CSV**: Spreadsheet-compatible summaries
- **Text**: Plain text extracts

## Need Help?

- Check the main README.md for installation instructions
- Review function docstrings in the source code
- See sample_output.json for field descriptions
- Run scripts with `--help` for command-line options