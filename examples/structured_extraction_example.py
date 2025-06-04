#!/usr/bin/env python3
"""
Example of using the PDF Structured Extractor as a module

This example demonstrates how to use the PDFStructuredExtractor class
to extract structured data from PDF files programmatically.
"""

import os
import sys
import json

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_structured_extractor import PDFStructuredExtractor

def main():
    # Example 1: Basic usage with default settings
    print("=== Example 1: Basic Extraction ===")
    
    # Initialize extractor (will use ANTHROPIC_API_KEY from environment)
    try:
        extractor = PDFStructuredExtractor()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set ANTHROPIC_API_KEY environment variable")
        return
    
    # Process a single PDF file
    pdf_path = "sample_document.pdf"  # Replace with actual PDF path
    
    if os.path.exists(pdf_path):
        result = extractor.process_pdf_file(pdf_path, schema_type="client")
        print(json.dumps(result, indent=2))
    else:
        print(f"Sample PDF not found: {pdf_path}")
    
    # Example 2: Custom schema extraction
    print("\n=== Example 2: Custom Schema ===")
    
    # Define a custom schema for a specific use case
    custom_schema = {
        "type": "object",
        "properties": {
            "case_summary": {
                "type": "object",
                "properties": {
                    "case_name": {"type": "string"},
                    "filing_date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "jurisdiction": {"type": "string"},
                    "case_type": {"type": "string"}
                }
            },
            "parties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "role": {"type": "string", "description": "e.g., plaintiff, defendant, petitioner"},
                        "representation": {"type": "string"}
                    }
                }
            },
            "key_dates": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                        "event": {"type": "string"}
                    }
                }
            }
        }
    }
    
    # Extract text and use custom schema
    if os.path.exists(pdf_path):
        document_text = extractor.extract_text_from_pdf(pdf_path)
        custom_result = extractor.extract_structured_data(
            document_text, 
            custom_schema, 
            document_type="legal case file"
        )
        print("Custom extraction result:")
        print(json.dumps(custom_result, indent=2))
    
    # Example 3: Batch processing
    print("\n=== Example 3: Batch Processing ===")
    
    # Process all PDFs in a directory
    input_dir = "./sample_pdfs"  # Replace with actual directory
    output_dir = "./extraction_results"
    
    if os.path.exists(input_dir):
        extractor.process_directory(input_dir, output_dir, schema_type="client")
        print(f"Batch processing complete. Results saved to {output_dir}")
    else:
        print(f"Sample directory not found: {input_dir}")
    
    # Example 4: Using different schemas
    print("\n=== Example 4: Different Schema Types ===")
    
    schemas = ["immigration", "legal", "client"]
    
    for schema in schemas:
        print(f"\nTesting {schema} schema:")
        # This would process the same file with different schemas
        # Useful for determining which schema works best for a document
        if os.path.exists(pdf_path):
            result = extractor.process_pdf_file(pdf_path, schema_type=schema)
            print(f"Extracted {len(result.get('extraction_result', {}))} fields")

if __name__ == "__main__":
    main()