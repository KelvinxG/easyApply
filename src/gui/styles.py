"""
Application Styles

Contains all styling definitions for the EasyApply application,
providing a modern, professional appearance across all components.
"""

from src.utils.constants import COLORS


def get_application_style() -> str:
    """
    Get the complete application stylesheet.
    
    Returns:
        str: Complete CSS stylesheet for the application
    """
    return f"""
    /* Main Application Styles */
    QMainWindow {{
        background-color: {COLORS['light']};
        color: {COLORS['dark']};
    }}
    
    /* Menu Bar */
    QMenuBar {{
        background-color: {COLORS['white']};
        border-bottom: 1px solid {COLORS['light_gray']};
        padding: 5px;
    }}
    
    QMenuBar::item {{
        background-color: transparent;
        padding: 8px 12px;
        border-radius: 4px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {COLORS['primary']};
        color: {COLORS['white']};
    }}
    
    QMenu {{
        background-color: {COLORS['white']};
        border: 1px solid {COLORS['light_gray']};
        border-radius: 6px;
        padding: 5px;
    }}
    
    QMenu::item {{
        padding: 8px 20px;
        border-radius: 4px;
    }}
    
    QMenu::item:selected {{
        background-color: {COLORS['primary']};
        color: {COLORS['white']};
    }}
    
    /* Toolbar */
    QToolBar {{
        background-color: {COLORS['white']};
        border-bottom: 1px solid {COLORS['light_gray']};
        spacing: 5px;
        padding: 5px;
    }}
    
    QToolBar::separator {{
        background-color: {COLORS['light_gray']};
        width: 1px;
        margin: 5px;
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {COLORS['white']};
        border-top: 1px solid {COLORS['light_gray']};
        padding: 5px;
    }}
    
    /* Group Boxes */
    QGroupBox {{
        font-weight: bold;
        border: 2px solid {COLORS['light_gray']};
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 10px;
        background-color: {COLORS['white']};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 8px 0 8px;
        color: {COLORS['primary']};
        font-size: 14px;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {COLORS['primary']};
        color: {COLORS['white']};
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 13px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['secondary']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['dark']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['gray']};
        color: {COLORS['light_gray']};
    }}
    
    /* Secondary Button Style */
    QPushButton[class="secondary"] {{
        background-color: {COLORS['light_gray']};
        color: {COLORS['dark']};
        border: 1px solid {COLORS['gray']};
    }}
    
    QPushButton[class="secondary"]:hover {{
        background-color: {COLORS['gray']};
        color: {COLORS['white']};
    }}
    
    /* Success Button Style */
    QPushButton[class="success"] {{
        background-color: {COLORS['success']};
    }}
    
    QPushButton[class="success"]:hover {{
        background-color: #218838;
    }}
    
    /* Warning Button Style */
    QPushButton[class="warning"] {{
        background-color: {COLORS['warning']};
        color: {COLORS['dark']};
    }}
    
    QPushButton[class="warning"]:hover {{
        background-color: #e0a800;
    }}
    
    /* Danger Button Style */
    QPushButton[class="danger"] {{
        background-color: {COLORS['danger']};
    }}
    
    QPushButton[class="danger"]:hover {{
        background-color: #c82333;
    }}
    
    /* Text Inputs */
    QTextEdit, QPlainTextEdit {{
        background-color: {COLORS['white']};
        border: 2px solid {COLORS['light_gray']};
        border-radius: 6px;
        padding: 8px;
        font-size: 13px;
        selection-background-color: {COLORS['primary']};
    }}
    
    QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {COLORS['primary']};
    }}
    
    QLineEdit {{
        background-color: {COLORS['white']};
        border: 2px solid {COLORS['light_gray']};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        selection-background-color: {COLORS['primary']};
    }}
    
    QLineEdit:focus {{
        border-color: {COLORS['primary']};
    }}
    
    /* Combo Boxes */
    QComboBox {{
        background-color: {COLORS['white']};
        border: 2px solid {COLORS['light_gray']};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        min-width: 100px;
    }}
    
    QComboBox:focus {{
        border-color: {COLORS['primary']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {COLORS['gray']};
        margin-right: 5px;
    }}
    
    QComboBox::down-arrow:on {{
        border-top-color: {COLORS['primary']};
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['white']};
        border: 1px solid {COLORS['light_gray']};
        border-radius: 6px;
        selection-background-color: {COLORS['primary']};
        selection-color: {COLORS['white']};
    }}
    
    /* Spin Boxes */
    QSpinBox, QDoubleSpinBox {{
        background-color: {COLORS['white']};
        border: 2px solid {COLORS['light_gray']};
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {COLORS['primary']};
    }}
    
    QSpinBox::up-button, QDoubleSpinBox::up-button,
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        background-color: {COLORS['light_gray']};
        border: none;
        border-radius: 3px;
        margin: 2px;
    }}
    
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background-color: {COLORS['gray']};
    }}
    
    /* Check Boxes */
    QCheckBox {{
        spacing: 8px;
        font-size: 13px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {COLORS['gray']};
        border-radius: 4px;
        background-color: {COLORS['white']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['primary']};
        border-color: {COLORS['primary']};
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {COLORS['primary']};
    }}
    
    /* Sliders */
    QSlider::groove:horizontal {{
        border: 1px solid {COLORS['light_gray']};
        height: 8px;
        background-color: {COLORS['light_gray']};
        border-radius: 4px;
        margin: 2px 0;
    }}
    
    QSlider::handle:horizontal {{
        background-color: {COLORS['primary']};
        border: 2px solid {COLORS['primary']};
        width: 18px;
        height: 18px;
        border-radius: 9px;
        margin: -5px 0;
    }}
    
    QSlider::handle:horizontal:hover {{
        background-color: {COLORS['secondary']};
        border-color: {COLORS['secondary']};
    }}
    
    QSlider::sub-page:horizontal {{
        background-color: {COLORS['primary']};
        border-radius: 4px;
    }}
    
    /* Progress Bars */
    QProgressBar {{
        border: 1px solid {COLORS['light_gray']};
        border-radius: 6px;
        text-align: center;
        background-color: {COLORS['light_gray']};
        font-weight: bold;
    }}
    
    QProgressBar::chunk {{
        background-color: {COLORS['primary']};
        border-radius: 5px;
    }}
    
    /* Tables */
    QTableWidget {{
        background-color: {COLORS['white']};
        border: 1px solid {COLORS['light_gray']};
        border-radius: 6px;
        gridline-color: {COLORS['light_gray']};
        selection-background-color: {COLORS['primary']};
        selection-color: {COLORS['white']};
    }}
    
    QTableWidget::item {{
        padding: 8px;
        border: none;
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLORS['primary']};
        color: {COLORS['white']};
    }}
    
    QHeaderView::section {{
        background-color: {COLORS['light_gray']};
        padding: 8px;
        border: none;
        border-right: 1px solid {COLORS['gray']};
        border-bottom: 1px solid {COLORS['gray']};
        font-weight: bold;
    }}
    
    QHeaderView::section:hover {{
        background-color: {COLORS['gray']};
        color: {COLORS['white']};
    }}
    
    /* Tab Widgets */
    QTabWidget::pane {{
        border: 1px solid {COLORS['light_gray']};
        border-radius: 6px;
        background-color: {COLORS['white']};
    }}
    
    QTabBar::tab {{
        background-color: {COLORS['light_gray']};
        color: {COLORS['dark']};
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-weight: bold;
    }}
    
    QTabBar::tab:selected {{
        background-color: {COLORS['primary']};
        color: {COLORS['white']};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {COLORS['gray']};
        color: {COLORS['white']};
    }}
    
    /* List Widgets */
    QListWidget {{
        background-color: {COLORS['white']};
        border: 1px solid {COLORS['light_gray']};
        border-radius: 6px;
        padding: 5px;
    }}
    
    QListWidget::item {{
        padding: 8px;
        border-radius: 4px;
        margin: 2px 0;
    }}
    
    QListWidget::item:selected {{
        background-color: {COLORS['primary']};
        color: {COLORS['white']};
    }}
    
    QListWidget::item:hover:!selected {{
        background-color: {COLORS['light_gray']};
    }}
    
    /* Scroll Areas */
    QScrollArea {{
        border: 1px solid {COLORS['light_gray']};
        border-radius: 6px;
        background-color: {COLORS['white']};
    }}
    
    /* Scroll Bars */
    QScrollBar:vertical {{
        background-color: {COLORS['light_gray']};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['gray']};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['primary']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: {COLORS['light_gray']};
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['gray']};
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['primary']};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* Splitter */
    QSplitter::handle {{
        background-color: {COLORS['light_gray']};
    }}
    
    QSplitter::handle:horizontal {{
        width: 2px;
    }}
    
    QSplitter::handle:vertical {{
        height: 2px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {COLORS['primary']};
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS['dark']};
        font-size: 13px;
    }}
    
    QLabel[class="title"] {{
        font-size: 18px;
        font-weight: bold;
        color: {COLORS['primary']};
    }}
    
    QLabel[class="subtitle"] {{
        font-size: 14px;
        font-weight: bold;
        color: {COLORS['secondary']};
    }}
    
    QLabel[class="success"] {{
        color: {COLORS['success']};
    }}
    
    QLabel[class="warning"] {{
        color: {COLORS['warning']};
    }}
    
    QLabel[class="danger"] {{
        color: {COLORS['danger']};
    }}
    
    QLabel[class="info"] {{
        color: {COLORS['info']};
    }}
    
    /* Frames */
    QFrame {{
        background-color: {COLORS['white']};
    }}
    
    QFrame[class="separator"] {{
        background-color: {COLORS['light_gray']};
        max-height: 1px;
    }}
    
    /* Message Boxes */
    QMessageBox {{
        background-color: {COLORS['white']};
    }}
    
    QMessageBox QPushButton {{
        min-width: 80px;
        min-height: 30px;
    }}
    
    /* File Dialog */
    QFileDialog {{
        background-color: {COLORS['white']};
    }}
    
    QFileDialog QListView, QFileDialog QTreeView {{
        background-color: {COLORS['white']};
        border: 1px solid {COLORS['light_gray']};
        border-radius: 6px;
    }}
    
    /* Tool Tips */
    QToolTip {{
        background-color: {COLORS['dark']};
        color: {COLORS['white']};
        border: 1px solid {COLORS['dark']};
        border-radius: 4px;
        padding: 5px;
        font-size: 12px;
    }}
    
    /* Focus Indicators */
    *:focus {{
        outline: 2px solid {COLORS['primary']};
        outline-offset: 2px;
    }}
    
    /* Disabled State */
    *:disabled {{
        opacity: 0.6;
    }}
    """


