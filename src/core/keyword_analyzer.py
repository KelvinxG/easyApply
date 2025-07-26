"""
Keyword Analysis Module

Handles keyword extraction, processing, and analysis from resume text and job descriptions.
Uses NLTK and spaCy for natural language processing and advanced text analysis.
"""

import logging
import re
from typing import List, Dict, Set, Tuple, Optional
from collections import Counter, defaultdict
import string

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer, PorterStemmer
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available, using basic text processing")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available, using NLTK for NLP")

from src.utils.constants import (
    MIN_KEYWORD_LENGTH, MAX_KEYWORD_LENGTH, STOP_WORDS_LANGUAGE,
    DEFAULT_KEYWORDS, NLTK_DATA_DIR
)
from src.utils.logger import get_logger


class KeywordAnalyzer:
    """
    Keyword analysis class for extracting and processing keywords from text.
    
    Supports both NLTK and spaCy for natural language processing,
    with fallback to basic text processing if neither is available.
    """
    
    def __init__(self, use_spacy: bool = True):
        """
        Initialize the keyword analyzer.
        
        Args:
            use_spacy (bool): Whether to use spaCy for advanced NLP (default: True)
        """
        self.logger = get_logger(__name__)
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        
        # Initialize NLP components
        self._initialize_nlp()
        
        # Load stop words
        self.stop_words = self._load_stop_words()
        
        # Initialize stemmers and lemmatizers
        self._initialize_processors()
        
        # Industry-specific keyword sets
        self.industry_keywords = DEFAULT_KEYWORDS
    
    def _initialize_nlp(self):
        """Initialize NLP components (NLTK and/or spaCy)."""
        if self.use_spacy:
            try:
                # Try to load English model
                self.nlp = spacy.load("en_core_web_sm")
                self.logger.info("spaCy English model loaded successfully")
            except OSError:
                self.logger.warning("spaCy English model not found, downloading...")
                try:
                    spacy.cli.download("en_core_web_sm")
                    self.nlp = spacy.load("en_core_web_sm")
                    self.logger.info("spaCy English model downloaded and loaded")
                except Exception as e:
                    self.logger.error(f"Failed to load spaCy model: {e}")
                    self.use_spacy = False
        
        if not self.use_spacy and NLTK_AVAILABLE:
            self._download_nltk_data()
    
    def _download_nltk_data(self):
        """Download required NLTK data."""
        try:
            nltk.data.path.append(str(NLTK_DATA_DIR))
            
            # Download required NLTK data
            required_packages = ['stopwords', 'punkt', 'averaged_perceptron_tagger', 'wordnet']
            for package in required_packages:
                try:
                    nltk.data.find(f'tokenizers/{package}')
                except LookupError:
                    nltk.download(package, download_dir=str(NLTK_DATA_DIR))
                    self.logger.info(f"Downloaded NLTK package: {package}")
        except Exception as e:
            self.logger.error(f"Error downloading NLTK data: {e}")
    
    def _load_stop_words(self) -> Set[str]:
        """Load stop words for filtering."""
        stop_words = set()
        
        if NLTK_AVAILABLE:
            try:
                stop_words.update(stopwords.words(STOP_WORDS_LANGUAGE))
            except Exception as e:
                self.logger.warning(f"Could not load NLTK stop words: {e}")
        
        # Add custom stop words
        custom_stops = {
            'resume', 'cv', 'curriculum', 'vitae', 'experience', 'education',
            'skills', 'work', 'job', 'position', 'role', 'responsibilities',
            'duties', 'achievements', 'accomplishments', 'projects', 'team',
            'company', 'organization', 'employer', 'employee', 'candidate',
            'applicant', 'professional', 'career', 'employment', 'workplace'
        }
        stop_words.update(custom_stops)
        
        return stop_words
    
    def _initialize_processors(self):
        """Initialize text processors (stemmers, lemmatizers)."""
        if NLTK_AVAILABLE:
            self.lemmatizer = WordNetLemmatizer()
            self.stemmer = PorterStemmer()
        else:
            self.lemmatizer = None
            self.stemmer = None
    
    def extract_keywords(self, text: str, max_keywords: int = 100) -> List[Dict[str, any]]:
        """
        Extract keywords from text with various analysis methods.
        
        Args:
            text (str): Input text to analyze
            max_keywords (int): Maximum number of keywords to return
            
        Returns:
            List[Dict[str, any]]: List of keyword dictionaries with metadata
        """
        if not text or not text.strip():
            return []
        
        self.logger.info(f"Extracting keywords from text ({len(text)} characters)")
        
        # Clean and preprocess text
        cleaned_text = self._preprocess_text(text)
        
        # Extract keywords using different methods
        keywords = []
        
        if self.use_spacy:
            keywords.extend(self._extract_with_spacy(cleaned_text))
        elif NLTK_AVAILABLE:
            keywords.extend(self._extract_with_nltk(cleaned_text))
        else:
            keywords.extend(self._extract_basic(cleaned_text))
        
        # Post-process and rank keywords
        processed_keywords = self._post_process_keywords(keywords)
        
        # Sort by importance and limit results
        sorted_keywords = sorted(
            processed_keywords, 
            key=lambda x: x.get('importance', 0), 
            reverse=True
        )[:max_keywords]
        
        self.logger.info(f"Extracted {len(sorted_keywords)} keywords")
        return sorted_keywords
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for keyword extraction.
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]\{\}]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_with_spacy(self, text: str) -> List[Dict[str, any]]:
        """
        Extract keywords using spaCy NLP.
        
        Args:
            text (str): Preprocessed text
            
        Returns:
            List[Dict[str, any]]: Extracted keywords with metadata
        """
        keywords = []
        doc = self.nlp(text)
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'PERSON', 'WORK_OF_ART']:
                keywords.append({
                    'text': ent.text,
                    'type': 'entity',
                    'entity_type': ent.label_,
                    'importance': 0.9,
                    'position': ent.start_char
                })
        
        # Extract noun phrases and important tokens
        for chunk in doc.noun_chunks:
            if len(chunk.text) >= MIN_KEYWORD_LENGTH:
                keywords.append({
                    'text': chunk.text,
                    'type': 'noun_phrase',
                    'importance': 0.8,
                    'position': chunk.start_char
                })
        
        # Extract individual important tokens
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                len(token.text) >= MIN_KEYWORD_LENGTH and
                token.text.lower() not in self.stop_words):
                
                keywords.append({
                    'text': token.text,
                    'type': 'token',
                    'pos': token.pos_,
                    'importance': 0.7,
                    'position': token.idx
                })
        
        return keywords
    
    def _extract_with_nltk(self, text: str) -> List[Dict[str, any]]:
        """
        Extract keywords using NLTK.
        
        Args:
            text (str): Preprocessed text
            
        Returns:
            List[Dict[str, any]]: Extracted keywords with metadata
        """
        keywords = []
        
        # Tokenize text
        tokens = word_tokenize(text)
        
        # POS tagging
        pos_tags = pos_tag(tokens)
        
        # Extract important words based on POS
        for token, pos in pos_tags:
            if (pos.startswith(('NN', 'JJ', 'VB')) and  # Nouns, adjectives, verbs
                len(token) >= MIN_KEYWORD_LENGTH and
                token.lower() not in self.stop_words):
                
                # Lemmatize token
                if self.lemmatizer:
                    lemma = self.lemmatizer.lemmatize(token.lower())
                else:
                    lemma = token.lower()
                
                keywords.append({
                    'text': token,
                    'lemma': lemma,
                    'type': 'token',
                    'pos': pos,
                    'importance': 0.7
                })
        
        return keywords
    
    def _extract_basic(self, text: str) -> List[Dict[str, any]]:
        """
        Basic keyword extraction without advanced NLP.
        
        Args:
            text (str): Preprocessed text
            
        Returns:
            List[Dict[str, any]]: Extracted keywords with metadata
        """
        keywords = []
        
        # Simple word tokenization
        words = text.split()
        
        # Filter and process words
        for word in words:
            if (len(word) >= MIN_KEYWORD_LENGTH and
                word.lower() not in self.stop_words and
                not word.isdigit()):
                
                keywords.append({
                    'text': word,
                    'type': 'basic',
                    'importance': 0.5
                })
        
        return keywords
    
    def _post_process_keywords(self, keywords: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Post-process extracted keywords.
        
        Args:
            keywords (List[Dict[str, any]]): Raw extracted keywords
            
        Returns:
            List[Dict[str, any]]: Processed keywords
        """
        processed = []
        keyword_counts = Counter()
        
        # Count occurrences and normalize
        for keyword in keywords:
            text = keyword['text'].lower()
            keyword_counts[text] += 1
        
        # Process each keyword
        for keyword in keywords:
            text = keyword['text']
            normalized_text = text.lower()
            
            # Skip if too short or too long
            if len(text) < MIN_KEYWORD_LENGTH or len(text) > MAX_KEYWORD_LENGTH:
                continue
            
            # Calculate frequency-based importance
            frequency = keyword_counts[normalized_text]
            base_importance = keyword.get('importance', 0.5)
            
            # Adjust importance based on frequency
            frequency_boost = min(frequency * 0.1, 0.3)
            final_importance = base_importance + frequency_boost
            
            # Create processed keyword
            processed_keyword = {
                'text': text,
                'normalized': normalized_text,
                'type': keyword.get('type', 'unknown'),
                'importance': final_importance,
                'frequency': frequency,
                'entity_type': keyword.get('entity_type'),
                'pos': keyword.get('pos'),
                'lemma': keyword.get('lemma', normalized_text)
            }
            
            processed.append(processed_keyword)
        
        # Remove duplicates based on normalized text
        seen = set()
        unique_keywords = []
        for keyword in processed:
            if keyword['normalized'] not in seen:
                seen.add(keyword['normalized'])
                unique_keywords.append(keyword)
        
        return unique_keywords
    
    def analyze_job_description(self, job_text: str) -> Dict[str, any]:
        """
        Analyze job description to extract key requirements and skills.
        
        Args:
            job_text (str): Job description text
            
        Returns:
            Dict[str, any]: Analysis results
        """
        self.logger.info("Analyzing job description")
        
        # Extract keywords
        keywords = self.extract_keywords(job_text)
        
        # Categorize keywords by type
        categorized = self._categorize_keywords(keywords)
        
        # Identify required vs preferred skills
        requirements = self._identify_requirements(job_text, keywords)
        
        return {
            'keywords': keywords,
            'categorized': categorized,
            'requirements': requirements,
            'total_keywords': len(keywords),
            'analysis_complete': True
        }
    
    def _categorize_keywords(self, keywords: List[Dict[str, any]]) -> Dict[str, List[str]]:
        """
        Categorize keywords by type (skills, technologies, etc.).
        
        Args:
            keywords (List[Dict[str, any]]): List of keywords
            
        Returns:
            Dict[str, List[str]]: Categorized keywords
        """
        categories = {
            'technical_skills': [],
            'soft_skills': [],
            'technologies': [],
            'tools': [],
            'languages': [],
            'certifications': [],
            'industries': [],
            'other': []
        }
        
        # Define category patterns
        tech_patterns = [
            r'\b(python|java|javascript|react|angular|vue|node|django|flask|spring|docker|kubernetes|aws|azure|gcp|git|sql|nosql|mongodb|postgresql|mysql|redis)\b',
            r'\b(machine learning|deep learning|ai|artificial intelligence|data science|analytics|statistics)\b',
            r'\b(html|css|php|ruby|go|rust|swift|kotlin|scala|r|matlab|sas|spss)\b'
        ]
        
        soft_skill_patterns = [
            r'\b(leadership|communication|teamwork|problem solving|critical thinking|creativity|adaptability|time management|organization|collaboration)\b'
        ]
        
        tool_patterns = [
            r'\b(jira|confluence|slack|teams|zoom|figma|sketch|photoshop|illustrator|excel|powerpoint|word|outlook)\b'
        ]
        
        # Categorize keywords
        for keyword in keywords:
            text = keyword['text'].lower()
            categorized = False
            
            # Check technical skills
            for pattern in tech_patterns:
                if re.search(pattern, text):
                    categories['technical_skills'].append(keyword['text'])
                    categorized = True
                    break
            
            # Check soft skills
            if not categorized:
                for pattern in soft_skill_patterns:
                    if re.search(pattern, text):
                        categories['soft_skills'].append(keyword['text'])
                        categorized = True
                        break
            
            # Check tools
            if not categorized:
                for pattern in tool_patterns:
                    if re.search(pattern, text):
                        categories['tools'].append(keyword['text'])
                        categorized = True
                        break
            
            # Default to other
            if not categorized:
                categories['other'].append(keyword['text'])
        
        return categories
    
    def _identify_requirements(self, job_text: str, keywords: List[Dict[str, any]]) -> Dict[str, List[str]]:
        """
        Identify required vs preferred skills from job description.
        
        Args:
            job_text (str): Job description text
            keywords (List[Dict[str, any]]): Extracted keywords
            
        Returns:
            Dict[str, List[str]]: Required and preferred skills
        """
        required = []
        preferred = []
        
        # Look for requirement indicators
        requirement_indicators = [
            r'required', r'requirement', r'must have', r'essential',
            r'minimum', r'at least', r'necessary', r'mandatory'
        ]
        
        preferred_indicators = [
            r'preferred', r'nice to have', r'bonus', r'plus',
            r'would be great', r'ideal', r'optional'
        ]
        
        # Analyze context around keywords
        for keyword in keywords:
            text = keyword['text']
            context = self._get_keyword_context(job_text, text)
            
            # Check for requirement indicators
            is_required = any(re.search(indicator, context, re.IGNORECASE) 
                            for indicator in requirement_indicators)
            is_preferred = any(re.search(indicator, context, re.IGNORECASE) 
                             for indicator in preferred_indicators)
            
            if is_required:
                required.append(text)
            elif is_preferred:
                preferred.append(text)
            else:
                # Default to required for important keywords
                if keyword.get('importance', 0) > 0.7:
                    required.append(text)
                else:
                    preferred.append(text)
        
        return {
            'required': list(set(required)),
            'preferred': list(set(preferred))
        }
    
    def _get_keyword_context(self, text: str, keyword: str, context_size: int = 100) -> str:
        """
        Get context around a keyword in the text.
        
        Args:
            text (str): Full text
            keyword (str): Keyword to find context for
            context_size (int): Number of characters around keyword
            
        Returns:
            str: Context around keyword
        """
        try:
            index = text.lower().find(keyword.lower())
            if index == -1:
                return ""
            
            start = max(0, index - context_size)
            end = min(len(text), index + len(keyword) + context_size)
            
            return text[start:end]
        except Exception:
            return ""
    
    def get_industry_keywords(self, industry: str) -> List[str]:
        """
        Get predefined keywords for a specific industry.
        
        Args:
            industry (str): Industry name
            
        Returns:
            List[str]: Industry-specific keywords
        """
        return self.industry_keywords.get(industry.lower(), [])
    
    def add_custom_keywords(self, industry: str, keywords: List[str]):
        """
        Add custom keywords for an industry.
        
        Args:
            industry (str): Industry name
            keywords (List[str]): Keywords to add
        """
        industry_lower = industry.lower()
        if industry_lower not in self.industry_keywords:
            self.industry_keywords[industry_lower] = []
        
        self.industry_keywords[industry_lower].extend(keywords)
        self.logger.info(f"Added {len(keywords)} custom keywords for industry: {industry}") 