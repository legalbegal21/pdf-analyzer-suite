#!/usr/bin/env python3
"""
PDF Analyzer Suite - Example Usage
==================================

This script demonstrates how to use each tool in the PDF Analyzer Suite.
"""

import sys
import os

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_analyzer import PDFAnalyzer
from pdf_batch_processor import PDFBatchProcessor
from pdf_text_extractor import PDFTextExtractor
from pdf_metadata_extractor import PDFMetadataExtractor
from pdf_structure_analyzer import PDFStructureAnalyzer
from pdf_image_extractor import PDFImageExtractor
from pdf_link_extractor import PDFLinkExtractor
from pdf_form_analyzer import PDFFormAnalyzer
from pdf_table_extractor import PDFTableExtractor
from pdf_page_analyzer import PDFPageAnalyzer
from pdf_font_analyzer import PDFFontAnalyzer
from pdf_security_analyzer import PDFSecurityAnalyzer
from pdf_reporter import PDFReporter
import json

def example_basic_analysis():
    """Example: Basic PDF analysis using the main PDFAnalyzer class"""
    print("=" * 60)
    print("EXAMPLE 1: Basic PDF Analysis")
    print("=" * 60)
    
    # Initialize the analyzer
    analyzer = PDFAnalyzer()
    
    # Analyze a PDF file
    pdf_path = "sample.pdf"  # Replace with your PDF path
    
    try:
        # Perform analysis
        results = analyzer.analyze(pdf_path, modules=['all'])
        
        # Print basic information
        print(f"File: {results['file_info']['name']}")
        print(f"Size: {results['file_info']['size_mb']:.2f} MB")
        print(f"Pages: {results['file_info']['page_count']}")
        print(f"Producer: {results['metadata'].get('producer', 'Unknown')}")
        
        # Save results to JSON
        with open('analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("\nFull results saved to 'analysis_results.json'")
        
    except Exception as e:
        print(f"Error analyzing PDF: {e}")

def example_text_extraction():
    """Example: Extract text from specific pages"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Text Extraction")
    print("=" * 60)
    
    extractor = PDFTextExtractor()
    
    # Extract text from all pages
    all_text = extractor.extract_text("sample.pdf")
    print(f"Total text length: {len(all_text)} characters")
    print(f"First 200 characters: {all_text[:200]}...")
    
    # Extract text from specific pages
    page_text = extractor.extract_text("sample.pdf", page_numbers=[1, 2])
    print(f"\nText from pages 1-2: {len(page_text)} characters")
    
    # Extract text from a page range
    range_text = extractor.extract_text("sample.pdf", start_page=1, end_page=3)
    print(f"Text from pages 1-3: {len(range_text)} characters")

def example_metadata_extraction():
    """Example: Extract and analyze PDF metadata"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Metadata Extraction")
    print("=" * 60)
    
    extractor = PDFMetadataExtractor()
    metadata = extractor.extract_metadata("sample.pdf")
    
    print("PDF Metadata:")
    for key, value in metadata.items():
        if value:
            print(f"  {key}: {value}")

def example_structure_analysis():
    """Example: Analyze PDF structure"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Structure Analysis")
    print("=" * 60)
    
    analyzer = PDFStructureAnalyzer()
    structure = analyzer.analyze_structure("sample.pdf")
    
    print(f"Total pages: {structure['total_pages']}")
    print(f"Has table of contents: {structure['has_toc']}")
    print(f"Number of bookmarks: {len(structure['bookmarks'])}")
    
    if structure['bookmarks']:
        print("\nFirst 5 bookmarks:")
        for i, bookmark in enumerate(structure['bookmarks'][:5]):
            print(f"  - {bookmark['title']} (page {bookmark['page']})")

def example_image_extraction():
    """Example: Extract images from PDF"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Image Extraction")
    print("=" * 60)
    
    extractor = PDFImageExtractor()
    
    # Create output directory
    os.makedirs("extracted_images", exist_ok=True)
    
    # Extract all images
    images = extractor.extract_images("sample.pdf", output_dir="extracted_images")
    
    print(f"Extracted {len(images)} images:")
    for img in images[:5]:  # Show first 5
        print(f"  - Page {img['page']}: {img['filename']} ({img['width']}x{img['height']})")

