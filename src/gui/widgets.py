"""
Custom GUI Widgets

Contains all custom widgets used throughout the EasyApply application
including file upload, keyword tables, results display, and infographics.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QScrollArea, QProgressBar,
    QGroupBox, QTextEdit, QComboBox, QSpinBox, QCheckBox, QSlider,
    QGridLayout, QSplitter, QTabWidget, QListWidget, QListWidgetItem,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsTextItem,
    QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsLineItem
)
from PySide6.QtCore import (
    Qt, Signal, QSize, QRect, QPoint, QPropertyAnimation,
    QEasingCurve, QTimer
)
from PySide6.QtGui import (
    QFont, QPainter, QColor, QPen, QBrush, QPixmap, QIcon,
    QDragEnterEvent, QDropEvent, QPalette
)

from src.utils.constants import COLORS, MATCH_COLORS
from src.utils.logger import get_logger


class FileUploadWidget(QWidget):
    """Custom file upload widget with drag and drop support."""
    
    file_selected = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.logger = get_logger(__name__)
        self._setup_ui()
        self._setup_drag_drop()
    
    def _setup_ui(self):
        """Set up the file upload interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Upload area
        self.upload_frame = QFrame()
        self.upload_frame.setFrameStyle(QFrame.Box)
        self.upload_frame.setMinimumHeight(120)
        self.upload_frame.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {COLORS['gray']};
                border-radius: 8px;
                background-color: {COLORS['light']};
            }}
            QFrame:hover {{
                border-color: {COLORS['primary']};
                background-color: {COLORS['light_gray']};
            }}
        """)
        
        upload_layout = QVBoxLayout(self.upload_frame)
        upload_layout.setAlignment(Qt.AlignCenter)
        
        # Upload icon/label
        self.upload_label = QLabel("📄 Drop PDF resume here\nor click to browse")
        self.upload_label.setAlignment(Qt.AlignCenter)
        self.upload_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['gray']};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        upload_layout.addWidget(self.upload_label)
        
        # Browse button
        self.browse_button = QPushButton("Browse Files")
        self.browse_button.setMaximumWidth(150)
        self.browse_button.clicked.connect(self._browse_files)
        upload_layout.addWidget(self.browse_button, alignment=Qt.AlignCenter)
        
        layout.addWidget(self.upload_frame)
        
        # File info
        self.file_info_label = QLabel("No file selected")
        self.file_info_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['gray']};
                font-size: 12px;
                padding: 5px;
            }}
        """)
        layout.addWidget(self.file_info_label)
        
        # Make upload frame clickable
        self.upload_frame.mousePressEvent = self._on_upload_frame_clicked
    
    def _setup_drag_drop(self):
        """Set up drag and drop functionality."""
        self.setAcceptDrops(True)
    
    def _browse_files(self):
        """Open file dialog to browse for PDF files."""
        from PySide6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Resume PDF",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            self.set_file(file_path)
    
    def _on_upload_frame_clicked(self, event):
        """Handle click on upload frame."""
        self._browse_files()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.upload_frame.setStyleSheet(f"""
                QFrame {{
                    border: 2px dashed {COLORS['primary']};
                    border-radius: 8px;
                    background-color: {COLORS['light_gray']};
                }}
            """)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave events."""
        self.upload_frame.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {COLORS['gray']};
                border-radius: 8px;
                background-color: {COLORS['light']};
            }}
        """)
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith('.pdf'):
                self.set_file(file_path)
        
        self.upload_frame.setStyleSheet(f"""
            QFrame {{
                border: 2px dashed {COLORS['gray']};
                border-radius: 8px;
                background-color: {COLORS['light']};
            }}
        """)
    
    def set_file(self, file_path: str):
        """Set the selected file."""
        self.file_path = file_path
        file_name = Path(file_path).name
        
        # Update UI
        self.upload_label.setText(f"📄 {file_name}")
        self.upload_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['success']};
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        
        # Update file info
        file_size = Path(file_path).stat().st_size / 1024  # KB
        self.file_info_label.setText(f"File: {file_name} ({file_size:.1f} KB)")
        self.file_info_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['success']};
                font-size: 12px;
                padding: 5px;
            }}
        """)
        
        # Emit signal
        self.file_selected.emit(file_path)
        self.logger.info(f"File selected: {file_path}")
    
    def has_file(self) -> bool:
        """Check if a file is selected."""
        return self.file_path is not None
    
    def get_file_path(self) -> Optional[str]:
        """Get the selected file path."""
        return self.file_path


class KeywordTableWidget(QWidget):
    """Widget for displaying keyword matching results in a table format."""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the keyword table interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Create tab widget for different keyword views
        self.tab_widget = QTabWidget()
        
        # Exact matches tab
        self.exact_table = self._create_keyword_table("Exact Matches")
        self.tab_widget.addTab(self.exact_table, "Exact Matches")
        
        # Fuzzy matches tab
        self.fuzzy_table = self._create_keyword_table("Fuzzy Matches")
        self.tab_widget.addTab(self.fuzzy_table, "Fuzzy Matches")
        
        # Partial matches tab
        self.partial_table = self._create_keyword_table("Partial Matches")
        self.tab_widget.addTab(self.partial_table, "Partial Matches")
        
        # Missing keywords tab
        self.missing_table = self._create_missing_table()
        self.tab_widget.addTab(self.missing_table, "Missing Keywords")
        
        layout.addWidget(self.tab_widget)
    
    def _create_keyword_table(self, title: str) -> QTableWidget:
        """Create a keyword table with standard columns."""
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Resume Keyword", "Job Keyword", "Match Type", "Confidence", "Importance", "Status"
        ])
        
        # Set table properties
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        return table
    
    def _create_missing_table(self) -> QTableWidget:
        """Create a table for missing keywords."""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "Missing Keyword", "Importance", "Type", "Recommendation"
        ])
        
        # Set table properties
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        return table
    
    def update_results(self, results: Dict):
        """Update the tables with analysis results."""
        match_results = results['match_results']
        
        # Update exact matches
        self._populate_table(self.exact_table, match_results['exact_matches'])
        
        # Update fuzzy matches
        self._populate_table(self.fuzzy_table, match_results['fuzzy_matches'])
        
        # Update partial matches
        self._populate_table(self.partial_table, match_results['partial_matches'])
        
        # Update missing keywords
        self._populate_missing_table(self.missing_table, match_results['missing_keywords'])
        
        self.logger.info("Keyword tables updated with results")
    
    def _populate_table(self, table: QTableWidget, matches: List[Dict]):
        """Populate a keyword table with match data."""
        table.setRowCount(len(matches))
        
        for row, match in enumerate(matches):
            # Resume keyword
            resume_item = QTableWidgetItem(match['resume_keyword'])
            resume_item.setBackground(QColor(MATCH_COLORS[match['match_type']]))
            table.setItem(row, 0, resume_item)
            
            # Job keyword
            job_item = QTableWidgetItem(match['job_keyword'])
            job_item.setBackground(QColor(MATCH_COLORS[match['match_type']]))
            table.setItem(row, 1, job_item)
            
            # Match type
            type_item = QTableWidgetItem(match['match_type'].title())
            table.setItem(row, 2, type_item)
            
            # Confidence
            confidence = match.get('confidence', 0)
            confidence_item = QTableWidgetItem(f"{confidence:.2f}")
            table.setItem(row, 3, confidence_item)
            
            # Importance
            importance = max(match.get('resume_importance', 0), match.get('job_importance', 0))
            importance_item = QTableWidgetItem(f"{importance:.2f}")
            table.setItem(row, 4, importance_item)
            
            # Status
            status_item = QTableWidgetItem("✓ Matched")
            status_item.setForeground(QColor(COLORS['success']))
            table.setItem(row, 5, status_item)
    
    def _populate_missing_table(self, table: QTableWidget, missing_keywords: List[Dict]):
        """Populate the missing keywords table."""
        table.setRowCount(len(missing_keywords))
        
        for row, keyword in enumerate(missing_keywords):
            # Missing keyword
            keyword_item = QTableWidgetItem(keyword['keyword'])
            keyword_item.setBackground(QColor(MATCH_COLORS['missing']))
            table.setItem(row, 0, keyword_item)
            
            # Importance
            importance_item = QTableWidgetItem(f"{keyword['importance']:.2f}")
            table.setItem(row, 1, importance_item)
            
            # Type
            type_item = QTableWidgetItem(keyword.get('type', 'Unknown'))
            table.setItem(row, 2, type_item)
            
            # Recommendation
            if keyword['importance'] >= 0.8:
                recommendation = "High Priority - Add to resume"
            elif keyword['importance'] >= 0.5:
                recommendation = "Medium Priority - Consider adding"
            else:
                recommendation = "Low Priority - Optional"
            
            rec_item = QTableWidgetItem(recommendation)
            table.setItem(row, 3, rec_item)
    
    def clear_results(self):
        """Clear all tables."""
        self.exact_table.setRowCount(0)
        self.fuzzy_table.setRowCount(0)
        self.partial_table.setRowCount(0)
        self.missing_table.setRowCount(0)


class ResultsWidget(QWidget):
    """Widget for displaying detailed analysis results."""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the detailed results interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Scores section
        self.scores_group = QGroupBox("Match Scores")
        scores_layout = QGridLayout(self.scores_group)
        
        self.score_labels = {}
        score_fields = [
            "overall_score", "match_percentage", "coverage_percentage",
            "resume_utilization", "exact_matches_count", "fuzzy_matches_count",
            "partial_matches_count"
        ]
        
        for i, field in enumerate(score_fields):
            label = QLabel(field.replace('_', ' ').title() + ":")
            value = QLabel("0")
            value.setStyleSheet(f"font-weight: bold; color: {COLORS['primary']};")
            
            scores_layout.addWidget(label, i // 2, (i % 2) * 2)
            scores_layout.addWidget(value, i // 2, (i % 2) * 2 + 1)
            
            self.score_labels[field] = value
        
        content_layout.addWidget(self.scores_group)
        
        # Summary section
        self.summary_group = QGroupBox("Analysis Summary")
        summary_layout = QVBoxLayout(self.summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        summary_layout.addWidget(self.summary_text)
        
        content_layout.addWidget(self.summary_group)
        
        # Recommendations section
        self.recommendations_group = QGroupBox("Recommendations")
        recommendations_layout = QVBoxLayout(self.recommendations_group)
        
        self.recommendations_list = QListWidget()
        recommendations_layout.addWidget(self.recommendations_list)
        
        content_layout.addWidget(self.recommendations_group)
        
        # Add stretch to push everything to the top
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
    
    def update_results(self, results: Dict):
        """Update the detailed results with analysis data."""
        match_results = results['match_results']
        scores = match_results['scores']
        summary = match_results['summary']
        
        # Update scores
        for field, label in self.score_labels.items():
            if field in scores:
                value = scores[field]
                if isinstance(value, float):
                    label.setText(f"{value:.1f}%")
                else:
                    label.setText(str(value))
        
        # Update summary
        summary_text = f"""
