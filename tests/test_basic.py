"""
Basic Tests for EasyApply

Simple tests to verify the application structure and basic functionality.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that all main modules can be imported."""
    try:
        from src.utils.constants import APP_NAME, APP_VERSION
        from src.utils.logger import get_logger
        from src.utils.helpers import clean_text
        from src.utils.validators import validate_file_path
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_constants():
    """Test that constants are properly defined."""
    from src.utils.constants import APP_NAME, APP_VERSION, COLORS
    
    assert APP_NAME == "EasyApply"
    assert APP_VERSION == "1.0.0"
    assert "primary" in COLORS
    assert "success" in COLORS


def test_helpers():
    """Test helper functions."""
    from src.utils.helpers import clean_text, normalize_keyword
    
    # Test text cleaning
    dirty_text = "  This   is   a   test   text  \n\n  with   extra   spaces  "
    cleaned = clean_text(dirty_text)
    assert cleaned == "This is a test text with extra spaces"
    
    # Test keyword normalization
    keyword = "  Python Programming  "
    normalized = normalize_keyword(keyword)
    assert normalized == "python programming"


def test_validators():
    """Test validation functions."""
    from src.utils.validators import validate_file_path, validate_file_format
    
    # Test file path validation
    assert validate_file_path(__file__) == True
    assert validate_file_path("nonexistent_file.txt") == False
    
    # Test file format validation
    assert validate_file_format("test.pdf", [".pdf"]) == True
    assert validate_file_format("test.txt", [".pdf"]) == False


def test_logger():
    """Test logger functionality."""
    from src.utils.logger import get_logger
    
    logger = get_logger("test")
    assert logger is not None
    assert logger.name == "test"


def test_application_structure():
    """Test that the application has the expected structure."""
    from src import __version__, __author__, __email__
    
    assert __version__ == "1.0.0"
    assert __author__ == "EasyApply Team"
    assert __email__ == "support@easyapply.com"


if __name__ == "__main__":
    pytest.main([__file__]) 