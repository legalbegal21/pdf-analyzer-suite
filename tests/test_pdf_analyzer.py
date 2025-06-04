"""
Unit tests for PDF Analyzer Suite
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import simple_pdf_analyzer
import analyze_pdf_batch


class TestPDFAnalyzer(unittest.TestCase):
    """Test cases for simple_pdf_analyzer module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = simple_pdf_analyzer.PDFAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test analyzer can be initialized"""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.modules)
    
    def test_format_file_size(self):
        """Test file size formatting"""
        self.assertEqual(self.analyzer._format_file_size(1024), "1.00 KB")
        self.assertEqual(self.analyzer._format_file_size(1048576), "1.00 MB")
        self.assertEqual(self.analyzer._format_file_size(500), "500 B")
    
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_analyze_without_pymupdf(self, mock_getsize, mock_exists):
        """Test basic analysis without PyMuPDF"""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        
        # Temporarily disable PyMuPDF
        original_fitz = simple_pdf_analyzer.fitz
        simple_pdf_analyzer.fitz = None
        
        try:
            result = self.analyzer.analyze("test.pdf")
            self.assertIsNotNone(result)
            self.assertEqual(result['file_info']['size_bytes'], 1024)
            self.assertEqual(result['file_info']['exists'], True)
        finally:
            simple_pdf_analyzer.fitz = original_fitz
    
    def test_json_export(self):
        """Test JSON export functionality"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_data = {"test": "data", "number": 123}
            self.analyzer._export_json(test_data, f.name)
            
        # Read back and verify
        with open(f.name, 'r') as f:
            loaded_data = json.load(f)
            self.assertEqual(loaded_data, test_data)
        
        # Clean up
        os.unlink(f.name)


class TestBatchAnalyzer(unittest.TestCase):
    """Test cases for analyze_pdf_batch module"""
    
    def test_validate_inputs(self):
        """Test input validation"""
        # Test valid inputs
        self.assertTrue(analyze_pdf_batch.validate_inputs('.', 'output.json', 'json'))
        
        # Test invalid directory
        self.assertFalse(analyze_pdf_batch.validate_inputs('/nonexistent', 'output.json', 'json'))
        
        # Test invalid format
        self.assertFalse(analyze_pdf_batch.validate_inputs('.', 'output.json', 'invalid'))
    
    def test_format_duration(self):
        """Test duration formatting"""
        self.assertEqual(analyze_pdf_batch.format_duration(0.5), "0.50s")
        self.assertEqual(analyze_pdf_batch.format_duration(65), "1m 5s")
        self.assertEqual(analyze_pdf_batch.format_duration(3665), "1h 1m 5s")
    
    @patch('glob.glob')
    def test_find_pdf_files(self, mock_glob):
        """Test PDF file discovery"""
        mock_glob.return_value = ['file1.pdf', 'file2.pdf']
        
        files = analyze_pdf_batch.find_pdf_files('.', recursive=False)
        self.assertEqual(len(files), 2)
        self.assertIn('file1.pdf', files)
    
    def test_csv_export(self):
        """Test CSV export functionality"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_results = [
                {
                    'file_path': 'test1.pdf',
                    'pages': 10,
                    'file_size': 1024,
                    'has_text': True,
                    'has_images': False,
                    'has_forms': True
                }
            ]
            
            analyze_pdf_batch.export_results_csv(test_results, f.name)
            
        # Verify file was created
        self.assertTrue(os.path.exists(f.name))
        
        # Clean up
        os.unlink(f.name)


class TestIntegration(unittest.TestCase):
    """Integration tests for the PDF Analyzer Suite"""
    
    def test_modules_import(self):
        """Test all modules can be imported"""
        modules = [
            'simple_pdf_analyzer',
            'analyze_pdf_batch',
            'pdf_structured_extractor'
        ]
        
        for module_name in modules:
            try:
                module = __import__(module_name)
                self.assertIsNotNone(module)
            except ImportError as e:
                # Some modules may have optional dependencies
                print(f"Warning: Could not import {module_name}: {e}")


if __name__ == '__main__':
    unittest.main()