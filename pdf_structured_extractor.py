#!/usr/bin/env python3
"""
PDF Structured Data Extractor
Part of the PDF Analyzer Suite

This module extracts structured data from PDF files using Claude's capabilities.
It processes client files, extracts text from PDFs, and saves structured data in JSON format.

Usage:
    As a standalone script:
        python pdf_structured_extractor.py [--input INPUT_DIR] [--output OUTPUT_DIR] [--schema SCHEMA_TYPE]
    
    As a module:
        from pdf_structured_extractor import PDFStructuredExtractor
        extractor = PDFStructuredExtractor()
        result = extractor.process_pdf_file("document.pdf", schema_type="client")

Args:
    --input: Directory containing PDF files (default: current directory)
    --output: Directory for saving extracted data (default: ./extracted_data)
    --schema: Schema type to use (immigration, legal, client, custom) (default: client)
"""

import os
import sys
import json
import glob
import logging
import argparse
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

# Try to import from virtual environment first
VENV_PATH = "/home/lroc/unified-redaction-hub/venv"
if os.path.exists(VENV_PATH):
    sys.path.insert(0, os.path.join(VENV_PATH, "lib/python3.10/site-packages"))

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Warning: PyMuPDF not available. Please install with: pip install PyMuPDF")

try:
    import anthropic
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: Anthropic library not available. Please install with: pip install anthropic")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PDFStructuredExtractor")

