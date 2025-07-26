"""
Validation Utilities

Contains validation functions for file handling, input validation,
and data integrity checks throughout the application.
"""

import os
import re
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import logging

from src.utils.constants import (
    SUPPORTED_RESUME_FORMATS, PDF_MAX_SIZE_MB,
    MIN_KEYWORD_LENGTH, MAX_KEYWORD_LENGTH
)
from src.utils.logger import get_logger


def validate_file_path(file_path: Union[str, Path]) -> bool:
    """
    Validate if a file path exists and is accessible.
    
    Args:
        file_path (Union[str, Path]): Path to the file
        
    Returns:
        bool: True if file is valid, False otherwise
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def validate_file_size(file_path: Union[str, Path], max_size_mb: float = PDF_MAX_SIZE_MB) -> bool:
    """
    Validate if a file size is within acceptable limits.
    
    Args:
        file_path (Union[str, Path]): Path to the file
        max_size_mb (float): Maximum file size in MB
        
    Returns:
        bool: True if file size is acceptable, False otherwise
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return False
        
        file_size_mb = path.stat().st_size / (1024 * 1024)
        return file_size_mb <= max_size_mb
    except Exception:
        return False


def validate_file_format(file_path: Union[str, Path], 
                        allowed_formats: List[str] = None) -> bool:
    """
    Validate if a file has an allowed format.
    
    Args:
        file_path (Union[str, Path]): Path to the file
        allowed_formats (List[str], optional): List of allowed file extensions
        
    Returns:
        bool: True if file format is allowed, False otherwise
    """
    if allowed_formats is None:
        allowed_formats = SUPPORTED_RESUME_FORMATS
    
    try:
        path = Path(file_path)
        return path.suffix.lower() in allowed_formats
    except Exception:
        return False


