"""
Helper Utilities

Contains helper functions for common operations, data processing,
and utility functions used throughout the application.
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging

from src.utils.logger import get_logger


def clean_text(text: str) -> str:
    """
    Clean and normalize text for processing.
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text
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


def extract_text_sections(text: str) -> Dict[str, str]:
    """
    Extract different sections from resume text.
    
    Args:
        text (str): Full resume text
        
    Returns:
        Dict[str, str]: Dictionary of text sections
    """
    sections = {
        'summary': '',
        'experience': '',
        'education': '',
        'skills': '',
        'projects': '',
        'other': ''
    }
    
    # Common section headers
    section_patterns = {
        'summary': r'(summary|profile|objective|about)\s*:?\s*\n(.*?)(?=\n\s*\n|\n\s*[A-Z]|\Z)',
        'experience': r'(experience|work\s+history|employment)\s*:?\s*\n(.*?)(?=\n\s*\n|\n\s*[A-Z]|\Z)',
        'education': r'(education|academic|qualifications)\s*:?\s*\n(.*?)(?=\n\s*\n|\n\s*[A-Z]|\Z)',
        'skills': r'(skills|technical\s+skills|competencies)\s*:?\s*\n(.*?)(?=\n\s*\n|\n\s*[A-Z]|\Z)',
        'projects': r'(projects|portfolio|achievements)\s*:?\s*\n(.*?)(?=\n\s*\n|\n\s*[A-Z]|\Z)'
    }
    
    text_lower = text.lower()
    
    for section_name, pattern in section_patterns.items():
        matches = re.findall(pattern, text_lower, re.IGNORECASE | re.DOTALL)
        if matches:
            sections[section_name] = matches[0][1].strip()
    
    # If no sections found, put everything in 'other'
    if not any(sections.values()):
        sections['other'] = text
    
    return sections


def calculate_text_statistics(text: str) -> Dict[str, Any]:
    """
    Calculate various statistics for text content.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        Dict[str, Any]: Text statistics
    """
    if not text:
        return {
            'characters': 0,
            'words': 0,
            'sentences': 0,
            'paragraphs': 0,
            'unique_words': 0,
            'average_word_length': 0,
            'average_sentence_length': 0
        }
    
    # Basic counts
    characters = len(text)
    words = len(text.split())
    sentences = len(re.split(r'[.!?]+', text))
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])
    
    # Word analysis
    word_list = re.findall(r'\b\w+\b', text.lower())
    unique_words = len(set(word_list))
    
    # Averages
    average_word_length = sum(len(word) for word in word_list) / len(word_list) if word_list else 0
    average_sentence_length = words / sentences if sentences > 0 else 0
    
    return {
        'characters': characters,
        'words': words,
        'sentences': sentences,
        'paragraphs': paragraphs,
        'unique_words': unique_words,
        'average_word_length': round(average_word_length, 2),
        'average_sentence_length': round(average_sentence_length, 2)
    }


