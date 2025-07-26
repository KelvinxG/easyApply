"""
Logging Configuration Module

Provides centralized logging configuration for the EasyApply application.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Set up application logging with both file and console handlers.
    
    Args:
        log_level (int): Logging level (default: logging.INFO)
        log_file (str, optional): Path to log file. If None, uses default location.
    """
    # Create logs directory if it doesn't exist
    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"easyapply_{timestamp}.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Create file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger('PySide6').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized. Log file: {log_file}")


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name (str): Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name) 