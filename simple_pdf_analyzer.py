#!/usr/bin/env python3
"""
Simple PDF Analyzer
Analyzes PDF files and provides comprehensive information about their structure and content.
Uses PyMuPDF (fitz) for PDF processing.
"""

import sys
import os
import argparse
from datetime import datetime
import fitz  # PyMuPDF

def format_bytes(bytes_size):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def format_date(date_str):
    """Format PDF date string to readable format."""
    if not date_str:
        return "Not available"
    
    # PDF dates are in format: D:YYYYMMDDHHmmSSOHH'mm
    try:
        if date_str.startswith("D:"):
            date_str = date_str[2:]
        # Extract just the date portion
        year = date_str[0:4]
        month = date_str[4:6]
        day = date_str[6:8]
        hour = date_str[8:10] if len(date_str) > 8 else "00"
        minute = date_str[10:12] if len(date_str) > 10 else "00"
        
        return f"{year}-{month}-{day} {hour}:{minute}"
    except:
        return date_str

def analyze_pdf(pdf_path, extract_text=False, text_limit=1000):
    """Analyze a PDF file and return comprehensive information."""
    
    print(f"\n{'='*60}")
    print(f"PDF ANALYSIS REPORT")
    print(f"{'='*60}")
    print(f"File: {pdf_path}")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        
        # Basic Information
        print("BASIC INFORMATION:")
        print(f"  Pages: {doc.page_count}")
        print(f"  File Size: {format_bytes(os.path.getsize(pdf_path))}")
        print(f"  PDF Version: {doc.metadata.get('format', 'Unknown')}")
        print(f"  Encrypted: {'Yes' if doc.is_encrypted else 'No'}")
        print(f"  Has Form Fields: {'Yes' if doc.is_form_pdf else 'No'}")
        
        # Metadata
        print("\nMETADATA:")
        metadata = doc.metadata
        print(f"  Title: {metadata.get('title', 'Not specified')}")
        print(f"  Author: {metadata.get('author', 'Not specified')}")
        print(f"  Subject: {metadata.get('subject', 'Not specified')}")
        print(f"  Keywords: {metadata.get('keywords', 'Not specified')}")
        print(f"  Creator: {metadata.get('creator', 'Not specified')}")
        print(f"  Producer: {metadata.get('producer', 'Not specified')}")
        print(f"  Creation Date: {format_date(metadata.get('creationDate', ''))}")
        print(f"  Modification Date: {format_date(metadata.get('modDate', ''))}")
        
        # Security Information
        print("\nSECURITY INFORMATION:")
        perms = doc.permissions
        if perms < 0:
            print("  No security restrictions")
        else:
            print(f"  Printing: {'Allowed' if perms & fitz.PDF_PERM_PRINT else 'Not allowed'}")
            print(f"  Modification: {'Allowed' if perms & fitz.PDF_PERM_MODIFY else 'Not allowed'}")
            print(f"  Copy/Extract: {'Allowed' if perms & fitz.PDF_PERM_COPY else 'Not allowed'}")
            print(f"  Annotations: {'Allowed' if perms & fitz.PDF_PERM_ANNOTATE else 'Not allowed'}")
            print(f"  Form Filling: {'Allowed' if perms & fitz.PDF_PERM_FORM else 'Not allowed'}")
            print(f"  Accessibility: {'Allowed' if perms & fitz.PDF_PERM_ACCESSIBILITY else 'Not allowed'}")
            print(f"  Assembly: {'Allowed' if perms & fitz.PDF_PERM_ASSEMBLE else 'Not allowed'}")
            print(f"  High Quality Print: {'Allowed' if perms & fitz.PDF_PERM_PRINT_HQ else 'Not allowed'}")
        
        # Page Analysis
        print("\nPAGE ANALYSIS:")
        total_images = 0
        total_fonts = set()
        has_annotations = False
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Count images
            image_list = page.get_images()
            total_images += len(image_list)
            
            # Collect fonts
            fonts = page.get_fonts()
            for font in fonts:
                total_fonts.add(font[3])  # Font name
            
            # Check for annotations
            if page.annots():
                has_annotations = True
        
        print(f"  Total Images: {total_images}")
        print(f"  Unique Fonts: {len(total_fonts)}")
        if total_fonts:
            print("  Font Names:")
            for font in sorted(total_fonts)[:10]:  # Show first 10 fonts
                print(f"    - {font}")
            if len(total_fonts) > 10:
                print(f"    ... and {len(total_fonts) - 10} more")
        print(f"  Has Annotations: {'Yes' if has_annotations else 'No'}")
        
        # Form Fields Analysis
        if doc.is_form_pdf:
            print("\nFORM FIELDS:")
            field_types = {}
            field_count = 0
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    field_count += 1
                    field_type = widget.field_type_string
                    field_types[field_type] = field_types.get(field_type, 0) + 1
                    
                    if field_count <= 10:  # Show first 10 fields
                        print(f"  Page {page_num + 1}: {widget.field_name} ({field_type})")
            
            if field_count > 10:
                print(f"  ... and {field_count - 10} more fields")
            
            print("\n  Field Type Summary:")
            for field_type, count in sorted(field_types.items()):
                print(f"    {field_type}: {count}")
        
        # Text Extraction (if requested)
        if extract_text:
            print("\nTEXT CONTENT (first 1000 characters):")
            print("-" * 40)
            
            full_text = ""
            for page_num in range(min(5, doc.page_count)):  # Extract from first 5 pages
                page = doc[page_num]
                text = page.get_text()
                full_text += f"\n--- Page {page_num + 1} ---\n{text}"
                
                if len(full_text) > text_limit:
                    break
            
            # Clean and truncate text
            full_text = full_text.strip()
            if len(full_text) > text_limit:
                full_text = full_text[:text_limit] + "..."
            
            print(full_text if full_text else "No text content found")
            print("-" * 40)
        
        # Page Dimensions
        print("\nPAGE DIMENSIONS:")
        page_sizes = {}
        for page_num in range(doc.page_count):
            page = doc[page_num]
            rect = page.rect
            size = f"{rect.width:.1f} x {rect.height:.1f} pts"
            page_sizes[size] = page_sizes.get(size, 0) + 1
        
        for size, count in sorted(page_sizes.items()):
            print(f"  {size}: {count} page(s)")
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY:")
        print(f"  Total Pages: {doc.page_count}")
        print(f"  Contains Images: {'Yes' if total_images > 0 else 'No'}")
        print(f"  Contains Forms: {'Yes' if doc.is_form_pdf else 'No'}")
        print(f"  Is Encrypted: {'Yes' if doc.is_encrypted else 'No'}")
        print(f"  Has Restrictions: {'Yes' if perms >= 0 else 'No'}")
        print(f"{'='*60}\n")
        
        # Close the document
        doc.close()
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to analyze PDF")
        print(f"  Details: {str(e)}")
        return False

def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Simple PDF Analyzer - Analyze PDF files for basic information, metadata, and structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf                    # Basic analysis
  %(prog)s document.pdf --text             # Include text extraction
  %(prog)s document.pdf --text --limit 500 # Extract only first 500 characters
  
This tool uses the unified-redaction-hub virtual environment.
To use it directly: /home/lroc/unified-redaction-hub/venv/bin/python %(prog)s
        """
    )
    
    parser.add_argument('pdf_file', help='Path to the PDF file to analyze')
    parser.add_argument('-t', '--text', action='store_true', 
                       help='Extract and display text content')
    parser.add_argument('-l', '--limit', type=int, default=1000,
                       help='Character limit for text extraction (default: 1000)')
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.pdf_file):
        print(f"ERROR: File not found: {args.pdf_file}")
        sys.exit(1)
    
    # Check if it's a PDF
    if not args.pdf_file.lower().endswith('.pdf'):
        print(f"WARNING: File may not be a PDF: {args.pdf_file}")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Analyze the PDF
    success = analyze_pdf(args.pdf_file, extract_text=args.text, text_limit=args.limit)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()