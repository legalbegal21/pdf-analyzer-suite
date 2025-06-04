# PDF Batch Analyzer

A high-performance Python script for analyzing multiple PDF files in parallel, extracting metadata, content statistics, and generating comprehensive reports in JSON or CSV format.

## Features

- **Parallel Processing**: Uses up to 8 workers for fast batch analysis
- **Comprehensive Analysis**: Extracts metadata, page count, text content, images, forms, and more
- **Multiple Output Formats**: JSON (detailed) or CSV (tabular) output
- **OCR Support**: Optional OCR for scanned PDFs with little text
- **Aggregate Statistics**: Generate summary statistics across all PDFs
- **Recursive Processing**: Process entire directory trees
- **Error Handling**: Graceful handling of corrupted or inaccessible PDFs
- **Virtual Environment Support**: Automatically uses the configured venv

## Installation

The script is already configured to use the virtual environment at:
`/home/lroc/unified-redaction-hub/venv/`

No additional installation needed if using the wrapper script.

## Usage

### Basic Usage

```bash
# Process all PDFs in a directory
./run_pdf_batch_analyzer.sh /path/to/pdfs -o results.json

# Process with CSV output and statistics
./run_pdf_batch_analyzer.sh /path/to/pdfs -o results.csv -f csv -s

# Process specific files
./run_pdf_batch_analyzer.sh file1.pdf file2.pdf -o analysis.json
```

### Advanced Options

```bash
# Use all 8 parallel workers with verbose output
./run_pdf_batch_analyzer.sh /path/to/pdfs -o results.json -w 8 -v

# Process recursively with OCR enabled
./run_pdf_batch_analyzer.sh /path/to/pdfs -o results.json -r --ocr -s

# Custom file pattern (case-insensitive)
./run_pdf_batch_analyzer.sh /path/to/pdfs -o results.json -p '*.PDF' -r

# Save logs to file
./run_pdf_batch_analyzer.sh /path/to/pdfs -o results.json --log analysis.log
```

## Command Line Options

- `input`: Directory path or PDF files to process (required)
- `-o, --output`: Output file path for results (required)
- `-f, --format`: Output format - json or csv (default: json)
- `-w, --workers`: Number of parallel workers (default: auto-detect, max 8)
- `-r, --recursive`: Process directories recursively
- `-p, --pattern`: File pattern to match (default: *.pdf)
- `-s, --stats`: Include aggregate statistics in output
- `--ocr`: Enable OCR for pages with little/no text
- `-v, --verbose`: Enable verbose output
- `--log`: Log file path

## Output Formats

### JSON Output Structure

```json
{
  "metadata": {
    "processing_date": "2024-01-20T10:30:00",
    "total_files": 50,
    "analyzer_version": "1.0.0",
    "workers_used": 8
  },
  "results": [
    {
      "file_name": "document.pdf",
      "file_path": "/full/path/to/document.pdf",
      "file_size_mb": 2.5,
      "page_count": 10,
      "total_text_length": 15000,
      "total_images": 5,
      "has_forms": true,
      "is_encrypted": false,
      "pdf_version": "1.7",
      "title": "Document Title",
      "author": "Author Name",
      "processing_time_seconds": 0.5
    }
  ],
  "statistics": {
    "summary": {
      "total_files": 50,
      "successful": 48,
      "failed": 2,
      "success_rate": 96.0
    },
    "file_statistics": {
      "total_size_mb": 125.5,
      "average_size_mb": 2.6
    },
    "content_statistics": {
      "total_pages": 500,
      "average_pages": 10.4,
      "files_with_forms": 15,
      "files_with_images": 30
    }
  }
}
```

### CSV Output Structure

The CSV output includes these columns:
- file_name
- file_path
- file_size_mb
- page_count
- total_text_length
- total_images
- has_forms
- is_encrypted
- pdf_version
- title
- author
- creation_date
- error (if any)
- processing_time

Statistics are saved to a separate `.stats.json` file when using CSV format.

## Performance Tips

1. **Parallel Workers**: Use `-w 8` for maximum performance on systems with 8+ cores
2. **OCR**: Only enable OCR (`--ocr`) when necessary as it significantly increases processing time
3. **File Pattern**: Use specific patterns to avoid processing non-PDF files
4. **Output Format**: JSON provides more detailed information; CSV is better for spreadsheet analysis

## Testing

Run the test script to see examples and verify the installation:

```bash
./test_pdf_batch_analyzer.sh
```

## Troubleshooting

1. **"Virtual environment not found"**: The script will fall back to system Python
2. **"PyMuPDF not available"**: Install with `pip install PyMuPDF` or use the venv
3. **Permission errors**: Ensure you have read access to the PDF files
4. **Memory issues**: Reduce workers with `-w 4` for large PDF collections

## Examples

### Analyze Legal Documents
```bash
./run_pdf_batch_analyzer.sh /mnt/c/Users/ramon/OneDrive -o legal_docs.json -r -s -v
```

### Quick Analysis of Downloads
```bash
./run_pdf_batch_analyzer.sh ~/Downloads -o downloads.csv -f csv -s
```

### Deep Analysis with OCR
```bash
./run_pdf_batch_analyzer.sh /path/to/scanned/docs -o scanned_analysis.json --ocr -w 4 -v
```

## Integration with Other Tools

The JSON output can be easily parsed by other scripts:

```python
import json

with open('results.json', 'r') as f:
    data = json.load(f)
    
# Access statistics
print(f"Total pages: {data['statistics']['content_statistics']['total_pages']}")

# Find large files
large_files = [r for r in data['results'] if r['file_size_mb'] > 10]
```

## Version History

- v1.0.0: Initial release with parallel processing, OCR support, and comprehensive analysis