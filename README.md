# EasyApply - Resume-Job Description Keyword Matcher

A comprehensive PySide6 desktop application for analyzing resume keywords against job descriptions to provide matching insights and scoring.

## 🚀 Features

- **PDF Resume Processing**: Extract text from PDF resumes using PyPDF2 and pdfplumber
- **Advanced Keyword Analysis**: Use NLTK and spaCy for natural language processing
- **Fuzzy String Matching**: Implement fuzzy matching with configurable thresholds
- **Visual Results**: Modern UI with infographics, progress bars, and detailed tables
- **Multiple Export Formats**: Save results as PDF, Excel, JSON, or CSV
- **Industry-Specific Analysis**: Pre-built keyword sets for different job sectors
- **Drag & Drop Support**: Easy file upload with drag and drop functionality
- **Real-time Analysis**: Background processing with progress indicators

## 📋 Requirements

- Python 3.8 or higher
- PySide6 (Qt6 bindings)
- PDF processing libraries (PyPDF2, pdfplumber)
- NLP libraries (NLTK, spaCy)
- Data processing (pandas, numpy)
- Visualization (matplotlib, pyqtgraph)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/easyapply.git
cd easyapply
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data (Optional)

```python
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"
```

### 5. Download spaCy Model (Optional)

```bash
python -m spacy download en_core_web_sm
```

## 🚀 Quick Start

### Running the Application

```bash
python main.py
```

### Basic Usage

1. **Upload Resume**: Click "Browse Files" or drag and drop a PDF resume
2. **Enter Job Description**: Paste the job description in the text area
3. **Select Industry**: Choose the relevant industry from the dropdown
4. **Analyze**: Click "Analyze Resume" to start the keyword matching
5. **Review Results**: View the analysis in the Overview, Keywords, and Detailed Analysis tabs

## 📊 Understanding Results

### Match Score
- **90%+**: Excellent Match
- **80-89%**: Very Good Match
- **70-79%**: Good Match
- **60-69%**: Fair Match
- **50-59%**: Poor Match
- **<50%**: Very Poor Match

### Keyword Categories
- **Exact Matches**: Perfect keyword matches (green)
- **Fuzzy Matches**: Similar keywords with high confidence (yellow)
- **Partial Matches**: Substring or word-level matches (orange)
- **Missing Keywords**: Keywords in job description not found in resume (red)

## 🏗️ Project Structure

```
easyapply/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── src/                   # Source code
│   ├── gui/              # PySide6 UI components
│   │   ├── main_window.py # Main application window
│   │   ├── widgets.py     # Custom widgets
│   │   └── styles.py      # Application styling
│   ├── core/             # Business logic
│   │   ├── pdf_processor.py    # PDF text extraction
│   │   ├── keyword_analyzer.py # Keyword analysis
│   │   └── matcher.py          # Keyword matching
│   ├── utils/            # Helper functions
│   │   ├── constants.py  # Application constants
│   │   ├── logger.py     # Logging configuration
│   │   ├── helpers.py    # Utility functions
│   │   └── validators.py # Input validation
│   ├── data/             # Data models and persistence
│   └── plugins/          # Extensible analyzer modules
├── tests/                # Unit and integration tests
├── docs/                 # Documentation
├── resources/            # Icons, stylesheets, sample files
├── scripts/              # Build and deployment scripts
└── examples/             # Usage examples and tutorials
```

## 🔧 Configuration

### Application Settings

Access settings through the "Settings" tab in the application:

- **Fuzzy Match Threshold**: Adjust sensitivity for fuzzy matching (50-100%)
- **Maximum Keywords**: Set limit for keyword extraction (50-500)
- **NLP Engine**: Choose between spaCy (advanced) and NLTK (basic)
- **Theme**: Select Light, Dark, or System theme
- **Auto-save**: Enable automatic result saving

### Custom Keywords

Add industry-specific keywords in the settings:

```python
# Example: Adding custom keywords for a new industry
analyzer = KeywordAnalyzer()
analyzer.add_custom_keywords("cybersecurity", [
    "penetration testing", "vulnerability assessment", "SIEM",
    "firewall", "encryption", "incident response"
])
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-qt pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_pdf_processor.py
```

## 📚 API Documentation

### Core Classes

#### PDFProcessor
```python
from src.core.pdf_processor import PDFProcessor

processor = PDFProcessor()
result = processor.process_pdf("resume.pdf")
text = processor.clean_text(result['text'])
```

#### KeywordAnalyzer
```python
from src.core.keyword_analyzer import KeywordAnalyzer

analyzer = KeywordAnalyzer()
keywords = analyzer.extract_keywords(text)
job_analysis = analyzer.analyze_job_description(job_text)
```

#### KeywordMatcher
```python
from src.core.matcher import KeywordMatcher

matcher = KeywordMatcher(fuzzy_threshold=70)
results = matcher.match_keywords(resume_keywords, job_keywords)
```

## 🔌 Extending the Application

### Adding New Analyzers

Create custom analyzers by extending the base class:

```python
from src.plugins.base import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    def analyze(self, text: str) -> List[Dict]:
        # Custom analysis logic
        return keywords
```

### Adding New Export Formats

Implement custom export handlers:

```python
def export_to_custom_format(results: Dict, file_path: str):
    # Custom export logic
    pass
```

## 🐛 Troubleshooting

### Common Issues

1. **PDF Processing Errors**
   - Ensure PDF is not password-protected
   - Check file size (max 50MB)
   - Verify PDF is not corrupted

2. **NLP Library Issues**
   - Install required NLTK data: `python -c "import nltk; nltk.download('all')"`
   - Download spaCy model: `python -m spacy download en_core_web_sm`

3. **Performance Issues**
   - Reduce maximum keywords in settings
   - Use basic NLP engine instead of spaCy
   - Process smaller PDF files

### Logs

Check application logs in the `logs/` directory for detailed error information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest`
6. Commit your changes: `git commit -m 'Add feature'`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run code formatting
black src/
flake8 src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- PySide6 team for the Qt6 Python bindings
- NLTK and spaCy teams for NLP capabilities
- PyPDF2 and pdfplumber teams for PDF processing
- All contributors and users of EasyApply

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/easyapply/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/easyapply/discussions)
- **Email**: tearteamoguy@gmail.com // right now it is a personal email

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added dark theme and improved UI
- **v1.2.0** - Enhanced keyword analysis and export features

---

**EasyApply** - Making resume analysis simple and effective! 🚀 