def validate_pdf_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Comprehensive PDF file validation.
    
    Args:
        file_path (Union[str, Path]): Path to the PDF file
        
    Returns:
        Dict[str, Any]: Validation results with details
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': []
    }
    
    try:
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            result['errors'].append("File does not exist")
            return result
        
        # Check if it's a file
        if not path.is_file():
            result['errors'].append("Path is not a file")
            return result
        
        # Check file format
        if not validate_file_format(path, ['.pdf']):
            result['errors'].append("File is not a PDF")
            return result
        
        # Check file size
        if not validate_file_size(path):
            result['errors'].append(f"File size exceeds {PDF_MAX_SIZE_MB} MB limit")
            return result
        
        # Check if file is readable
        try:
            with open(path, 'rb') as f:
                # Read first few bytes to check PDF signature
                header = f.read(4)
                if header != b'%PDF':
                    result['errors'].append("File does not appear to be a valid PDF")
                    return result
        except Exception as e:
            result['errors'].append(f"Cannot read file: {str(e)}")
            return result
        
        # Check file size for warnings
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:  # Warning for files larger than 10MB
            result['warnings'].append(f"Large file size ({file_size_mb:.1f} MB) may slow processing")
        
        result['valid'] = True
        
    except Exception as e:
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def validate_job_description(text: str) -> Dict[str, Any]:
    """
    Validate job description text.
    
    Args:
        text (str): Job description text
        
    Returns:
        Dict[str, Any]: Validation results with details
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'word_count': 0,
        'character_count': 0
    }
    
    try:
        # Check if text is provided
        if not text or not text.strip():
            result['errors'].append("Job description is empty")
            return result
        
        # Count characters and words
        result['character_count'] = len(text)
        result['word_count'] = len(text.split())
        
        # Check minimum length
        if result['word_count'] < 10:
            result['errors'].append("Job description is too short (minimum 10 words)")
            return result
        
        # Check maximum length
        if result['character_count'] > 10000:
            result['warnings'].append("Job description is very long and may slow processing")
        
        # Check for common issues
        if len(text) < 50:
            result['warnings'].append("Job description seems very short")
        
        # Check for potential formatting issues
        if text.count('\n') > 100:
            result['warnings'].append("Job description has many line breaks")
        
        result['valid'] = True
        
    except Exception as e:
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def validate_keyword(keyword: str) -> Dict[str, Any]:
    """
    Validate a keyword for processing.
    
    Args:
        keyword (str): Keyword to validate
        
    Returns:
        Dict[str, Any]: Validation results with details
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'cleaned': keyword
    }
    
    try:
        if not keyword or not keyword.strip():
            result['errors'].append("Keyword is empty")
            return result
        
        # Clean the keyword
        cleaned = keyword.strip()
        result['cleaned'] = cleaned
        
        # Check length
        if len(cleaned) < MIN_KEYWORD_LENGTH:
            result['errors'].append(f"Keyword too short (minimum {MIN_KEYWORD_LENGTH} characters)")
            return result
        
        if len(cleaned) > MAX_KEYWORD_LENGTH:
            result['errors'].append(f"Keyword too long (maximum {MAX_KEYWORD_LENGTH} characters)")
            return result
        
        # Check for invalid characters
        invalid_chars = re.findall(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}]', cleaned)
        if invalid_chars:
            result['warnings'].append(f"Contains special characters: {set(invalid_chars)}")
        
        # Check for common issues
        if cleaned.isdigit():
            result['warnings'].append("Keyword consists only of numbers")
        
        if len(cleaned.split()) > 5:
            result['warnings'].append("Keyword is very long (consider breaking into multiple keywords)")
        
        result['valid'] = True
        
    except Exception as e:
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def validate_keyword_list(keywords: List[str]) -> Dict[str, Any]:
    """
    Validate a list of keywords.
    
    Args:
        keywords (List[str]): List of keywords to validate
        
    Returns:
        Dict[str, Any]: Validation results with details
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'valid_keywords': [],
        'invalid_keywords': [],
        'total_count': len(keywords),
        'valid_count': 0
    }
    
    try:
        if not keywords:
            result['errors'].append("Keyword list is empty")
            return result
        
        # Validate each keyword
        for keyword in keywords:
            validation = validate_keyword(keyword)
            if validation['valid']:
                result['valid_keywords'].append(validation['cleaned'])
                result['valid_count'] += 1
            else:
                result['invalid_keywords'].append({
                    'keyword': keyword,
                    'errors': validation['errors']
                })
        
        # Check overall validity
        if result['valid_count'] == 0:
            result['errors'].append("No valid keywords found")
            return result
        
        if result['valid_count'] < len(keywords) * 0.8:
            result['warnings'].append(f"Many invalid keywords ({len(result['invalid_keywords'])} out of {len(keywords)})")
        
        result['valid'] = True
        
    except Exception as e:
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def validate_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate application settings.
    
    Args:
        settings (Dict[str, Any]): Settings dictionary to validate
        
    Returns:
        Dict[str, Any]: Validation results with details
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'validated_settings': {}
    }
    
    try:
        # Validate fuzzy threshold
        fuzzy_threshold = settings.get('fuzzy_threshold', 70)
        if not isinstance(fuzzy_threshold, (int, float)) or fuzzy_threshold < 0 or fuzzy_threshold > 100:
            result['errors'].append("Fuzzy threshold must be between 0 and 100")
        else:
            result['validated_settings']['fuzzy_threshold'] = fuzzy_threshold
        
        # Validate max keywords
        max_keywords = settings.get('max_keywords', 100)
        if not isinstance(max_keywords, int) or max_keywords < 10 or max_keywords > 1000:
            result['errors'].append("Max keywords must be between 10 and 1000")
        else:
            result['validated_settings']['max_keywords'] = max_keywords
        
        # Validate use_spacy
        use_spacy = settings.get('use_spacy', True)
        if not isinstance(use_spacy, bool):
            result['errors'].append("use_spacy must be a boolean")
        else:
            result['validated_settings']['use_spacy'] = use_spacy
        
        # Validate theme
        theme = settings.get('theme', 'light')
        valid_themes = ['light', 'dark', 'system']
        if theme not in valid_themes:
            result['errors'].append(f"Theme must be one of: {valid_themes}")
        else:
            result['validated_settings']['theme'] = theme
        
        # Validate auto_save
        auto_save = settings.get('auto_save', True)
        if not isinstance(auto_save, bool):
            result['errors'].append("auto_save must be a boolean")
        else:
            result['validated_settings']['auto_save'] = auto_save
        
        if not result['errors']:
            result['valid'] = True
        
    except Exception as e:
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe file operations.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'untitled'
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def validate_directory_path(dir_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Validate if a directory path exists and is accessible.
    
    Args:
        dir_path (Union[str, Path]): Path to the directory
        
    Returns:
        Dict[str, Any]: Validation results with details
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'exists': False,
        'writable': False
    }
    
    try:
        path = Path(dir_path)
        
        # Check if directory exists
        if path.exists():
            result['exists'] = True
            
            # Check if it's a directory
            if not path.is_dir():
                result['errors'].append("Path exists but is not a directory")
                return result
            
            # Check if it's writable
            try:
                test_file = path / '.test_write'
                test_file.touch()
                test_file.unlink()
                result['writable'] = True
            except Exception:
                result['errors'].append("Directory is not writable")
                return result
        else:
            # Try to create directory
            try:
                path.mkdir(parents=True, exist_ok=True)
                result['exists'] = True
                result['writable'] = True
                result['warnings'].append("Directory was created")
            except Exception as e:
                result['errors'].append(f"Cannot create directory: {str(e)}")
                return result
        
        result['valid'] = True
        
    except Exception as e:
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    if not email:
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    if not url:
        return False
    
    # Basic URL regex pattern
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def validate_json_data(data: Any) -> Dict[str, Any]:
    """
    Validate JSON-like data structure.
    
    Args:
        data (Any): Data to validate
        
    Returns:
        Dict[str, Any]: Validation results with details
    """
    result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'data_type': type(data).__name__
    }
    
    try:
        # Check if data is JSON-serializable
        import json
        json.dumps(data)
        
        # Additional validation based on data type
        if isinstance(data, dict):
            if not data:
                result['warnings'].append("Dictionary is empty")
            else:
                # Check for common issues in dictionaries
                for key, value in data.items():
                    if not isinstance(key, str):
                        result['errors'].append(f"Dictionary key must be string, got {type(key).__name__}")
                    if value is None:
                        result['warnings'].append(f"Key '{key}' has None value")
        
        elif isinstance(data, list):
            if not data:
                result['warnings'].append("List is empty")
            else:
                # Check for common issues in lists
                for i, item in enumerate(data):
                    if item is None:
                        result['warnings'].append(f"List item at index {i} is None")
        
        result['valid'] = True
        
    except (TypeError, ValueError) as e:
        result['errors'].append(f"JSON serialization error: {str(e)}")
    except Exception as e:
        result['errors'].append(f"Validation error: {str(e)}")
    
    return result 