def get_dark_theme_style() -> str:
    """
    Get the dark theme stylesheet.
    
    Returns:
        str: Dark theme CSS stylesheet
    """
    # Dark theme colors
    dark_colors = {
        'background': '#2b2b2b',
        'surface': '#3c3c3c',
        'primary': '#4a9eff',
        'secondary': '#6c757d',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8',
        'text': '#ffffff',
        'text_secondary': '#b0b0b0',
        'border': '#555555',
        'border_light': '#444444'
    }
    
    return f"""
    /* Dark Theme Styles */
    QMainWindow {{
        background-color: {dark_colors['background']};
        color: {dark_colors['text']};
    }}
    
    QWidget {{
        background-color: {dark_colors['background']};
        color: {dark_colors['text']};
    }}
    
    QGroupBox {{
        background-color: {dark_colors['surface']};
        border-color: {dark_colors['border']};
        color: {dark_colors['text']};
    }}
    
    QTextEdit, QPlainTextEdit, QLineEdit {{
        background-color: {dark_colors['surface']};
        border-color: {dark_colors['border']};
        color: {dark_colors['text']};
    }}
    
    QComboBox, QSpinBox, QDoubleSpinBox {{
        background-color: {dark_colors['surface']};
        border-color: {dark_colors['border']};
        color: {dark_colors['text']};
    }}
    
    QTableWidget, QListWidget {{
        background-color: {dark_colors['surface']};
        border-color: {dark_colors['border']};
        color: {dark_colors['text']};
        gridline-color: {dark_colors['border']};
    }}
    
    QHeaderView::section {{
        background-color: {dark_colors['border']};
        color: {dark_colors['text']};
        border-color: {dark_colors['border_light']};
    }}
    
    QTabWidget::pane {{
        background-color: {dark_colors['surface']};
        border-color: {dark_colors['border']};
    }}
    
    QTabBar::tab {{
        background-color: {dark_colors['border']};
        color: {dark_colors['text']};
    }}
    
    QTabBar::tab:selected {{
        background-color: {dark_colors['primary']};
        color: {dark_colors['text']};
    }}
    
    QScrollBar:vertical, QScrollBar:horizontal {{
        background-color: {dark_colors['border']};
    }}
    
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
        background-color: {dark_colors['secondary']};
    }}
    
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
        background-color: {dark_colors['primary']};
    }}
    """


def get_compact_style() -> str:
    """
    Get a compact stylesheet for smaller screens.
    
    Returns:
        str: Compact CSS stylesheet
    """
    return f"""
    /* Compact Style Overrides */
    QGroupBox {{
        margin-top: 5px;
        padding-top: 5px;
    }}
    
    QGroupBox::title {{
        font-size: 12px;
    }}
    
    QPushButton {{
        padding: 6px 12px;
        font-size: 12px;
    }}
    
    QTextEdit, QPlainTextEdit, QLineEdit {{
        padding: 6px;
        font-size: 12px;
    }}
    
    QComboBox, QSpinBox, QDoubleSpinBox {{
        padding: 6px 10px;
        font-size: 12px;
    }}
    
    QTableWidget::item {{
        padding: 4px;
    }}
    
    QHeaderView::section {{
        padding: 4px;
        font-size: 12px;
    }}
    
    QTabBar::tab {{
        padding: 6px 12px;
        font-size: 12px;
    }}
    
    QLabel {{
        font-size: 12px;
    }}
    """ 