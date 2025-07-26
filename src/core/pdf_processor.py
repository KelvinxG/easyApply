"""
PDF Processing Module

Handles PDF file processing, text extraction, and validation for resume analysis.
Supports both PyPDF2 and pdfplumber libraries for robust text extraction.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import re

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logging.warning("PyPDF2 not available, falling back to pdfplumber")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.error("pdfplumber not available. PDF processing will not work.")

from src.utils.constants import (
    PDF_MAX_SIZE_MB, PDF_PASSWORD_TIMEOUT, SUPPORTED_RESUME_FORMATS,
    ERROR_MESSAGES
)
from src.utils.validators import validate_file_path, validate_file_size


class PDFProcessor:
    """
    PDF processing class for extracting text from PDF resumes.
    
    Supports multiple PDF processing libraries and provides fallback mechanisms
    for robust text extraction.
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        self.logger = logging.getLogger(__name__)
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """Validate that required PDF processing libraries are available."""
        if not PYPDF2_AVAILABLE and not PDFPLUMBER_AVAILABLE:
            raise ImportError(
                "Neither PyPDF2 nor pdfplumber is available. "
                "Please install at least one of these libraries."
            )
    
    def process_pdf(self, file_path: str) -> Dict[str, any]:
        """
        Process a PDF file and extract text content.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict[str, any]: Dictionary containing extracted text and metadata
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is invalid or corrupted
            Exception: For other processing errors
        """
        file_path = Path(file_path)
        
        # Validate file
        self._validate_file(file_path)
        
        try:
            # Try pdfplumber first (better text extraction)
            if PDFPLUMBER_AVAILABLE:
                return self._extract_with_pdfplumber(file_path)
            
            # Fallback to PyPDF2
            elif PYPDF2_AVAILABLE:
                return self._extract_with_pypdf2(file_path)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {file_path}: {e}")
            raise Exception(ERROR_MESSAGES["processing_error"].format(str(e)))
    
    def _validate_file(self, file_path: Path):
        """
        Validate the PDF file before processing.
        
        Args:
            file_path (Path): Path to the PDF file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(ERROR_MESSAGES["file_not_found"].format(file_path))
        
        # Check file extension
        if file_path.suffix.lower() not in SUPPORTED_RESUME_FORMATS:
            raise ValueError(
                ERROR_MESSAGES["invalid_file_format"].format(
                    ", ".join(SUPPORTED_RESUME_FORMATS)
                )
            )
        
        # Check file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > PDF_MAX_SIZE_MB:
            raise ValueError(
                ERROR_MESSAGES["file_too_large"].format(PDF_MAX_SIZE_MB)
            )
    
    def _extract_with_pdfplumber(self, file_path: Path) -> Dict[str, any]:
        """
        Extract text using pdfplumber library.
        
        Args:
            file_path (Path): Path to the PDF file
            
        Returns:
            Dict[str, any]: Extracted text and metadata
        """
        self.logger.info(f"Extracting text with pdfplumber from {file_path}")
        
        text_content = []
        metadata = {
            "pages": 0,
            "characters": 0,
            "words": 0,
            "extraction_method": "pdfplumber",
            "processing_time": 0
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                metadata["pages"] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    self.logger.debug(f"Processing page {page_num + 1}")
                    
                    # Extract text from page
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                    
                    # Extract tables if present
                    tables = page.extract_tables()
                    for table in tables:
                        table_text = self._extract_table_text(table)
                        if table_text:
                            text_content.append(table_text)
                
                # Combine all text
                full_text = "\n".join(text_content)
                metadata["characters"] = len(full_text)
                metadata["words"] = len(full_text.split())
                
                return {
                    "text": full_text,
                    "metadata": metadata,
                    "success": True
                }
                
        except Exception as e:
            self.logger.error(f"pdfplumber extraction failed: {e}")
            raise
    
    def _extract_with_pypdf2(self, file_path: Path) -> Dict[str, any]:
        """
        Extract text using PyPDF2 library.
        
        Args:
            file_path (Path): Path to the PDF file
            
        Returns:
            Dict[str, any]: Extracted text and metadata
        """
        self.logger.info(f"Extracting text with PyPDF2 from {file_path}")
        
        text_content = []
        metadata = {
            "pages": 0,
            "characters": 0,
            "words": 0,
            "extraction_method": "PyPDF2",
            "processing_time": 0
        }
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    raise ValueError(ERROR_MESSAGES["password_protected"])
                
                metadata["pages"] = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    self.logger.debug(f"Processing page {page_num + 1}")
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                
                # Combine all text
                full_text = "\n".join(text_content)
                metadata["characters"] = len(full_text)
                metadata["words"] = len(full_text.split())
                
                return {
                    "text": full_text,
                    "metadata": metadata,
                    "success": True
                }
                
        except Exception as e:
            self.logger.error(f"PyPDF2 extraction failed: {e}")
            raise
    
    def _extract_table_text(self, table: List[List[str]]) -> str:
        """
        Extract text from a table structure.
        
        Args:
            table (List[List[str]]): Table data as list of lists
            
        Returns:
            str: Extracted text from table
        """
        if not table:
            return ""
        
        text_lines = []
        for row in table:
            # Filter out None values and join with spaces
            row_text = " ".join([str(cell) for cell in row if cell is not None])
            if row_text.strip():
                text_lines.append(row_text)
        
        return "\n".join(text_lines)
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with analysis
        text = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}]', ' ', text)
        
        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def get_pdf_metadata(self, file_path: str) -> Dict[str, any]:
        """
        Extract PDF metadata without processing the full content.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict[str, any]: PDF metadata
        """
        file_path = Path(file_path)
        self._validate_file(file_path)
        
        try:
            if PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(file_path) as pdf:
                    return {
                        "pages": len(pdf.pages),
                        "file_size": file_path.stat().st_size,
                        "extraction_method": "pdfplumber"
                    }
            elif PYPDF2_AVAILABLE:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    return {
                        "pages": len(pdf_reader.pages),
                        "file_size": file_path.stat().st_size,
                        "extraction_method": "PyPDF2"
                    }
        except Exception as e:
            self.logger.error(f"Error getting PDF metadata: {e}")
            raise
    
    def is_pdf_valid(self, file_path: str) -> bool:
        """
        Check if a PDF file is valid and can be processed.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            bool: True if PDF is valid, False otherwise
        """
        try:
            self._validate_file(Path(file_path))
            return True
        except Exception:
            return False 