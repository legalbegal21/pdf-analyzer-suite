#!/usr/bin/env python3
"""
PDF Batch Processing Script with Parallel Analysis
Processes multiple PDFs and generates comprehensive reports in CSV/JSON format

Author: LROC Enhanced Processing System
Version: 1.0.0
"""

import os
import sys
import json
import csv
import argparse
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional, Any
import multiprocessing
import traceback
import time

# Add virtual environment packages if available
VENV_PATH = "/home/lroc/unified-redaction-hub/venv"
if os.path.exists(VENV_PATH):
    sys.path.insert(0, os.path.join(VENV_PATH, "lib/python3.10/site-packages"))

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("Warning: PyMuPDF not available. Using basic PDF analysis.")

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Info: OCR capabilities not available.")

# Configure logging
def setup_logging(log_file: Optional[str] = None, verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    return logging.getLogger(__name__)

class PDFAnalyzer:
    """Analyzes individual PDF files and extracts metadata and content"""
    
    def __init__(self, enable_ocr: bool = False):
        self.enable_ocr = enable_ocr and OCR_AVAILABLE
        
    def analyze_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Analyze a single PDF file"""
        start_time = time.time()
        
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return self._error_result(str(pdf_path), "File not found")
            
            result = {
                "file_path": str(pdf_path),
                "file_name": pdf_path.name,
                "file_size_bytes": pdf_path.stat().st_size,
                "file_size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
                "modified_date": datetime.fromtimestamp(pdf_path.stat().st_mtime).isoformat(),
                "analysis_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": 0,
                "error": None
            }
            
            if PYMUPDF_AVAILABLE:
                result.update(self._analyze_with_pymupdf(pdf_path))
            else:
                result.update(self._analyze_basic(pdf_path))
            
            result["processing_time_seconds"] = round(time.time() - start_time, 2)
            return result
            
        except Exception as e:
            return self._error_result(str(pdf_path), str(e), traceback.format_exc())
    
    def _analyze_with_pymupdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Analyze PDF using PyMuPDF"""
        doc = fitz.open(str(pdf_path))
        
        try:
            # Basic metadata
            metadata = doc.metadata or {}
            
            # Page analysis
            page_count = doc.page_count
            page_info = []
            total_text_length = 0
            total_images = 0
            total_links = 0
            has_forms = False
            
            for i, page in enumerate(doc):
                text = page.get_text()
                text_length = len(text)
                total_text_length += text_length
                
                # Count images
                image_list = page.get_images()
                image_count = len(image_list)
                total_images += image_count
                
                # Count links
                links = page.get_links()
                link_count = len(links)
                total_links += link_count
                
                # Check for form fields
                widgets = page.widgets()
                form_fields = sum(1 for _ in widgets)
                if form_fields > 0:
                    has_forms = True
                
                page_info.append({
                    "page_number": i + 1,
                    "text_length": text_length,
                    "image_count": image_count,
                    "link_count": link_count,
                    "form_fields": form_fields,
                    "width": page.rect.width,
                    "height": page.rect.height
                })
            
            # Calculate statistics
            avg_text_per_page = total_text_length / page_count if page_count > 0 else 0
            
            # Extract text samples
            first_page_text = doc[0].get_text()[:500] if page_count > 0 else ""
            
            result = {
                "page_count": page_count,
                "total_text_length": total_text_length,
                "average_text_per_page": round(avg_text_per_page, 2),
                "total_images": total_images,
                "total_links": total_links,
                "has_forms": has_forms,
                "is_encrypted": doc.is_encrypted,
                "is_tagged": getattr(doc, 'is_tagged', None),
                "pdf_version": doc.metadata.get("format", "Unknown"),
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
                "producer": metadata.get("producer", ""),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "first_page_preview": first_page_text.replace('\n', ' ')[:200] + "..." if first_page_text else "",
                "page_details": page_info[:5]  # First 5 pages for summary
            }
            
            # OCR analysis if enabled
            if self.enable_ocr and total_text_length < 100:
                result["ocr_performed"] = True
                result["ocr_text_sample"] = self._perform_ocr(doc, max_pages=3)
            else:
                result["ocr_performed"] = False
                
            return result
            
        finally:
            doc.close()
    
    def _analyze_basic(self, pdf_path: Path) -> Dict[str, Any]:
        """Basic PDF analysis without PyMuPDF"""
        return {
            "page_count": "Unknown",
            "analysis_method": "basic",
            "note": "Install PyMuPDF for detailed analysis"
        }
    
    def _perform_ocr(self, doc, max_pages: int = 3) -> str:
        """Perform OCR on PDF pages"""
        ocr_text = []
        
        for i in range(min(max_pages, doc.page_count)):
            page = doc[i]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img_data = pix.tobytes("png")
            
            img = Image.open(io.BytesIO(img_data))
            text = pytesseract.image_to_string(img)
            if text.strip():
                ocr_text.append(f"Page {i+1}: {text[:200]}...")
        
        return "\n".join(ocr_text) if ocr_text else "No text found via OCR"
    
    def _error_result(self, file_path: str, error: str, traceback: str = "") -> Dict[str, Any]:
        """Create error result dictionary"""
        return {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "error": error,
            "traceback": traceback,
            "analysis_timestamp": datetime.now().isoformat()
        }

class PDFBatchProcessor:
    """Processes multiple PDFs in parallel and generates reports"""
    
    def __init__(self, 
                 num_workers: int = None,
                 enable_ocr: bool = False,
                 verbose: bool = False):
        self.num_workers = num_workers or min(8, multiprocessing.cpu_count())
        self.enable_ocr = enable_ocr
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        
    def process_directory(self, 
                         directory: str,
                         pattern: str = "*.pdf",
                         recursive: bool = True) -> List[Dict[str, Any]]:
        """Process all PDFs in a directory"""
        directory = Path(directory)
        
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory}")
        
        # Find all PDF files
        if recursive:
            pdf_files = list(directory.rglob(pattern))
        else:
            pdf_files = list(directory.glob(pattern))
        
        self.logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        if not pdf_files:
            return []
        
        # Process files in parallel
        return self.process_files(pdf_files)
    
    def process_files(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Process a list of PDF files in parallel"""
        results = []
        analyzer = PDFAnalyzer(enable_ocr=self.enable_ocr)
        
        self.logger.info(f"Processing {len(file_paths)} files with {self.num_workers} workers")
        
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(analyzer.analyze_pdf, str(file_path)): file_path
                for file_path in file_paths
            }
            
            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                completed += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if self.verbose:
                        status = "✓" if not result.get("error") else "✗"
                        self.logger.info(f"[{completed}/{len(file_paths)}] {status} {file_path.name}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path}: {e}")
                    results.append({
                        "file_path": str(file_path),
                        "file_name": file_path.name,
                        "error": str(e),
                        "analysis_timestamp": datetime.now().isoformat()
                    })
        
        return results
    
    def generate_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate aggregate statistics from results"""
        if not results:
            return {}
        
        successful = [r for r in results if not r.get("error")]
        failed = [r for r in results if r.get("error")]
        
        total_size = sum(r.get("file_size_bytes", 0) for r in successful)
        total_pages = sum(r.get("page_count", 0) for r in successful if isinstance(r.get("page_count"), int))
        total_text = sum(r.get("total_text_length", 0) for r in successful)
        
        stats = {
            "summary": {
                "total_files": len(results),
                "successful": len(successful),
                "failed": len(failed),
                "success_rate": round(len(successful) / len(results) * 100, 2) if results else 0
            },
            "file_statistics": {
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "average_size_mb": round(total_size / (1024 * 1024) / len(successful), 2) if successful else 0,
                "largest_file": max(successful, key=lambda x: x.get("file_size_bytes", 0))["file_name"] if successful else None,
                "smallest_file": min(successful, key=lambda x: x.get("file_size_bytes", 0))["file_name"] if successful else None
            },
            "content_statistics": {
                "total_pages": total_pages,
                "average_pages": round(total_pages / len(successful), 2) if successful else 0,
                "total_text_length": total_text,
                "average_text_length": round(total_text / len(successful), 2) if successful else 0,
                "files_with_forms": sum(1 for r in successful if r.get("has_forms")),
                "files_with_images": sum(1 for r in successful if r.get("total_images", 0) > 0),
                "encrypted_files": sum(1 for r in successful if r.get("is_encrypted"))
            },
            "processing_statistics": {
                "total_processing_time": sum(r.get("processing_time_seconds", 0) for r in results),
                "average_processing_time": round(sum(r.get("processing_time_seconds", 0) for r in results) / len(results), 2) if results else 0,
                "files_requiring_ocr": sum(1 for r in successful if r.get("ocr_performed"))
            },
            "errors": [
                {
                    "file": r["file_name"],
                    "error": r["error"]
                } for r in failed
            ]
        }
        
        return stats
    
    def save_results(self, 
                     results: List[Dict[str, Any]], 
                     output_path: str,
                     format: str = "json",
                     include_stats: bool = True):
        """Save results to file in specified format"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "json":
            self._save_json(results, output_path, include_stats)
        elif format.lower() == "csv":
            self._save_csv(results, output_path, include_stats)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Results saved to: {output_path}")
    
    def _save_json(self, results: List[Dict[str, Any]], output_path: Path, include_stats: bool):
        """Save results as JSON"""
        output = {
            "metadata": {
                "processing_date": datetime.now().isoformat(),
                "total_files": len(results),
                "analyzer_version": "1.0.0",
                "workers_used": self.num_workers
            },
            "results": results
        }
        
        if include_stats:
            output["statistics"] = self.generate_statistics(results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    
    def _save_csv(self, results: List[Dict[str, Any]], output_path: Path, include_stats: bool):
        """Save results as CSV"""
        if not results:
            return
        
        # Flatten nested dictionaries for CSV
        flattened_results = []
        for result in results:
            flat_result = {
                "file_name": result.get("file_name"),
                "file_path": result.get("file_path"),
                "file_size_mb": result.get("file_size_mb"),
                "page_count": result.get("page_count"),
                "total_text_length": result.get("total_text_length"),
                "total_images": result.get("total_images"),
                "has_forms": result.get("has_forms"),
                "is_encrypted": result.get("is_encrypted"),
                "pdf_version": result.get("pdf_version"),
                "title": result.get("title"),
                "author": result.get("author"),
                "creation_date": result.get("creation_date"),
                "error": result.get("error"),
                "processing_time": result.get("processing_time_seconds")
            }
            flattened_results.append(flat_result)
        
        # Write main results
        fieldnames = list(flattened_results[0].keys())
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_results)
        
        # Write statistics to separate file if requested
        if include_stats:
            stats_path = output_path.with_suffix('.stats.json')
            stats = self.generate_statistics(results)
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)
            self.logger.info(f"Statistics saved to: {stats_path}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PDF Batch Processing Script - Analyze multiple PDFs in parallel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all PDFs in a directory
  python analyze_pdf_batch.py /path/to/pdfs -o results.json
  
  # Process with CSV output and statistics
  python analyze_pdf_batch.py /path/to/pdfs -o results.csv -f csv -s
  
  # Process specific files with OCR
  python analyze_pdf_batch.py file1.pdf file2.pdf -o results.json --ocr
  
  # Process with maximum workers and verbose output
  python analyze_pdf_batch.py /path/to/pdfs -o results.json -w 8 -v
        """
    )
    
    parser.add_argument(
        "input",
        nargs="+",
        help="Input directory or PDF files to process"
    )
    
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output file path (JSON or CSV)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (default: auto)"
    )
    
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process directories recursively"
    )
    
    parser.add_argument(
        "-p", "--pattern",
        default="*.pdf",
        help="File pattern to match (default: *.pdf)"
    )
    
    parser.add_argument(
        "-s", "--stats",
        action="store_true",
        help="Include aggregate statistics in output"
    )
    
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Enable OCR for pages with little/no text"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--log",
        help="Log file path"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log, args.verbose)
    
    try:
        # Initialize processor
        processor = PDFBatchProcessor(
            num_workers=args.workers,
            enable_ocr=args.ocr,
            verbose=args.verbose
        )
        
        # Collect files to process
        all_files = []
        for input_path in args.input:
            path = Path(input_path)
            if path.is_file() and path.suffix.lower() == '.pdf':
                all_files.append(path)
            elif path.is_dir():
                results = processor.process_directory(
                    path,
                    pattern=args.pattern,
                    recursive=args.recursive
                )
                # Don't process directory results here, get files instead
                if args.recursive:
                    all_files.extend(path.rglob(args.pattern))
                else:
                    all_files.extend(path.glob(args.pattern))
            else:
                logger.warning(f"Skipping invalid input: {input_path}")
        
        if not all_files:
            logger.error("No PDF files found to process")
            return 1
        
        # Process all files
        logger.info(f"Starting batch processing of {len(all_files)} PDF files")
        start_time = time.time()
        
        results = processor.process_files(all_files)
        
        total_time = time.time() - start_time
        logger.info(f"Completed processing in {total_time:.2f} seconds")
        
        # Generate and display statistics
        if args.stats or args.verbose:
            stats = processor.generate_statistics(results)
            logger.info("\n=== Processing Statistics ===")
            logger.info(f"Total files: {stats['summary']['total_files']}")
            logger.info(f"Successful: {stats['summary']['successful']}")
            logger.info(f"Failed: {stats['summary']['failed']}")
            logger.info(f"Success rate: {stats['summary']['success_rate']}%")
            logger.info(f"Total size: {stats['file_statistics']['total_size_mb']} MB")
            logger.info(f"Total pages: {stats['content_statistics']['total_pages']}")
            logger.info(f"Files with forms: {stats['content_statistics']['files_with_forms']}")
            logger.info(f"Processing rate: {len(all_files) / total_time:.2f} files/second")
        
        # Save results
        processor.save_results(
            results,
            args.output,
            format=args.format,
            include_stats=args.stats
        )
        
        logger.info(f"\nResults saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())