Overall Assessment: {summary['overall_assessment']}

High Importance Matches: {summary['high_importance_matches']}
Medium Importance Matches: {summary['medium_importance_matches']}
Low Importance Matches: {summary['low_importance_matches']}
Missing Keywords: {summary['missing_keywords_count']}

Total Resume Keywords: {results['total_resume_keywords']}
Total Job Keywords: {results['total_job_keywords']}
        """
        self.summary_text.setPlainText(summary_text.strip())
        
        # Update recommendations
        self.recommendations_list.clear()
        for recommendation in summary['recommendations']:
            item = QListWidgetItem(f"• {recommendation}")
            self.recommendations_list.addItem(item)
        
        self.logger.info("Detailed results updated")
    
    def clear_results(self):
        """Clear all results."""
        for label in self.score_labels.values():
            label.setText("0")
        
        self.summary_text.clear()
        self.recommendations_list.clear()


class InfographicWidget(QWidget):
    """Widget for displaying visual infographics of analysis results."""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the infographic interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Main score display
        self.score_group = QGroupBox("Overall Match Score")
        score_layout = QVBoxLayout(self.score_group)
        
        self.score_label = QLabel("0%")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet(f"""
            QLabel {{
                font-size: 48px;
                font-weight: bold;
                color: {COLORS['primary']};
                padding: 20px;
            }}
        """)
        score_layout.addWidget(self.score_label)
        
        self.score_description = QLabel("No analysis performed")
        self.score_description.setAlignment(Qt.AlignCenter)
        self.score_description.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {COLORS['gray']};
                padding: 10px;
            }}
        """)
        score_layout.addWidget(self.score_description)
        
        layout.addWidget(self.score_group)
        
        # Statistics grid
        self.stats_group = QGroupBox("Key Statistics")
        stats_layout = QGridLayout(self.stats_group)
        
        self.stats_labels = {}
        stat_fields = [
            ("resume_keywords", "Resume Keywords"),
            ("job_keywords", "Job Keywords"),
            ("exact_matches", "Exact Matches"),
            ("fuzzy_matches", "Fuzzy Matches"),
            ("partial_matches", "Partial Matches"),
            ("missing_keywords", "Missing Keywords")
        ]
        
        for i, (field, title) in enumerate(stat_fields):
            label = QLabel(title + ":")
            value = QLabel("0")
            value.setStyleSheet(f"font-weight: bold; color: {COLORS['primary']};")
            
            stats_layout.addWidget(label, i // 2, (i % 2) * 2)
            stats_layout.addWidget(value, i // 2, (i % 2) * 2 + 1)
            
            self.stats_labels[field] = value
        
        layout.addWidget(self.stats_group)
        
        # Progress bars
        self.progress_group = QGroupBox("Match Breakdown")
        progress_layout = QVBoxLayout(self.progress_group)
        
        self.progress_bars = {}
        progress_fields = [
            ("exact", "Exact Matches", MATCH_COLORS['exact']),
            ("fuzzy", "Fuzzy Matches", MATCH_COLORS['fuzzy']),
            ("partial", "Partial Matches", MATCH_COLORS['partial']),
            ("missing", "Missing", MATCH_COLORS['missing'])
        ]
        
        for field, title, color in progress_fields:
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 5, 0, 5)
            
            label = QLabel(title)
            label.setMinimumWidth(120)
            
            progress_bar = QProgressBar()
            progress_bar.setMaximum(100)
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {COLORS['gray']};
                    border-radius: 3px;
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 2px;
                }}
            """)
            
            percentage_label = QLabel("0%")
            percentage_label.setMinimumWidth(50)
            
            container_layout.addWidget(label)
            container_layout.addWidget(progress_bar)
            container_layout.addWidget(percentage_label)
            
            progress_layout.addWidget(container)
            
            self.progress_bars[field] = (progress_bar, percentage_label)
        
        layout.addWidget(self.progress_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def update_results(self, results: Dict):
        """Update the infographic with analysis results."""
        match_results = results['match_results']
        scores = match_results['scores']
        
        # Update main score
        overall_score = scores['overall_score']
        self.score_label.setText(f"{overall_score:.1f}%")
        
        # Update score description
        if overall_score >= 90:
            description = "Excellent Match"
            color = COLORS['success']
        elif overall_score >= 80:
            description = "Very Good Match"
            color = COLORS['success']
        elif overall_score >= 70:
            description = "Good Match"
            color = COLORS['info']
        elif overall_score >= 60:
            description = "Fair Match"
            color = COLORS['warning']
        elif overall_score >= 50:
            description = "Poor Match"
            color = COLORS['danger']
        else:
            description = "Very Poor Match"
            color = COLORS['danger']
        
        self.score_description.setText(description)
        self.score_description.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {color};
                padding: 10px;
            }}
        """)
        
        # Update statistics
        stats_data = {
            'resume_keywords': len(results['resume_keywords']),
            'job_keywords': len(results['job_keywords']),
            'exact_matches': scores['exact_matches_count'],
            'fuzzy_matches': scores['fuzzy_matches_count'],
            'partial_matches': scores['partial_matches_count'],
            'missing_keywords': len(match_results['missing_keywords'])
        }
        
        for field, value in stats_data.items():
            if field in self.stats_labels:
                self.stats_labels[field].setText(str(value))
        
        # Update progress bars
        total_job_keywords = len(results['job_keywords'])
        if total_job_keywords > 0:
            exact_pct = (scores['exact_matches_count'] / total_job_keywords) * 100
            fuzzy_pct = (scores['fuzzy_matches_count'] / total_job_keywords) * 100
            partial_pct = (scores['partial_matches_count'] / total_job_keywords) * 100
            missing_pct = (len(match_results['missing_keywords']) / total_job_keywords) * 100
            
            self.progress_bars['exact'][0].setValue(int(exact_pct))
            self.progress_bars['exact'][1].setText(f"{exact_pct:.1f}%")
            
            self.progress_bars['fuzzy'][0].setValue(int(fuzzy_pct))
            self.progress_bars['fuzzy'][1].setText(f"{fuzzy_pct:.1f}%")
            
            self.progress_bars['partial'][0].setValue(int(partial_pct))
            self.progress_bars['partial'][1].setText(f"{partial_pct:.1f}%")
            
            self.progress_bars['missing'][0].setValue(int(missing_pct))
            self.progress_bars['missing'][1].setText(f"{missing_pct:.1f}%")
        
        self.logger.info("Infographic updated with results")
    
    def clear_results(self):
        """Clear all infographic data."""
        self.score_label.setText("0%")
        self.score_description.setText("No analysis performed")
        self.score_description.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {COLORS['gray']};
                padding: 10px;
            }}
        """)
        
        for label in self.stats_labels.values():
            label.setText("0")
        
        for progress_bar, percentage_label in self.progress_bars.values():
            progress_bar.setValue(0)
            percentage_label.setText("0%")


class SettingsWidget(QWidget):
    """Widget for application settings and configuration."""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the settings interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Analysis settings
        analysis_group = QGroupBox("Analysis Settings")
        analysis_layout = QGridLayout(analysis_group)
        
        # Fuzzy match threshold
        analysis_layout.addWidget(QLabel("Fuzzy Match Threshold:"), 0, 0)
        self.fuzzy_threshold_slider = QSlider(Qt.Horizontal)
        self.fuzzy_threshold_slider.setRange(50, 100)
        self.fuzzy_threshold_slider.setValue(70)
        self.fuzzy_threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.fuzzy_threshold_slider.setTickInterval(10)
        analysis_layout.addWidget(self.fuzzy_threshold_slider, 0, 1)
        
        self.fuzzy_threshold_label = QLabel("70%")
        analysis_layout.addWidget(self.fuzzy_threshold_label, 0, 2)
        
        # Max keywords
        analysis_layout.addWidget(QLabel("Maximum Keywords:"), 1, 0)
        self.max_keywords_spin = QSpinBox()
        self.max_keywords_spin.setRange(50, 500)
        self.max_keywords_spin.setValue(100)
        analysis_layout.addWidget(self.max_keywords_spin, 1, 1)
        
        # Use spaCy
        self.use_spacy_checkbox = QCheckBox("Use spaCy for advanced NLP")
        self.use_spacy_checkbox.setChecked(True)
        analysis_layout.addWidget(self.use_spacy_checkbox, 2, 0, 1, 2)
        
        content_layout.addWidget(analysis_group)
        
        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QGridLayout(display_group)
        
        # Theme selection
        display_layout.addWidget(QLabel("Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        self.theme_combo.setCurrentText("Light")
        display_layout.addWidget(self.theme_combo, 0, 1)
        
        # Auto-save results
        self.auto_save_checkbox = QCheckBox("Auto-save analysis results")
        self.auto_save_checkbox.setChecked(True)
        display_layout.addWidget(self.auto_save_checkbox, 1, 0, 1, 2)
        
        content_layout.addWidget(display_group)
        
        # Add stretch to push everything to the top
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Connect signals
        self.fuzzy_threshold_slider.valueChanged.connect(self._on_fuzzy_threshold_changed)
    
    def _on_fuzzy_threshold_changed(self, value: int):
        """Handle fuzzy threshold slider changes."""
        self.fuzzy_threshold_label.setText(f"{value}%")
    
    def get_settings(self) -> Dict:
        """Get current settings."""
        return {
            'fuzzy_threshold': self.fuzzy_threshold_slider.value(),
            'max_keywords': self.max_keywords_spin.value(),
            'use_spacy': self.use_spacy_checkbox.isChecked(),
            'theme': self.theme_combo.currentText().lower(),
            'auto_save': self.auto_save_checkbox.isChecked()
        }
    
    def set_settings(self, settings: Dict):
        """Set settings from dictionary."""
        if 'fuzzy_threshold' in settings:
            self.fuzzy_threshold_slider.setValue(settings['fuzzy_threshold'])
        
        if 'max_keywords' in settings:
            self.max_keywords_spin.setValue(settings['max_keywords'])
        
        if 'use_spacy' in settings:
            self.use_spacy_checkbox.setChecked(settings['use_spacy'])
        
        if 'theme' in settings:
            theme = settings['theme'].title()
            if theme in ["Light", "Dark", "System"]:
                self.theme_combo.setCurrentText(theme)
        
        if 'auto_save' in settings:
            self.auto_save_checkbox.setChecked(settings['auto_save'])


class StatusWidget(QWidget):
    """Widget for displaying application status information."""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the status interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['success']};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.status_indicator)
        
        # Status text
        self.status_text = QLabel("Ready")
        self.status_text.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['gray']};
                font-size: 11px;
            }}
        """)
        layout.addWidget(self.status_text)
        
        # Memory usage
        self.memory_label = QLabel("Memory: 0 MB")
        self.memory_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['gray']};
                font-size: 11px;
            }}
        """)
        layout.addWidget(self.memory_label)
        
        # Add stretch to push everything to the right
        layout.addStretch()
    
    def set_status(self, status: str, color: str = COLORS['success']):
        """Set the status text and color."""
        self.status_text.setText(status)
        self.status_indicator.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
    
    def set_memory_usage(self, memory_mb: float):
        """Set the memory usage display."""
        self.memory_label.setText(f"Memory: {memory_mb:.1f} MB") 