def normalize_keyword(keyword: str) -> str:
    """
    Normalize a keyword for consistent matching.
    
    Args:
        keyword (str): Raw keyword
        
    Returns:
        str: Normalized keyword
    """
    if not keyword:
        return ""
    
    # Convert to lowercase
    normalized = keyword.lower()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove special characters but keep important ones
    normalized = re.sub(r'[^\w\s\-\.]', ' ', normalized)
    
    # Strip leading/trailing whitespace
    normalized = normalized.strip()
    
    return normalized


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two text strings.
    
    Args:
        text1 (str): First text string
        text2 (str): Second text string
        
    Returns:
        float: Similarity score (0.0 to 1.0)
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize texts
    text1_norm = normalize_keyword(text1)
    text2_norm = normalize_keyword(text2)
    
    # Calculate Jaccard similarity
    words1 = set(text1_norm.split())
    words2 = set(text2_norm.split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union


def group_similar_keywords(keywords: List[str], threshold: float = 0.8) -> List[List[str]]:
    """
    Group similar keywords together.
    
    Args:
        keywords (List[str]): List of keywords
        threshold (float): Similarity threshold for grouping
        
    Returns:
        List[List[str]]: Groups of similar keywords
    """
    if not keywords:
        return []
    
    groups = []
    used = set()
    
    for i, keyword1 in enumerate(keywords):
        if i in used:
            continue
        
        group = [keyword1]
        used.add(i)
        
        for j, keyword2 in enumerate(keywords[i+1:], i+1):
            if j in used:
                continue
            
            similarity = calculate_similarity(keyword1, keyword2)
            if similarity >= threshold:
                group.append(keyword2)
                used.add(j)
        
        groups.append(group)
    
    return groups


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted file size
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds (float): Duration in seconds
        
    Returns:
        str: Formatted duration
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def generate_unique_filename(base_name: str, extension: str, directory: str = "") -> str:
    """
    Generate a unique filename to avoid conflicts.
    
    Args:
        base_name (str): Base filename
        extension (str): File extension
        directory (str): Directory path
        
    Returns:
        str: Unique filename
    """
    if not base_name:
        base_name = "file"
    
    # Clean the base name
    base_name = re.sub(r'[^\w\s-]', '', base_name)
    base_name = re.sub(r'\s+', '_', base_name)
    
    # Ensure extension starts with dot
    if not extension.startswith('.'):
        extension = '.' + extension
    
    filename = base_name + extension
    counter = 1
    
    while True:
        full_path = Path(directory) / filename if directory else Path(filename)
        if not full_path.exists():
            return str(full_path)
        
        filename = f"{base_name}_{counter}{extension}"
        counter += 1


def save_json_data(data: Any, file_path: Union[str, Path], indent: int = 2) -> bool:
    """
    Save data to JSON file with error handling.
    
    Args:
        data (Any): Data to save
        file_path (Union[str, Path]): Output file path
        indent (int): JSON indentation
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)
        
        return True
    except Exception as e:
        logging.error(f"Error saving JSON data: {e}")
        return False


def load_json_data(file_path: Union[str, Path]) -> Optional[Any]:
    """
    Load data from JSON file with error handling.
    
    Args:
        file_path (Union[str, Path]): Input file path
        
    Returns:
        Optional[Any]: Loaded data or None if failed
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON data: {e}")
        return None


def calculate_hash(data: Union[str, bytes]) -> str:
    """
    Calculate SHA-256 hash of data.
    
    Args:
        data (Union[str, bytes]): Data to hash
        
    Returns:
        str: Hexadecimal hash string
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()


def get_file_hash(file_path: Union[str, Path]) -> Optional[str]:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path (Union[str, Path]): Path to the file
        
    Returns:
        Optional[str]: File hash or None if failed
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        
        hash_sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    except Exception as e:
        logging.error(f"Error calculating file hash: {e}")
        return None


def create_backup(file_path: Union[str, Path], backup_dir: str = "backups") -> Optional[str]:
    """
    Create a backup of a file.
    
    Args:
        file_path (Union[str, Path]): Path to the file to backup
        backup_dir (str): Backup directory name
        
    Returns:
        Optional[str]: Backup file path or None if failed
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        
        # Create backup directory
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{path.stem}_{timestamp}{path.suffix}"
        backup_file_path = backup_path / backup_filename
        
        # Copy file
        import shutil
        shutil.copy2(path, backup_file_path)
        
        return str(backup_file_path)
    except Exception as e:
        logging.error(f"Error creating backup: {e}")
        return None


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging and logging.
    
    Returns:
        Dict[str, Any]: System information
    """
    import platform
    import psutil
    
    try:
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:\\').percent
        }
    except Exception as e:
        logging.error(f"Error getting system info: {e}")
        return {}


def format_timestamp(timestamp: Union[datetime, float, str], 
                    format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp in a consistent way.
    
    Args:
        timestamp (Union[datetime, float, str]): Timestamp to format
        format_str (str): Format string
        
    Returns:
        str: Formatted timestamp
    """
    try:
        if isinstance(timestamp, str):
            # Try to parse string timestamp
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, float):
            # Unix timestamp
            timestamp = datetime.fromtimestamp(timestamp)
        elif not isinstance(timestamp, datetime):
            raise ValueError("Invalid timestamp type")
        
        return timestamp.strftime(format_str)
    except Exception as e:
        logging.error(f"Error formatting timestamp: {e}")
        return str(timestamp)


def retry_operation(operation, max_attempts: int = 3, delay: float = 1.0):
    """
    Retry an operation with exponential backoff.
    
    Args:
        operation: Function to retry
        max_attempts (int): Maximum number of attempts
        delay (float): Initial delay in seconds
        
    Returns:
        Any: Operation result
        
    Raises:
        Exception: Last exception if all attempts fail
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return operation()
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                sleep_time = delay * (2 ** attempt)
                logging.warning(f"Operation failed (attempt {attempt + 1}/{max_attempts}), retrying in {sleep_time}s: {e}")
                import time
                time.sleep(sleep_time)
    
    raise last_exception


def safe_filename(filename: str) -> str:
    """
    Convert a string to a safe filename.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Safe filename
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


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst (List[Any]): List to chunk
        chunk_size (int): Size of each chunk
        
    Returns:
        List[List[Any]]: List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_list(nested_list: List[Any]) -> List[Any]:
    """
    Flatten a nested list.
    
    Args:
        nested_list (List[Any]): Nested list to flatten
        
    Returns:
        List[Any]: Flattened list
    """
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened


def remove_duplicates_preserve_order(lst: List[Any]) -> List[Any]:
    """
    Remove duplicates from a list while preserving order.
    
    Args:
        lst (List[Any]): List with potential duplicates
        
    Returns:
        List[Any]: List with duplicates removed
    """
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result 