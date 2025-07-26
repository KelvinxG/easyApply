#!/usr/bin/env python3
"""
Basic Usage Example for EasyApply

This script demonstrates how to use the core components of EasyApply
programmatically without the GUI.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.core.pdf_processor import PDFProcessor
from src.core.keyword_analyzer import KeywordAnalyzer
from src.core.matcher import KeywordMatcher
from src.utils.logger import setup_logging


def main():
    """Demonstrate basic usage of EasyApply components."""
    
    # Set up logging
    setup_logging()
    
    print("🚀 EasyApply - Basic Usage Example")
    print("=" * 50)
    
    # Sample job description
    job_description = """
    Software Engineer Position
    
    We are looking for a skilled Software Engineer with experience in:
    - Python programming
    - Web development with Django or Flask
    - Database design and SQL
    - Git version control
    - RESTful API development
    - Docker containerization
    - AWS cloud services
    - Agile development methodologies
    
    Required Skills:
    - 3+ years of Python development experience
    - Strong understanding of software design patterns
    - Experience with frontend technologies (HTML, CSS, JavaScript)
    - Knowledge of testing frameworks (pytest, unittest)
    - Familiarity with CI/CD pipelines
    
    Nice to Have:
    - Machine learning experience
    - React or Vue.js knowledge
    - Kubernetes experience
    - Microservices architecture
    """
    
    # Sample resume text (in real usage, this would come from PDF processing)
    resume_text = """
    John Doe - Software Engineer
    
    SUMMARY
    Experienced software engineer with 5 years of Python development experience.
    Skilled in web development, database design, and cloud technologies.
    
    SKILLS
    - Python, JavaScript, HTML, CSS
    - Django, Flask, React
    - PostgreSQL, MySQL, MongoDB
    - Git, Docker, AWS
    - REST APIs, Microservices
    - Unit testing, CI/CD
    
    EXPERIENCE
    Senior Developer at TechCorp (2020-2023)
    - Developed web applications using Python and Django
    - Implemented RESTful APIs and microservices
    - Used Docker for containerization and deployment
    - Collaborated with team using Git and Agile methodologies
    
    Junior Developer at StartupXYZ (2018-2020)
    - Built frontend applications with React
    - Worked with SQL databases and REST APIs
    - Participated in code reviews and testing
    """
    
    print("📄 Processing Resume Text...")
    
    # Initialize components
    pdf_processor = PDFProcessor()
    keyword_analyzer = KeywordAnalyzer()
    matcher = KeywordMatcher()
    
    # Clean the resume text
    cleaned_resume = pdf_processor.clean_text(resume_text)
    print(f"✅ Resume text cleaned ({len(cleaned_resume)} characters)")
    
    # Extract keywords from resume
    print("🔍 Extracting keywords from resume...")
    resume_keywords = keyword_analyzer.extract_keywords(cleaned_resume, max_keywords=50)
    print(f"✅ Extracted {len(resume_keywords)} keywords from resume")
    
    # Analyze job description
    print("📋 Analyzing job description...")
    job_analysis = keyword_analyzer.analyze_job_description(job_description)
    job_keywords = job_analysis['keywords']
    print(f"✅ Extracted {len(job_keywords)} keywords from job description")
    
    # Match keywords
    print("🔗 Matching keywords...")
    match_results = matcher.match_keywords(resume_keywords, job_keywords)
    
    # Display results
    print("\n📊 ANALYSIS RESULTS")
    print("=" * 50)
    
    scores = match_results['scores']
    print(f"Overall Match Score: {scores['overall_score']:.1f}%")
    print(f"Exact Matches: {scores['exact_matches_count']}")
    print(f"Fuzzy Matches: {scores['fuzzy_matches_count']}")
    print(f"Partial Matches: {scores['partial_matches_count']}")
    print(f"Missing Keywords: {len(match_results['missing_keywords'])}")
    
    # Show some exact matches
    if match_results['exact_matches']:
        print("\n✅ EXACT MATCHES:")
        for match in match_results['exact_matches'][:5]:  # Show first 5
            print(f"  • {match['resume_keyword']} ↔ {match['job_keyword']}")
    
    # Show some fuzzy matches
    if match_results['fuzzy_matches']:
        print("\n🔄 FUZZY MATCHES:")
        for match in match_results['fuzzy_matches'][:5]:  # Show first 5
            print(f"  • {match['resume_keyword']} ↔ {match['job_keyword']} ({match['ratio']}%)")
    
    # Show some missing keywords
    if match_results['missing_keywords']:
        print("\n❌ MISSING KEYWORDS (High Priority):")
        high_priority = [kw for kw in match_results['missing_keywords'] if kw['importance'] >= 0.8]
        for keyword in high_priority[:5]:  # Show first 5
            print(f"  • {keyword['keyword']} (Importance: {keyword['importance']:.2f})")
    
    # Show recommendations
    print("\n💡 RECOMMENDATIONS:")
    for recommendation in match_results['summary']['recommendations']:
        print(f"  • {recommendation}")
    
    print("\n🎉 Analysis complete!")
    print("\nTo use the full GUI application, run: python main.py")


if __name__ == "__main__":
    main() 