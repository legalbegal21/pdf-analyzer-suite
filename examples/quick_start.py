#!/usr/bin/env python3
"""
PDF Analyzer Suite - Quick Start Example
=======================================

This is the simplest example to get you started with PDF analysis.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_analyzer import PDFAnalyzer

def analyze_pdf(pdf_path):
    """Analyze a PDF and display key information"""
    
    print(f"Analyzing: {pdf_path}")
    print("-" * 50)
    
    try:
        # Create analyzer instance
        analyzer = PDFAnalyzer()
        
        # Analyze the PDF
        results = analyzer.analyze(pdf_path)
        
        # Display key information
        print(f"File: {results['file_info']['name']}")
        print(f"Size: {results['file_info']['size_mb']:.2f} MB")
        print(f"Pages: {results['file_info']['page_count']}")
        print(f"PDF Version: {results['file_info']['pdf_version']}")
        print()
        
        # Metadata
        print("Metadata:")
        print(f"  Title: {results['metadata'].get('title', 'N/A')}")
        print(f"  Author: {results['metadata'].get('author', 'N/A')}")
        print(f"  Created: {results['metadata'].get('creation_date', 'N/A')}")
        print(f"  Modified: {results['metadata'].get('mod_date', 'N/A')}")
        print()
        
        # Content summary
        print("Content Summary:")
        print(f"  Text: {results['text']['total_words']} words")
        print(f"  Images: {results['images']['count']}")
        print(f"  Tables: {results['tables']['count']}")
        print(f"  Links: {results['links']['internal_count']} internal, "
              f"{results['links']['external_count']} external")
        
        # Forms
        if results['forms']['is_form']:
            print(f"  Form Fields: {results['forms']['field_count']}")
        
        # Security
        if results['security']['is_encrypted']:
            print(f"  Security: Encrypted ({results['security']['encryption_level']})")
        
        print()
        
        # Save full results
        output_file = pdf_path.replace('.pdf', '_analysis.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"Full analysis saved to: {output_file}")
        
        return results
        
    except FileNotFoundError:
        print(f"Error: File '{pdf_path}' not found")
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
    
    return None

def main():
    """Main function"""
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("PDF Analyzer Suite - Quick Start")
        print("================================")
        print()
        print("Usage: python3 quick_start.py <pdf_file>")
        print()
        print("Example: python3 quick_start.py document.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Analyze the PDF
    results = analyze_pdf(pdf_path)
    
    if results:
        print("\nAnalysis complete!")

if __name__ == "__main__":
    main()