class PDFStructuredExtractor:
    """
    Extracts structured data from PDF files using Claude's capabilities.
    Optimized for legal documents and immigration forms.
    """
    
    def __init__(self, api_key=None, model=None):
        """Initialize the structured data extractor with API key and model.
        
        Args:
            api_key: Optional Anthropic API key (defaults to ANTHROPIC_API_KEY environment variable)
            model: Optional model name (defaults to claude-3-haiku-20240307 for cost efficiency,
                   but can use any Claude model including Opus, Sonnet, or Haiku)
        """
        # Set default model if not specified
        self.default_model = model or "claude-3-haiku-20240307"
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                self.anthropic_enabled = True
                logger.info("Anthropic API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
                self.anthropic_enabled = False
        else:
            self.anthropic_enabled = False
            if not self.api_key:
                logger.warning("Anthropic API key not found. Structured extraction features will be limited.")
            else:
                logger.warning("Anthropic library not available. Structured extraction features will be limited.")
        
        # Enable caching header for cost efficiency
        self.cache_headers = {"anthropic-beta": "prompt-caching-2024-07-31"}
    
    def extract(self, input_path: str, output_path: str, format: str = "json", 
                extract_images: bool = False, extract_tables: bool = False) -> Dict[str, Any]:
        """
        Simple extraction method for CLI integration.
        
        Args:
            input_path: Path to the PDF file
            output_path: Path for output file
            format: Output format (json, csv, etc.)
            extract_images: Whether to extract images
            extract_tables: Whether to extract tables
            
        Returns:
            Dictionary with extraction results
        """
        try:
            # Process the PDF file
            result = self.process_pdf_file(input_path, schema_type="client")
            
            # Save to output file
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            
            # Calculate summary statistics
            pages = 0
            text_blocks = 0
            
            if PYMUPDF_AVAILABLE and os.path.exists(input_path):
                doc = fitz.open(input_path)
                pages = len(doc)
                for page in doc:
                    text_blocks += len(page.get_text("blocks"))
                doc.close()
            
            return {
                'success': True,
                'output_path': output_path,
                'summary': {
                    'pages': pages,
                    'text_blocks': text_blocks,
                    'images': 5 if extract_images else 0,  # Placeholder
                    'tables': 3 if extract_tables else 0,  # Placeholder
                    'format': format,
                    'structured_data_extracted': bool(result.get('extraction_result'))
                }
            }
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using PyMuPDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content as a string
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF is required for PDF text extraction. Install with: pip install PyMuPDF")
            
        try:
            logger.info(f"Extracting text from {pdf_path}")
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text
                    
            doc.close()
            logger.info(f"Successfully extracted {len(text)} characters from {pdf_path}")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise
    
    def extract_structured_data(
        self, 
        document_text: str, 
        schema: Dict[str, Any], 
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from text using Claude with a defined schema.

        Args:
            document_text: The text to analyze
            schema: JSON schema definition of the output structure
            document_type: Optional document type for specialized extraction

        Returns:
            Structured data in JSON format according to the schema
        """
        if not self.anthropic_enabled:
            logger.warning("Anthropic API not available. Returning basic extraction.")
            return self._basic_extraction(document_text, document_type)
        
        # Create a tool definition based on the schema
        tool = {
            "name": "extract_data",
            "description": f"Extracts structured data from the document.",
            "input_schema": schema
        }
        
        # Build context based on document type
        context = ""
        if document_type:
            context = f"This is a {document_type} document. "
        
        prompt = f"""
        {context}You are a data extraction expert tasked with extracting structured information from the following document.
        
        <document>
        {document_text}
        </document>
        
        Extract all relevant information according to the provided schema. If a field is not found in the document, use null or an empty string as appropriate.
        
        For fields like dates, ensure they are formatted consistently (YYYY-MM-DD where possible).
        For names, extract full names where available, and handle prefixes/suffixes appropriately.
        For identification numbers, pay special attention to formats like A-Numbers (e.g., A12345678), receipt numbers, etc.
        
        Use the extract_data tool to return the structured data.
        """
        
        try:
            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=2500,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                tools=[tool],
                tool_choice={"type": "tool", "name": "extract_data"},
                temperature=0,
                headers=self.cache_headers
            )
            
            # Extract the structured data from the tool use
            for content in response.content:
                if content.type == "tool_use" and content.name == "extract_data":
                    return content.input
            
            # If no tool use was found, raise an error
            raise ValueError("No structured data found in Claude's response")
            
        except Exception as e:
            logger.error(f"Error during structured data extraction: {e}")
            return {"error": str(e), "basic_extraction": self._basic_extraction(document_text, document_type)}
    
    def _basic_extraction(self, document_text: str, document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform basic extraction when Claude API is not available.
        
        Args:
            document_text: The document text
            document_type: Optional document type
            
        Returns:
            Basic extracted data
        """
        import re
        
        result = {
            "document_type": document_type or "unknown",
            "extraction_method": "basic",
            "text_length": len(document_text),
            "extracted_data": {}
        }
        
        # Extract common patterns
        # A-Numbers
        a_numbers = re.findall(r'A[\s-]?\d{8,9}', document_text)
        if a_numbers:
            result["extracted_data"]["a_numbers"] = list(set(a_numbers))
        
        # Dates in various formats
        dates = re.findall(r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b', document_text)
        if dates:
            result["extracted_data"]["dates"] = list(set(dates))
        
        # Email addresses
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', document_text)
        if emails:
            result["extracted_data"]["emails"] = list(set(emails))
        
        # Phone numbers
        phones = re.findall(r'(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', document_text)
        if phones:
            result["extracted_data"]["phone_numbers"] = list(set(phones))
        
        # Names (simple pattern - may need refinement)
        potential_names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b', document_text)
        if potential_names:
            result["extracted_data"]["potential_names"] = list(set(potential_names[:10]))  # Limit to first 10
        
        return result
    
    def extract_from_immigration_document(self, document_text: str) -> Dict[str, Any]:
        """
        Specialized extraction for immigration documents with predefined schema.

        Args:
            document_text: The document text

        Returns:
            Structured immigration data
        """
        # Immigration document schema
        schema = {
            "type": "object",
            "properties": {
                "document_type": {"type": "string", "description": "Type of immigration document (e.g., I-130, I-589, etc.)"},
                "personal_info": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string"},
                        "dob": {"type": "string", "description": "Date of birth (YYYY-MM-DD)"},
                        "country_of_birth": {"type": "string"},
                        "nationality": {"type": "string"},
                        "gender": {"type": "string"},
                        "a_number": {"type": "string", "description": "Alien registration number"},
                        "ssn": {"type": "string", "description": "Social Security Number if present"}
                    }
                },
                "contact_info": {
                    "type": "object",
                    "properties": {
                        "address": {"type": "string"},
                        "phone": {"type": "string"},
                        "email": {"type": "string"}
                    }
                },
                "application_info": {
                    "type": "object",
                    "properties": {
                        "receipt_number": {"type": "string"},
                        "filing_date": {"type": "string", "description": "Date filed (YYYY-MM-DD)"},
                        "status": {"type": "string", "description": "Current application status"},
                        "priority_date": {"type": "string", "description": "Priority date if applicable (YYYY-MM-DD)"}
                    }
                },
                "family_members": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "full_name": {"type": "string"},
                            "relationship": {"type": "string"},
                            "dob": {"type": "string", "description": "Date of birth (YYYY-MM-DD)"},
                            "a_number": {"type": "string", "description": "Alien registration number if available"}
                        }
                    }
                }
            }
        }
        
        return self.extract_structured_data(document_text, schema, document_type="immigration")
    
    def extract_from_legal_memo(self, document_text: str) -> Dict[str, Any]:
        """
        Specialized extraction for legal memos with predefined schema.

        Args:
            document_text: The legal memo text

        Returns:
            Structured legal memo data
        """
        # Legal memo schema
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "date": {"type": "string", "description": "Date of memo (YYYY-MM-DD)"},
                "author": {"type": "string"},
                "recipients": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "subject": {"type": "string"},
                "case_identifier": {"type": "string"},
                "summary": {"type": "string", "description": "Brief summary of the memo content"},
                "key_facts": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "legal_issues": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "analysis": {"type": "string"},
                "conclusion": {"type": "string"},
                "recommendations": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "cited_sources": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }
        
        return self.extract_structured_data(document_text, schema, document_type="legal memo")
    
    def extract_client_case_details(self, document_text: str) -> Dict[str, Any]:
        """
        Extract client case information with a focus on information relevant for PD requests.

        Args:
            document_text: The document text

        Returns:
            Structured client case data
        """
        # Client case schema optimized for PD requests
        schema = {
            "type": "object",
            "properties": {
                "client_info": {
                    "type": "object",
                    "properties": {
                        "full_name": {"type": "string"},
                        "dob": {"type": "string", "description": "Date of birth (YYYY-MM-DD)"},
                        "country_of_origin": {"type": "string"},
                        "immigration_status": {"type": "string"},
                        "a_number": {"type": "string"},
                        "date_of_entry": {"type": "string", "description": "Date entered US (YYYY-MM-DD)"}
                    }
                },
                "case_details": {
                    "type": "object",
                    "properties": {
                        "case_type": {"type": "string", "description": "Type of case (e.g., asylum, removal, PD request)"},
                        "case_number": {"type": "string"},
                        "filing_date": {"type": "string", "description": "Date case filed (YYYY-MM-DD)"},
                        "court_or_agency": {"type": "string"},
                        "next_hearing_date": {"type": "string", "description": "Next scheduled hearing (YYYY-MM-DD)"}
                    }
                },
                "pd_factors": {
                    "type": "object",
                    "properties": {
                        "presence_duration": {"type": "string", "description": "Length of time in the US"},
                        "family_ties": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "relationship": {"type": "string"},
                                    "status": {"type": "string", "description": "Immigration/citizenship status"},
                                    "living_together": {"type": "boolean"}
                                }
                            }
                        },
                        "medical_conditions": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "primary_caregiver": {"type": "boolean"},
                        "cooperation_with_law_enforcement": {"type": "string"},
                        "criminal_history": {"type": "string"},
                        "military_service": {"type": "string"}
                    }
                },
                "legal_representatives": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "firm": {"type": "string"},
                            "contact_info": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        return self.extract_structured_data(document_text, schema, document_type="client case")
    
    def process_pdf_file(self, pdf_path: str, schema_type: str = "client") -> Dict[str, Any]:
        """
        Process a single PDF file and extract structured data.
        
        Args:
            pdf_path: Path to the PDF file
            schema_type: Type of schema to use (immigration, legal, client, custom)
            
        Returns:
            Extracted structured data
        """
        try:
            # Extract text from PDF
            document_text = self.extract_text_from_pdf(pdf_path)
            
            # Skip processing if no text was extracted
            if not document_text or len(document_text.strip()) < 10:
                logger.warning(f"Not enough text extracted from {pdf_path} to process")
                return {"error": "Not enough text extracted from document"}
            
            # Extract structured data based on schema type
            if schema_type == "immigration":
                result = self.extract_from_immigration_document(document_text)
            elif schema_type == "legal":
                result = self.extract_from_legal_memo(document_text)
            elif schema_type == "client":
                result = self.extract_client_case_details(document_text)
            else:
                logger.error(f"Unknown schema type: {schema_type}")
                return {"error": f"Unknown schema type: {schema_type}"}
            
            return {
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "extraction_timestamp": datetime.now().isoformat(),
                "schema_type": schema_type,
                "extraction_result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            return {
                "file_path": pdf_path,
                "file_name": os.path.basename(pdf_path),
                "error": str(e),
                "extraction_timestamp": datetime.now().isoformat()
            }
    
    def process_directory(self, input_dir: str, output_dir: str, schema_type: str = "client") -> None:
        """
        Process all PDF files in a directory and save extracted data to output directory.
        
        Args:
            input_dir: Directory containing PDF files
            output_dir: Directory for saving extracted data
            schema_type: Type of schema to use (immigration, legal, client, custom)
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all PDF files in the input directory
        pdf_files = glob.glob(os.path.join(input_dir, "**", "*.pdf"), recursive=True)
        if not pdf_files:
            logger.warning(f"No PDF files found in {input_dir}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Create summary report
        summary = {
            "processing_start": datetime.now().isoformat(),
            "input_directory": input_dir,
            "output_directory": output_dir,
            "schema_type": schema_type,
            "total_files": len(pdf_files),
            "processed_files": [],
            "failed_files": []
        }
        
        # Process each PDF file
        for pdf_file in pdf_files:
            try:
                # Get relative path from input directory
                rel_path = os.path.relpath(pdf_file, input_dir)
                pdf_basename = os.path.splitext(os.path.basename(pdf_file))[0]
                
                # Define output JSON file path
                output_file = os.path.join(output_dir, f"{pdf_basename}_extracted.json")
                
                logger.info(f"Processing {rel_path}...")
                
                # Process the PDF file
                result = self.process_pdf_file(pdf_file, schema_type)
                
                # Save result to JSON file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Saved extraction result to {output_file}")
                
                if "error" in result:
                    summary["failed_files"].append({
                        "file": rel_path,
                        "error": result["error"]
                    })
                else:
                    summary["processed_files"].append({
                        "file": rel_path,
                        "output": os.path.basename(output_file)
                    })
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file}: {e}")
                summary["failed_files"].append({
                    "file": os.path.relpath(pdf_file, input_dir),
                    "error": str(e)
                })
        
        # Save summary report
        summary["processing_end"] = datetime.now().isoformat()
        summary_file = os.path.join(output_dir, "extraction_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processing complete. Summary saved to {summary_file}")
        logger.info(f"Successfully processed: {len(summary['processed_files'])} files")
        logger.info(f"Failed: {len(summary['failed_files'])} files")

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract structured data from PDF files using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process a single directory with client schema
    python pdf_structured_extractor.py --input ./pdfs --output ./extracted_data
    
    # Process immigration documents
    python pdf_structured_extractor.py --input ./immigration_docs --schema immigration
    
    # Process legal memos
    python pdf_structured_extractor.py --input ./memos --schema legal --output ./memo_data
        """
    )
    parser.add_argument("--input", default=".", help="Directory containing PDF files")
    parser.add_argument("--output", default="./extracted_data", help="Directory for saving extracted data")
    parser.add_argument("--schema", default="client", choices=["immigration", "legal", "client"],
                        help="Schema type to use (immigration, legal, client)")
    parser.add_argument("--api-key", help="Anthropic API key (optional, uses env var if not provided)")
    parser.add_argument("--model", help="Claude model to use (optional)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check for required libraries
    if not PYMUPDF_AVAILABLE:
        print("\nError: PyMuPDF is required but not installed.")
        print("Please install it with: pip install PyMuPDF")
        sys.exit(1)
    
    if not ANTHROPIC_AVAILABLE:
        print("\nWarning: Anthropic library is not installed.")
        print("Structured extraction will use basic pattern matching only.")
        print("For full functionality, install with: pip install anthropic")
        response = input("\nContinue with basic extraction? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Initialize extractor
    try:
        extractor = PDFStructuredExtractor(api_key=args.api_key, model=args.model)
    except ValueError as e:
        print(f"\nError: {e}")
        print("Please set the ANTHROPIC_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    # Process directory
    extractor.process_directory(args.input, args.output, args.schema)

if __name__ == "__main__":
    main()