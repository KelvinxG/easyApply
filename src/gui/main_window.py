"""
Main Application Window

The primary GUI window for the EasyApply application with modern design,
file upload capabilities, job description input, and comprehensive results display.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, List
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QTextEdit, QLabel, QProgressBar, QTableWidget,
    QTableWidgetItem, QFileDialog, QMessageBox, QTabWidget,
    QGroupBox, QSplitter, QFrame, QScrollArea, QApplication,
    QStatusBar, QMenuBar, QMenu, QToolBar, QComboBox,
    QSpinBox, QCheckBox, QSlider, QProgressDialog
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer, QSize, QPropertyAnimation,
    QEasingCurve, QRect, QPoint
)
from PySide6.QtGui import (
    QFont, QIcon, QPixmap, QPainter, QColor, QPalette,
    QAction, QActionGroup, QKeySequence, QDragEnterEvent, QDropEvent
)

from src.gui.widgets import (
    FileUploadWidget, KeywordTableWidget, ResultsWidget,
    InfographicWidget, SettingsWidget, StatusWidget
)
from src.gui.styles import get_application_style
from src.core.pdf_processor import PDFProcessor
from src.core.keyword_analyzer import KeywordAnalyzer
from src.core.matcher import KeywordMatcher
from src.utils.constants import (
    APP_NAME, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, COLORS
)
from src.utils.logger import get_logger


class AnalysisWorker(QThread):
    """Worker thread for performing keyword analysis."""
    
    progress_updated = Signal(int)
    analysis_complete = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, resume_path: str, job_description: str):
        super().__init__()
        self.resume_path = resume_path
        self.job_description = job_description
        self.logger = get_logger(__name__)
    
    def run(self):
        """Run the analysis in a separate thread."""
        try:
            self.progress_updated.emit(10)
            
            # Initialize processors
            pdf_processor = PDFProcessor()
            keyword_analyzer = KeywordAnalyzer()
            matcher = KeywordMatcher()
            
            self.progress_updated.emit(20)
            
            # Process PDF
            self.logger.info(f"Processing PDF: {self.resume_path}")
            pdf_result = pdf_processor.process_pdf(self.resume_path)
            resume_text = pdf_processor.clean_text(pdf_result['text'])
            
            self.progress_updated.emit(40)
            
            # Extract keywords from resume
            self.logger.info("Extracting keywords from resume")
            resume_keywords = keyword_analyzer.extract_keywords(resume_text)
            
            self.progress_updated.emit(60)
            
            # Analyze job description
            self.logger.info("Analyzing job description")
            job_analysis = keyword_analyzer.analyze_job_description(self.job_description)
            job_keywords = job_analysis['keywords']
            
            self.progress_updated.emit(80)
            
            # Match keywords
            self.logger.info("Matching keywords")
            match_results = matcher.match_keywords(resume_keywords, job_keywords)
            
            self.progress_updated.emit(90)
            
            # Compile results
            results = {
                'resume_keywords': resume_keywords,
                'job_keywords': job_keywords,
                'job_analysis': job_analysis,
                'match_results': match_results,
                'pdf_metadata': pdf_result['metadata'],
                'resume_text': resume_text,
                'job_description': self.job_description
            }
            
            self.progress_updated.emit(100)
            self.analysis_complete.emit(results)
            
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    """
    Main application window for EasyApply.
    
    Provides a comprehensive interface for resume-job description keyword matching
    with modern design and intuitive user experience.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.analysis_worker = None
        self.current_results = None
        
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_status_bar()
        self._apply_styles()
        self._connect_signals()
        
        self.logger.info("Main window initialized successfully")
    
    def _setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle(f"{APP_NAME} - Resume-Job Description Keyword Matcher")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Left panel (Input)
        self._create_input_panel(main_splitter)
        
        # Right panel (Results)
        self._create_results_panel(main_splitter)
        
        # Set splitter proportions
        main_splitter.setSizes([400, 800])
    
    def _create_input_panel(self, parent):
        """Create the input panel with file upload and job description."""
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        
        # File upload section
        upload_group = QGroupBox("Resume Upload")
        upload_layout = QVBoxLayout(upload_group)
        
        self.file_upload_widget = FileUploadWidget()
        upload_layout.addWidget(self.file_upload_widget)
        
        input_layout.addWidget(upload_group)
        
        # Job description section
        job_group = QGroupBox("Job Description")
        job_layout = QVBoxLayout(job_group)
        
        # Job description text area
        self.job_description_edit = QTextEdit()
        self.job_description_edit.setPlaceholderText(
            "Paste the job description here...\n\n"
            "The application will analyze this text and extract relevant keywords "
            "to match against your resume."
        )
        self.job_description_edit.setMinimumHeight(200)
        job_layout.addWidget(self.job_description_edit)
        
        # Industry selection
        industry_layout = QHBoxLayout()
        industry_layout.addWidget(QLabel("Industry:"))
        
        self.industry_combo = QComboBox()
        self.industry_combo.addItems([
            "Software Development",
            "Data Science",
            "Marketing",
            "Finance",
            "Healthcare",
            "Education",
            "Other"
        ])
        industry_layout.addWidget(self.industry_combo)
        
        job_layout.addLayout(industry_layout)
        
        input_layout.addWidget(job_group)
        
        # Analysis controls
        controls_group = QGroupBox("Analysis Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Analysis button
        self.analyze_button = QPushButton("Analyze Resume")
        self.analyze_button.setMinimumHeight(40)
        self.analyze_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['gray']};
            }}
        """)
        controls_layout.addWidget(self.analyze_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to analyze")
        self.status_label.setAlignment(Qt.AlignCenter)
        controls_layout.addWidget(self.status_label)
        
        input_layout.addWidget(controls_group)
        
        # Add stretch to push everything to the top
        input_layout.addStretch()
        
        parent.addWidget(input_widget)
    
    def _create_results_panel(self, parent):
        """Create the results panel with tabs for different views."""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(10)
        
        # Results title
        title_label = QLabel("Analysis Results")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: bold;
                color: {COLORS['primary']};
                padding: 10px;
            }}
        """)
        results_layout.addWidget(title_label)
        
        # Create tab widget
        self.results_tabs = QTabWidget()
        
        # Overview tab
        self.overview_widget = InfographicWidget()
        self.results_tabs.addTab(self.overview_widget, "Overview")
        
        # Keywords tab
        self.keywords_widget = KeywordTableWidget()
        self.results_tabs.addTab(self.keywords_widget, "Keywords")
        
        # Detailed results tab
        self.detailed_widget = ResultsWidget()
        self.results_tabs.addTab(self.detailed_widget, "Detailed Analysis")
        
        # Settings tab
        self.settings_widget = SettingsWidget()
        self.results_tabs.addTab(self.settings_widget, "Settings")
        
        results_layout.addWidget(self.results_tabs)
        
        parent.addWidget(results_widget)
    
    def _setup_menu(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Resume", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_resume)
        file_menu.addAction(open_action)
        
        save_results_action = QAction("&Save Results", self)
        save_results_action.setShortcut(QKeySequence.Save)
        save_results_action.triggered.connect(self._save_results)
        file_menu.addAction(save_results_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu("&Analysis")
        
        analyze_action = QAction("&Analyze", self)
        analyze_action.setShortcut("Ctrl+A")
        analyze_action.triggered.connect(self._start_analysis)
        analysis_menu.addAction(analyze_action)
        
        clear_action = QAction("&Clear Results", self)
        clear_action.setShortcut("Ctrl+C")
        clear_action.triggered.connect(self._clear_results)
        analysis_menu.addAction(clear_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Set up the application toolbar."""
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        
        # Open resume action
        open_action = QAction("Open Resume", self)
        open_action.triggered.connect(self._open_resume)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # Analyze action
        analyze_action = QAction("Analyze", self)
        analyze_action.triggered.connect(self._start_analysis)
        toolbar.addAction(analyze_action)
        
        toolbar.addSeparator()
        
        # Save results action
        save_action = QAction("Save Results", self)
        save_action.triggered.connect(self._save_results)
        toolbar.addAction(save_action)
    
    def _setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status widget
        self.status_widget = StatusWidget()
        self.status_bar.addPermanentWidget(self.status_widget)
    
    def _apply_styles(self):
        """Apply application-wide styles."""
        self.setStyleSheet(get_application_style())
    
    def _connect_signals(self):
        """Connect all signal handlers."""
        # File upload signals
        self.file_upload_widget.file_selected.connect(self._on_file_selected)
        
        # Analysis button
        self.analyze_button.clicked.connect(self._start_analysis)
        
        # Job description changes
        self.job_description_edit.textChanged.connect(self._on_job_description_changed)
    
    def _on_file_selected(self, file_path: str):
        """Handle file selection from upload widget."""
        self.logger.info(f"File selected: {file_path}")
        self.status_label.setText(f"Resume loaded: {Path(file_path).name}")
        self._update_analyze_button()
    
    def _on_job_description_changed(self):
        """Handle job description text changes."""
        self._update_analyze_button()
    
    def _update_analyze_button(self):
        """Update the analyze button state based on input availability."""
        has_file = self.file_upload_widget.has_file()
        has_job_description = bool(self.job_description_edit.toPlainText().strip())
        
        self.analyze_button.setEnabled(has_file and has_job_description)
    
    def _start_analysis(self):
        """Start the keyword analysis process."""
        if not self.file_upload_widget.has_file():
            QMessageBox.warning(self, "No Resume", "Please select a resume file first.")
            return
        
        job_description = self.job_description_edit.toPlainText().strip()
        if not job_description:
            QMessageBox.warning(self, "No Job Description", "Please enter a job description first.")
            return
        
        # Get selected file path
        resume_path = self.file_upload_widget.get_file_path()
        
        # Start analysis
        self._run_analysis(resume_path, job_description)
    
    def _run_analysis(self, resume_path: str, job_description: str):
        """Run the analysis in a background thread."""
        # Disable UI during analysis
        self.analyze_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Analyzing resume...")
        
        # Create and start worker thread
        self.analysis_worker = AnalysisWorker(resume_path, job_description)
        self.analysis_worker.progress_updated.connect(self.progress_bar.setValue)
        self.analysis_worker.analysis_complete.connect(self._on_analysis_complete)
        self.analysis_worker.error_occurred.connect(self._on_analysis_error)
        self.analysis_worker.finished.connect(self._on_analysis_finished)
        
        self.analysis_worker.start()
    
    def _on_analysis_complete(self, results: Dict):
        """Handle analysis completion."""
        self.current_results = results
        self.logger.info("Analysis completed successfully")
        
        # Update results widgets
        self.overview_widget.update_results(results)
        self.keywords_widget.update_results(results)
        self.detailed_widget.update_results(results)
        
        # Switch to overview tab
        self.results_tabs.setCurrentIndex(0)
        
        # Update status
        match_percentage = results['match_results']['match_percentage']
        self.status_label.setText(f"Analysis complete - Match: {match_percentage:.1f}%")
        
        # Show completion message
        QMessageBox.information(
            self, 
            "Analysis Complete", 
            f"Analysis completed successfully!\n\n"
            f"Overall match: {match_percentage:.1f}%\n"
            f"Keywords found: {len(results['resume_keywords'])}\n"
            f"Job keywords: {len(results['job_keywords'])}"
        )
    
    def _on_analysis_error(self, error_message: str):
        """Handle analysis errors."""
        self.logger.error(f"Analysis error: {error_message}")
        QMessageBox.critical(self, "Analysis Error", f"An error occurred during analysis:\n\n{error_message}")
    
    def _on_analysis_finished(self):
        """Handle analysis thread completion."""
        # Re-enable UI
        self.analyze_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._update_analyze_button()
        
        # Clean up worker
        if self.analysis_worker:
            self.analysis_worker.deleteLater()
            self.analysis_worker = None
    
    def _open_resume(self):
        """Open file dialog to select resume."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Resume File",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            self.file_upload_widget.set_file(file_path)
    
    def _save_results(self):
        """Save analysis results to file."""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "No analysis results to save.")
            return
        
        # TODO: Implement save functionality
        QMessageBox.information(self, "Save Results", "Save functionality will be implemented in a future version.")
    
    def _clear_results(self):
        """Clear current analysis results."""
        self.current_results = None
        self.overview_widget.clear_results()
        self.keywords_widget.clear_results()
        self.detailed_widget.clear_results()
        self.status_label.setText("Results cleared")
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"{APP_NAME} v1.0.0\n\n"
            "A comprehensive resume-job description keyword matching application.\n\n"
            "Features:\n"
            "• PDF resume processing\n"
            "• Advanced keyword extraction\n"
            "• Fuzzy string matching\n"
            "• Visual results presentation\n"
            "• Industry-specific analysis\n\n"
            "Built with PySide6 and modern NLP libraries."
        )
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for file dropping."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for file dropping."""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith('.pdf'):
                self.file_upload_widget.set_file(file_path)
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Stop any running analysis
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.analysis_worker.terminate()
            self.analysis_worker.wait()
        
        self.logger.info("Application closing")
        event.accept() 