def example_form_analysis():
    """Example: Analyze PDF forms"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Form Analysis")
    print("=" * 60)
    
    analyzer = PDFFormAnalyzer()
    form_data = analyzer.analyze_forms("sample.pdf")
    
    if form_data['is_form']:
        print(f"This PDF contains {form_data['field_count']} form fields")
        print("\nField types:")
        for field_type, count in form_data['field_types'].items():
            print(f"  - {field_type}: {count}")
        
        print("\nFirst 5 fields:")
        for field in form_data['fields'][:5]:
            print(f"  - {field['name']} ({field['type']})")
    else:
        print("This PDF does not contain form fields")

def example_table_extraction():
    """Example: Extract tables from PDF"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Table Extraction")
    print("=" * 60)
    
    extractor = PDFTableExtractor()
    tables = extractor.extract_tables("sample.pdf")
    
    print(f"Found {len(tables)} tables")
    
    for i, table in enumerate(tables[:3]):  # Show first 3 tables
        print(f"\nTable {i+1} (Page {table['page']}):")
        print(f"  Rows: {table['rows']}, Columns: {table['columns']}")
        if table['data']:
            print("  First row:", table['data'][0])

def example_security_analysis():
    """Example: Analyze PDF security"""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Security Analysis")
    print("=" * 60)
    
    analyzer = PDFSecurityAnalyzer()
    security = analyzer.analyze_security("sample.pdf")
    
    print(f"Encrypted: {security['is_encrypted']}")
    print(f"Password protected: {security['has_password']}")
    print(f"Encryption level: {security['encryption_level']}")
    
    print("\nPermissions:")
    for perm, allowed in security['permissions'].items():
        status = "Allowed" if allowed else "Restricted"
        print(f"  - {perm}: {status}")

def example_batch_processing():
    """Example: Process multiple PDFs"""
    print("\n" + "=" * 60)
    print("EXAMPLE 9: Batch Processing")
    print("=" * 60)
    
    processor = PDFBatchProcessor()
    
    # Process all PDFs in a directory
    pdf_directory = "/path/to/pdfs"  # Replace with your directory
    output_dir = "batch_results"
    
    try:
        results = processor.process_directory(
            pdf_directory,
            output_dir=output_dir,
            modules=['metadata', 'text', 'structure']
        )
        
        print(f"Processed {results['processed_count']} PDFs")
        print(f"Successful: {results['success_count']}")
        print(f"Failed: {results['error_count']}")
        
        # Generate summary report
        processor.generate_summary_report(results, output_dir)
        print(f"\nSummary report saved to {output_dir}/summary_report.json")
        
    except Exception as e:
        print(f"Error in batch processing: {e}")

def example_custom_analysis():
    """Example: Custom analysis with specific modules"""
    print("\n" + "=" * 60)
    print("EXAMPLE 10: Custom Analysis")
    print("=" * 60)
    
    # Initialize analyzer with specific modules only
    analyzer = PDFAnalyzer()
    
    # Analyze with only specific modules
    modules = ['metadata', 'structure', 'fonts', 'security']
    results = analyzer.analyze("sample.pdf", modules=modules)
    
    print("Custom analysis results:")
    print(f"- Font count: {len(results.get('fonts', {}).get('fonts', []))}")
    print(f"- Security level: {results.get('security', {}).get('encryption_level', 'None')}")
    
    # Generate HTML report
    reporter = PDFReporter()
    reporter.generate_html_report(results, "custom_analysis_report.html")
    print("\nHTML report saved to 'custom_analysis_report.html'")

def example_advanced_filtering():
    """Example: Advanced text extraction with filtering"""
    print("\n" + "=" * 60)
    print("EXAMPLE 11: Advanced Text Filtering")
    print("=" * 60)
    
    extractor = PDFTextExtractor()
    
    # Extract text with custom options
    text = extractor.extract_text(
        "sample.pdf",
        preserve_layout=True,  # Maintain original layout
        remove_headers_footers=True,  # Remove headers/footers
        min_length=10  # Only extract text blocks with 10+ characters
    )
    
    print(f"Filtered text length: {len(text)} characters")

def main():
    """Run all examples"""
    print("PDF Analyzer Suite - Examples")
    print("=============================\n")
    
    # Note: Comment out examples that require actual PDF files
    # These are demonstrations of how to use the tools
    
    print("This script demonstrates how to use the PDF Analyzer Suite.")
    print("Replace 'sample.pdf' with your actual PDF file path.\n")
    
    # Uncomment the examples you want to run:
    
    # example_basic_analysis()
    # example_text_extraction()
    # example_metadata_extraction()
    # example_structure_analysis()
    # example_image_extraction()
    # example_form_analysis()
    # example_table_extraction()
    # example_security_analysis()
    # example_batch_processing()
    # example_custom_analysis()
    # example_advanced_filtering()
    
    print("\nFor more examples, see the individual example functions in this file.")
    print("Each function demonstrates a specific feature of the PDF Analyzer Suite.")

if __name__ == "__main__":
    main()