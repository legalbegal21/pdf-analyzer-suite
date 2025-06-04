#!/usr/bin/env python3
"""
PDF Analyzer Suite - Common Usage Patterns
=========================================

This file shows common patterns and best practices for using the PDF Analyzer Suite.
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_analyzer import PDFAnalyzer
from pdf_batch_processor import PDFBatchProcessor
from pdf_text_extractor import PDFTextExtractor
from pdf_reporter import PDFReporter

# Pattern 1: Analyze and Generate Report
def pattern_analyze_and_report(pdf_path):
    """Analyze a PDF and generate both JSON and HTML reports"""
    print("Pattern 1: Analyze and Generate Report")
    print("-" * 40)
    
    analyzer = PDFAnalyzer()
    reporter = PDFReporter()
    
    # Analyze
    results = analyzer.analyze(pdf_path)
    
    # Generate reports
    base_name = os.path.splitext(pdf_path)[0]
    
    # JSON report
    json_file = f"{base_name}_report.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # HTML report
    html_file = f"{base_name}_report.html"
    reporter.generate_html_report(results, html_file)
    
    print(f"✓ JSON report: {json_file}")
    print(f"✓ HTML report: {html_file}")
    print()

# Pattern 2: Extract Text with Custom Filtering
def pattern_filtered_text_extraction(pdf_path, search_term=None):
    """Extract and filter text from PDF"""
    print("Pattern 2: Filtered Text Extraction")
    print("-" * 40)
    
    extractor = PDFTextExtractor()
    
    # Extract all text
    full_text = extractor.extract_text(pdf_path)
    
    # Filter by search term if provided
    if search_term:
        lines = full_text.split('\n')
        matching_lines = [line for line in lines if search_term.lower() in line.lower()]
        
        print(f"Found {len(matching_lines)} lines containing '{search_term}':")
        for i, line in enumerate(matching_lines[:5], 1):
            print(f"  {i}. {line.strip()}")
        
        if len(matching_lines) > 5:
            print(f"  ... and {len(matching_lines) - 5} more")
    else:
        words = len(full_text.split())
        print(f"Extracted {words} words from {pdf_path}")
    
    print()

# Pattern 3: Batch Process with Error Handling
def pattern_safe_batch_processing(input_dir, output_dir):
    """Safely process multiple PDFs with error handling"""
    print("Pattern 3: Safe Batch Processing")
    print("-" * 40)
    
    processor = PDFBatchProcessor()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Log file for errors
    log_file = os.path.join(output_dir, "processing_log.txt")
    
    success_count = 0
    error_count = 0
    
    with open(log_file, 'w') as log:
        log.write(f"Batch Processing Log - {datetime.now()}\n")
        log.write("=" * 50 + "\n\n")
        
        # Process each PDF
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(input_dir, filename)
                
                try:
                    # Process individual file
                    analyzer = PDFAnalyzer()
                    results = analyzer.analyze(pdf_path, modules=['metadata', 'text', 'structure'])
                    
                    # Save results
                    output_file = os.path.join(output_dir, f"{filename}_analysis.json")
                    with open(output_file, 'w') as f:
                        json.dump(results, f, indent=2)
                    
                    success_count += 1
                    log.write(f"✓ SUCCESS: {filename}\n")
                    
                except Exception as e:
                    error_count += 1
                    log.write(f"✗ ERROR: {filename} - {str(e)}\n")
                    print(f"  Error processing {filename}: {e}")
    
    print(f"✓ Processed: {success_count} successful, {error_count} errors")
    print(f"✓ Log file: {log_file}")
    print()

# Pattern 4: Conditional Processing Based on Content
def pattern_conditional_processing(pdf_path):
    """Process PDF differently based on its content"""
    print("Pattern 4: Conditional Processing")
    print("-" * 40)
    
    analyzer = PDFAnalyzer()
    
    # Quick analysis to determine PDF type
    quick_results = analyzer.analyze(pdf_path, modules=['metadata', 'forms', 'structure'])
    
    # Determine processing strategy
    if quick_results['forms']['is_form']:
        print("✓ Detected: Form PDF")
        # Full analysis for forms
        full_results = analyzer.analyze(pdf_path, modules=['all'])
        print(f"  - Form fields: {full_results['forms']['field_count']}")
        
    elif quick_results['structure']['bookmark_count'] > 10:
        print("✓ Detected: Structured Document (many bookmarks)")
        # Focus on structure and text
        full_results = analyzer.analyze(pdf_path, modules=['structure', 'text', 'links'])
        print(f"  - Bookmarks: {len(full_results['structure']['bookmarks'])}")
        
    elif quick_results['file_info']['page_count'] > 50:
        print("✓ Detected: Large Document")
        # Selective processing for large files
        full_results = analyzer.analyze(pdf_path, modules=['metadata', 'structure'])
        print(f"  - Pages: {full_results['file_info']['page_count']}")
        
    else:
        print("✓ Detected: Standard Document")
        # Standard processing
        full_results = analyzer.analyze(pdf_path, modules=['metadata', 'text', 'images'])
    
    print()
    return full_results

# Pattern 5: Memory-Efficient Processing
def pattern_memory_efficient(pdf_path):
    """Process large PDFs efficiently"""
    print("Pattern 5: Memory-Efficient Processing")
    print("-" * 40)
    
    extractor = PDFTextExtractor()
    
    # Process in chunks of 10 pages
    chunk_size = 10
    total_words = 0
    
    # First, get page count
    analyzer = PDFAnalyzer()
    info = analyzer.analyze(pdf_path, modules=['metadata'])
    page_count = info['file_info']['page_count']
    
    print(f"Processing {page_count} pages in chunks of {chunk_size}...")
    
    for start_page in range(1, page_count + 1, chunk_size):
        end_page = min(start_page + chunk_size - 1, page_count)
        
        # Extract text for chunk
        chunk_text = extractor.extract_text(
            pdf_path,
            start_page=start_page,
            end_page=end_page
        )
        
        words_in_chunk = len(chunk_text.split())
        total_words += words_in_chunk
        
        print(f"  Pages {start_page}-{end_page}: {words_in_chunk} words")
    
    print(f"✓ Total words: {total_words}")
    print()

# Pattern 6: Create Summary Dashboard
def pattern_create_dashboard(pdf_list):
    """Create a summary dashboard for multiple PDFs"""
    print("Pattern 6: Create Summary Dashboard")
    print("-" * 40)
    
    dashboard_data = {
        'generated': datetime.now().isoformat(),
        'total_files': len(pdf_list),
        'total_pages': 0,
        'total_size_mb': 0,
        'files': []
    }
    
    analyzer = PDFAnalyzer()
    
    for pdf_path in pdf_list:
        if os.path.exists(pdf_path):
            try:
                # Quick analysis
                results = analyzer.analyze(pdf_path, modules=['metadata', 'structure'])
                
                file_summary = {
                    'name': os.path.basename(pdf_path),
                    'pages': results['file_info']['page_count'],
                    'size_mb': results['file_info']['size_mb'],
                    'encrypted': results['metadata'].get('encrypted', False),
                    'has_forms': results.get('forms', {}).get('is_form', False)
                }
                
                dashboard_data['files'].append(file_summary)
                dashboard_data['total_pages'] += file_summary['pages']
                dashboard_data['total_size_mb'] += file_summary['size_mb']
                
            except Exception as e:
                print(f"  Error processing {pdf_path}: {e}")
    
    # Save dashboard
    with open('pdf_dashboard.json', 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"✓ Dashboard created with {len(dashboard_data['files'])} files")
    print(f"✓ Total pages: {dashboard_data['total_pages']}")
    print(f"✓ Total size: {dashboard_data['total_size_mb']:.2f} MB")
    print()

# Pattern 7: Extract Specific Data Types
def pattern_extract_specific_data(pdf_path):
    """Extract only specific types of data from PDF"""
    print("Pattern 7: Extract Specific Data")
    print("-" * 40)
    
    from pdf_image_extractor import PDFImageExtractor
    from pdf_link_extractor import PDFLinkExtractor
    from pdf_table_extractor import PDFTableExtractor
    
    # Extract images
    image_extractor = PDFImageExtractor()
    images = image_extractor.extract_images(pdf_path, output_dir="extracted_images")
    print(f"✓ Extracted {len(images)} images")
    
    # Extract links
    link_extractor = PDFLinkExtractor()
    links = link_extractor.extract_links(pdf_path)
    print(f"✓ Found {links['external_count']} external links")
    
    # Extract tables
    table_extractor = PDFTableExtractor()
    tables = table_extractor.extract_tables(pdf_path)
    print(f"✓ Found {len(tables)} tables")
    
    # Save summary
    summary = {
        'images': len(images),
        'external_links': [link['target'] for link in links['links'] if link['type'] == 'external'],
        'tables': len(tables)
    }
    
    with open('extracted_data_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print()

def main():
    """Demonstrate all patterns"""
    print("PDF Analyzer Suite - Common Usage Patterns")
    print("=========================================\n")
    
    # Example PDF (replace with actual path)
    sample_pdf = "sample.pdf"
    
    if len(sys.argv) > 1:
        sample_pdf = sys.argv[1]
    
    print(f"Note: These are code patterns. Replace '{sample_pdf}' with your actual PDF path.\n")
    
    # Show all patterns (comment out ones you don't want to run)
    
    # pattern_analyze_and_report(sample_pdf)
    # pattern_filtered_text_extraction(sample_pdf, "search_term")
    # pattern_safe_batch_processing("./pdfs", "./results")
    # pattern_conditional_processing(sample_pdf)
    # pattern_memory_efficient(sample_pdf)
    # pattern_create_dashboard([sample_pdf])
    # pattern_extract_specific_data(sample_pdf)
    
    print("Review the code above to see common usage patterns.")
    print("Uncomment the patterns you want to run.")

if __name__ == "__main__":
    main()