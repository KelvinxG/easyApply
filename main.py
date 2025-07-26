#!/usr/bin/env python3
"""
EasyApply - Main Application Entry Point

Resume-Job Description Keyword Matching Application
A comprehensive PySide6 desktop application for analyzing resume keywords
against job descriptions to provide matching insights and scoring.
"""

import sys
import logging
import traceback
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox


from PySide6.QtCore import Qt

# Ensure src/ is in the Python path for absolute imports
project_root = Path(__file__).parent.resolve()
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.gui.main_window import MainWindow
from src.utils.logger import setup_logging


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler for uncaught exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Handle Ctrl+C gracefully
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log the exception
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Show error dialog to user
    error_msg = f"An unexpected error occurred:\n\n{exc_value}\n\n"
    error_msg += "Please check the log files for more details."
    
    if QApplication.instance():
        QMessageBox.critical(None, "Error", error_msg)


def main():
    """Main application entry point."""
    # Set up logging
    setup_logging()
    logging.info("Starting EasyApply application")
    
    # Set global exception handler
    sys.excepthook = handle_exception
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("EasyApply")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("EasyApply Team")
    
    # Set application properties
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    try:
        # Create and show main window
        window = MainWindow()
        window.show()
        
        logging.info("Main window displayed successfully")
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logging.error(f"Failed to start application: {e}")
        QMessageBox.critical(None, "Startup Error", 
                           f"Failed to start application:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 