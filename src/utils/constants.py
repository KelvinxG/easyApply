"""
Application Constants

Contains all application-wide constants, configuration values, and settings.
"""

import os
from pathlib import Path

# Application Information
APP_NAME = "EasyApply"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Resume-Job Description Keyword Matching Application"
APP_AUTHOR = "EasyApply Team"
APP_EMAIL = "support@easyapply.com"

# File Paths
BASE_DIR = Path(__file__).parent.parent.parent
RESOURCES_DIR = BASE_DIR / "resources"
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = BASE_DIR / "temp"

# Supported File Formats
SUPPORTED_RESUME_FORMATS = [".pdf", ".docx", ".txt"]
SUPPORTED_EXPORT_FORMATS = [".pdf", ".xlsx", ".json", ".csv"]

# PDF Processing Settings
PDF_MAX_SIZE_MB = 50
PDF_PASSWORD_TIMEOUT = 30  # seconds

# Keyword Analysis Settings
MIN_KEYWORD_LENGTH = 3
MAX_KEYWORD_LENGTH = 50
MIN_FUZZY_MATCH_RATIO = 70  # percentage
EXACT_MATCH_WEIGHT = 1.0
FUZZY_MATCH_WEIGHT = 0.8
PARTIAL_MATCH_WEIGHT = 0.6

# NLTK Settings
NLTK_DATA_DIR = BASE_DIR / "nltk_data"
STOP_WORDS_LANGUAGE = "english"

# UI Settings
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
WINDOW_DEFAULT_WIDTH = 1400
WINDOW_DEFAULT_HEIGHT = 900

# Progress Bar Settings
PROGRESS_UPDATE_INTERVAL = 100  # milliseconds

# Database Settings
DATABASE_NAME = "easyapply.db"
DATABASE_VERSION = "1.0"

# Plugin Settings
PLUGIN_DIR = BASE_DIR / "plugins"
PLUGIN_CONFIG_FILE = "plugin_config.json"

# Export Settings
EXPORT_TEMPLATE_DIR = RESOURCES_DIR / "templates"
DEFAULT_REPORT_TEMPLATE = "default_report.html"

# Error Messages
ERROR_MESSAGES = {
    "file_not_found": "File not found: {}",
    "invalid_file_format": "Invalid file format. Supported formats: {}",
    "file_too_large": "File is too large. Maximum size: {} MB",
    "password_protected": "PDF is password protected",
    "corrupted_file": "File appears to be corrupted",
    "processing_error": "Error processing file: {}",
    "no_keywords_found": "No keywords found in the document",
    "invalid_job_description": "Please enter a valid job description",
    "database_error": "Database error: {}",
    "plugin_error": "Plugin error: {}",
}

# Success Messages
SUCCESS_MESSAGES = {
    "file_uploaded": "File uploaded successfully",
    "analysis_complete": "Analysis completed successfully",
    "export_complete": "Export completed successfully",
    "settings_saved": "Settings saved successfully",
}

# Color Schemes
COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "success": "#28A745",
    "warning": "#FFC107",
    "danger": "#DC3545",
    "info": "#17A2B8",
    "light": "#F8F9FA",
    "dark": "#343A40",
    "white": "#FFFFFF",
    "black": "#000000",
    "gray": "#6C757D",
    "light_gray": "#E9ECEF",
}

# Match Status Colors
MATCH_COLORS = {
    "exact": "#28A745",    # Green
    "fuzzy": "#FFC107",    # Yellow
    "partial": "#FD7E14",  # Orange
    "missing": "#DC3545",  # Red
    "neutral": "#6C757D",  # Gray
}

# Default Keywords by Industry
DEFAULT_KEYWORDS = {
    "software_development": [
        "Python", "Java", "JavaScript", "React", "Angular", "Vue.js",
        "Node.js", "Django", "Flask", "Spring", "Docker", "Kubernetes",
        "AWS", "Azure", "GCP", "Git", "GitHub", "CI/CD", "Agile",
        "Scrum", "REST API", "GraphQL", "SQL", "NoSQL", "MongoDB",
        "PostgreSQL", "MySQL", "Redis", "Microservices", "DevOps"
    ],
    "data_science": [
        "Python", "R", "SQL", "Pandas", "NumPy", "Matplotlib",
        "Seaborn", "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
        "Jupyter", "Tableau", "Power BI", "Apache Spark", "Hadoop",
        "Machine Learning", "Deep Learning", "Neural Networks",
        "Statistical Analysis", "Data Visualization", "ETL", "Big Data"
    ],
    "marketing": [
        "Digital Marketing", "SEO", "SEM", "Google Ads", "Facebook Ads",
        "Social Media Marketing", "Content Marketing", "Email Marketing",
        "Marketing Automation", "Analytics", "Google Analytics",
        "Conversion Optimization", "Brand Management", "Market Research",
        "Customer Acquisition", "Lead Generation", "CRM", "Salesforce"
    ]
}

# Configuration Keys
CONFIG_KEYS = {
    "theme": "app_theme",
    "language": "app_language",
    "auto_save": "auto_save_enabled",
    "auto_save_interval": "auto_save_interval",
    "recent_files": "recent_files",
    "default_export_format": "default_export_format",
    "fuzzy_match_threshold": "fuzzy_match_threshold",
    "max_recent_files": "max_recent_files",
}

# Default Configuration Values
DEFAULT_CONFIG = {
    "app_theme": "light",
    "app_language": "en",
    "auto_save_enabled": True,
    "auto_save_interval": 300,  # 5 minutes
    "recent_files": [],
    "default_export_format": "pdf",
    "fuzzy_match_threshold": 70,
    "max_recent_files": 10,
} 