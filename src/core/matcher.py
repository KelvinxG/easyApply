"""
Keyword Matching Module

Handles keyword matching between resume and job description using various
matching algorithms including exact, fuzzy, and partial matching.
"""

import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import re

try:
    from fuzzywuzzy import fuzz, process
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    logging.warning("fuzzywuzzy not available, using basic string matching")

from src.utils.constants import (
    MIN_FUZZY_MATCH_RATIO, EXACT_MATCH_WEIGHT, FUZZY_MATCH_WEIGHT,
    PARTIAL_MATCH_WEIGHT, MATCH_COLORS
)
from src.utils.logger import get_logger


class KeywordMatcher:
    """
    Keyword matching class for comparing resume keywords against job description keywords.
    
    Supports multiple matching strategies including exact, fuzzy, and partial matching
    with configurable thresholds and scoring.
    """
    
    def __init__(self, fuzzy_threshold: int = MIN_FUZZY_MATCH_RATIO):
        """
        Initialize the keyword matcher.
        
        Args:
            fuzzy_threshold (int): Minimum fuzzy match ratio (0-100)
        """
        self.logger = get_logger(__name__)
        self.fuzzy_threshold = fuzzy_threshold
        
        if not FUZZYWUZZY_AVAILABLE:
            self.logger.warning("fuzzywuzzy not available, fuzzy matching disabled")
    
    def match_keywords(self, resume_keywords: List[Dict[str, any]], 
                      job_keywords: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Match resume keywords against job description keywords.
        
        Args:
            resume_keywords (List[Dict[str, any]]): Keywords extracted from resume
            job_keywords (List[Dict[str, any]]): Keywords extracted from job description
            
        Returns:
            Dict[str, any]: Matching results with detailed analysis
        """
        self.logger.info(f"Matching {len(resume_keywords)} resume keywords against {len(job_keywords)} job keywords")
        
        # Normalize keyword lists
        resume_normalized = self._normalize_keywords(resume_keywords)
        job_normalized = self._normalize_keywords(job_keywords)
        
        # Perform matching
        exact_matches = self._find_exact_matches(resume_normalized, job_normalized)
        fuzzy_matches = self._find_fuzzy_matches(resume_normalized, job_normalized)
        partial_matches = self._find_partial_matches(resume_normalized, job_normalized)
        
        # Identify missing keywords
        missing_keywords = self._find_missing_keywords(resume_normalized, job_normalized, 
                                                     exact_matches, fuzzy_matches, partial_matches)
        
        # Calculate scores
        scores = self._calculate_scores(exact_matches, fuzzy_matches, partial_matches, 
                                      len(resume_normalized), len(job_normalized))
        
        # Compile results
        results = {
            'exact_matches': exact_matches,
            'fuzzy_matches': fuzzy_matches,
            'partial_matches': partial_matches,
            'missing_keywords': missing_keywords,
            'scores': scores,
            'summary': self._generate_summary(exact_matches, fuzzy_matches, partial_matches, 
                                            missing_keywords, scores),
            'total_resume_keywords': len(resume_normalized),
            'total_job_keywords': len(job_normalized),
            'match_percentage': scores['overall_score']
        }
        
        self.logger.info(f"Match analysis complete. Overall score: {scores['overall_score']:.1f}%")
        return results
    
    def _normalize_keywords(self, keywords: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Normalize keywords for consistent matching.
        
        Args:
            keywords (List[Dict[str, any]]): Raw keywords
            
        Returns:
            List[Dict[str, any]]: Normalized keywords
        """
        normalized = []
        
        for keyword in keywords:
            text = keyword.get('text', '')
            if not text:
                continue
            
            # Create normalized version
            normalized_keyword = {
                'original': text,
                'normalized': text.lower().strip(),
                'cleaned': self._clean_keyword(text),
                'importance': keyword.get('importance', 0.5),
                'type': keyword.get('type', 'unknown'),
                'frequency': keyword.get('frequency', 1),
                'metadata': keyword
            }
            
            normalized.append(normalized_keyword)
        
        return normalized
    
    def _clean_keyword(self, keyword: str) -> str:
        """
        Clean keyword for better matching.
        
        Args:
            keyword (str): Raw keyword
            
        Returns:
            str: Cleaned keyword
        """
        # Remove special characters and extra spaces
        cleaned = re.sub(r'[^\w\s]', ' ', keyword)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned.lower()
    
    def _find_exact_matches(self, resume_keywords: List[Dict[str, any]], 
                           job_keywords: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Find exact matches between resume and job keywords.
        
        Args:
            resume_keywords (List[Dict[str, any]]): Normalized resume keywords
            job_keywords (List[Dict[str, any]]): Normalized job keywords
            
        Returns:
            List[Dict[str, any]]: Exact matches with details
        """
        exact_matches = []
        resume_set = {kw['normalized'] for kw in resume_keywords}
        job_set = {kw['normalized'] for kw in job_keywords}
        
        # Find intersection
        common_keywords = resume_set.intersection(job_set)
        
        for keyword in common_keywords:
            resume_kw = next(kw for kw in resume_keywords if kw['normalized'] == keyword)
            job_kw = next(kw for kw in job_keywords if kw['normalized'] == keyword)
            
            match = {
                'resume_keyword': resume_kw['original'],
                'job_keyword': job_kw['original'],
                'normalized': keyword,
                'match_type': 'exact',
                'confidence': 1.0,
                'weight': EXACT_MATCH_WEIGHT,
                'resume_importance': resume_kw['importance'],
                'job_importance': job_kw['importance'],
                'color': MATCH_COLORS['exact']
            }
            
            exact_matches.append(match)
        
        self.logger.info(f"Found {len(exact_matches)} exact matches")
        return exact_matches
    
    def _find_fuzzy_matches(self, resume_keywords: List[Dict[str, any]], 
                           job_keywords: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Find fuzzy matches between resume and job keywords.
        
        Args:
            resume_keywords (List[Dict[str, any]]): Normalized resume keywords
            job_keywords (List[Dict[str, any]]): Normalized job keywords
            
        Returns:
            List[Dict[str, any]]: Fuzzy matches with details
        """
        if not FUZZYWUZZY_AVAILABLE:
            return []
        
        fuzzy_matches = []
        processed_resume = set()
        processed_job = set()
        
        # Get exact matches to exclude from fuzzy matching
        exact_normalized = {kw['normalized'] for kw in self._find_exact_matches(resume_keywords, job_keywords)}
        
        # Filter out exact matches
        resume_for_fuzzy = [kw for kw in resume_keywords if kw['normalized'] not in exact_normalized]
        job_for_fuzzy = [kw for kw in job_keywords if kw['normalized'] not in exact_normalized]
        
        for resume_kw in resume_for_fuzzy:
            if resume_kw['normalized'] in processed_resume:
                continue
            
            # Find best fuzzy match
            best_match = None
            best_ratio = 0
            
            for job_kw in job_for_fuzzy:
                if job_kw['normalized'] in processed_job:
                    continue
                
                # Calculate fuzzy ratio
                ratio = fuzz.ratio(resume_kw['normalized'], job_kw['normalized'])
                
                if ratio > best_ratio and ratio >= self.fuzzy_threshold:
                    best_ratio = ratio
                    best_match = job_kw
            
            if best_match:
                match = {
                    'resume_keyword': resume_kw['original'],
                    'job_keyword': best_match['original'],
                    'normalized_resume': resume_kw['normalized'],
                    'normalized_job': best_match['normalized'],
                    'match_type': 'fuzzy',
                    'confidence': best_ratio / 100.0,
                    'ratio': best_ratio,
                    'weight': FUZZY_MATCH_WEIGHT,
                    'resume_importance': resume_kw['importance'],
                    'job_importance': best_match['importance'],
                    'color': MATCH_COLORS['fuzzy']
                }
                
                fuzzy_matches.append(match)
                processed_resume.add(resume_kw['normalized'])
                processed_job.add(best_match['normalized'])
        
        self.logger.info(f"Found {len(fuzzy_matches)} fuzzy matches")
        return fuzzy_matches
    
    def _find_partial_matches(self, resume_keywords: List[Dict[str, any]], 
                             job_keywords: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Find partial matches (substring matches) between resume and job keywords.
        
        Args:
            resume_keywords (List[Dict[str, any]]): Normalized resume keywords
            job_keywords (List[Dict[str, any]]): Normalized job keywords
            
        Returns:
            List[Dict[str, any]]: Partial matches with details
        """
        partial_matches = []
        processed_resume = set()
        processed_job = set()
        
        # Get already matched keywords
        exact_normalized = {kw['normalized'] for kw in self._find_exact_matches(resume_keywords, job_keywords)}
        fuzzy_normalized = {kw['normalized_resume'] for kw in self._find_fuzzy_matches(resume_keywords, job_keywords)}
        all_matched_resume = exact_normalized.union(fuzzy_normalized)
        
        # Filter out already matched keywords
        resume_for_partial = [kw for kw in resume_keywords if kw['normalized'] not in all_matched_resume]
        job_for_partial = [kw for kw in job_keywords if kw['normalized'] not in exact_normalized]
        
        for resume_kw in resume_for_partial:
            if resume_kw['normalized'] in processed_resume:
                continue
            
            for job_kw in job_for_partial:
                if job_kw['normalized'] in processed_job:
                    continue
                
                # Check for partial matches
                if self._is_partial_match(resume_kw['normalized'], job_kw['normalized']):
                    match = {
                        'resume_keyword': resume_kw['original'],
                        'job_keyword': job_kw['original'],
                        'normalized_resume': resume_kw['normalized'],
                        'normalized_job': job_kw['normalized'],
                        'match_type': 'partial',
                        'confidence': 0.6,  # Lower confidence for partial matches
                        'weight': PARTIAL_MATCH_WEIGHT,
                        'resume_importance': resume_kw['importance'],
                        'job_importance': job_kw['importance'],
                        'color': MATCH_COLORS['partial']
                    }
                    
                    partial_matches.append(match)
                    processed_resume.add(resume_kw['normalized'])
                    processed_job.add(job_kw['normalized'])
                    break
        
        self.logger.info(f"Found {len(partial_matches)} partial matches")
        return partial_matches
    
    def _is_partial_match(self, keyword1: str, keyword2: str) -> bool:
        """
        Check if two keywords have a partial match relationship.
        
        Args:
            keyword1 (str): First keyword
            keyword2 (str): Second keyword
            
        Returns:
            bool: True if keywords partially match
        """
        # Check if one is a substring of the other
        if keyword1 in keyword2 or keyword2 in keyword1:
            return True
        
        # Check for word-level partial matches
        words1 = set(keyword1.split())
        words2 = set(keyword2.split())
        
        # If there's significant word overlap
        if len(words1.intersection(words2)) >= min(len(words1), len(words2)) * 0.5:
            return True
        
        return False
    
    def _find_missing_keywords(self, resume_keywords: List[Dict[str, any]], 
                              job_keywords: List[Dict[str, any]],
                              exact_matches: List[Dict[str, any]],
                              fuzzy_matches: List[Dict[str, any]],
                              partial_matches: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Find keywords in job description that are missing from resume.
        
        Args:
            resume_keywords (List[Dict[str, any]]): Resume keywords
            job_keywords (List[Dict[str, any]]): Job keywords
            exact_matches (List[Dict[str, any]]): Exact matches
            fuzzy_matches (List[Dict[str, any]]): Fuzzy matches
            partial_matches (List[Dict[str, any]]): Partial matches
            
        Returns:
            List[Dict[str, any]]: Missing keywords with details
        """
        # Get all matched job keywords
        matched_job_keywords = set()
        
        for match in exact_matches:
            matched_job_keywords.add(match['normalized'])
        
        for match in fuzzy_matches:
            matched_job_keywords.add(match['normalized_job'])
        
        for match in partial_matches:
            matched_job_keywords.add(match['normalized_job'])
        
        # Find missing keywords
        missing_keywords = []
        for job_kw in job_keywords:
            if job_kw['normalized'] not in matched_job_keywords:
                missing = {
                    'keyword': job_kw['original'],
                    'normalized': job_kw['normalized'],
                    'importance': job_kw['importance'],
                    'type': job_kw['type'],
                    'color': MATCH_COLORS['missing']
                }
                missing_keywords.append(missing)
        
        self.logger.info(f"Found {len(missing_keywords)} missing keywords")
        return missing_keywords
    
    def _calculate_scores(self, exact_matches: List[Dict[str, any]],
                         fuzzy_matches: List[Dict[str, any]],
                         partial_matches: List[Dict[str, any]],
                         total_resume_keywords: int,
                         total_job_keywords: int) -> Dict[str, float]:
        """
        Calculate various matching scores.
        
        Args:
            exact_matches (List[Dict[str, any]]): Exact matches
            fuzzy_matches (List[Dict[str, any]]): Fuzzy matches
            partial_matches (List[Dict[str, any]]): Partial matches
            total_resume_keywords (int): Total resume keywords
            total_job_keywords (int): Total job keywords
            
        Returns:
            Dict[str, float]: Various scoring metrics
        """
        # Calculate weighted scores
        exact_score = sum(match['weight'] * match['confidence'] for match in exact_matches)
        fuzzy_score = sum(match['weight'] * match['confidence'] for match in fuzzy_matches)
        partial_score = sum(match['weight'] * match['confidence'] for match in partial_matches)
        
        total_weighted_score = exact_score + fuzzy_score + partial_score
        
        # Calculate percentages
        total_matches = len(exact_matches) + len(fuzzy_matches) + len(partial_matches)
        
        if total_job_keywords > 0:
            match_percentage = (total_matches / total_job_keywords) * 100
            coverage_percentage = (total_matches / total_job_keywords) * 100
        else:
            match_percentage = 0.0
            coverage_percentage = 0.0
        
        if total_resume_keywords > 0:
            resume_utilization = (total_matches / total_resume_keywords) * 100
        else:
            resume_utilization = 0.0
        
        # Calculate overall score (weighted average)
        max_possible_score = total_job_keywords * EXACT_MATCH_WEIGHT
        if max_possible_score > 0:
            overall_score = (total_weighted_score / max_possible_score) * 100
        else:
            overall_score = 0.0
        
        return {
            'exact_score': exact_score,
            'fuzzy_score': fuzzy_score,
            'partial_score': partial_score,
            'total_weighted_score': total_weighted_score,
            'match_percentage': match_percentage,
            'coverage_percentage': coverage_percentage,
            'resume_utilization': resume_utilization,
            'overall_score': overall_score,
            'total_matches': total_matches,
            'exact_matches_count': len(exact_matches),
            'fuzzy_matches_count': len(fuzzy_matches),
            'partial_matches_count': len(partial_matches)
        }
    
    def _generate_summary(self, exact_matches: List[Dict[str, any]],
                         fuzzy_matches: List[Dict[str, any]],
                         partial_matches: List[Dict[str, any]],
                         missing_keywords: List[Dict[str, any]],
                         scores: Dict[str, float]) -> Dict[str, any]:
        """
        Generate a summary of the matching results.
        
        Args:
            exact_matches (List[Dict[str, any]]): Exact matches
            fuzzy_matches (List[Dict[str, any]]): Fuzzy matches
            partial_matches (List[Dict[str, any]]): Partial matches
            missing_keywords (List[Dict[str, any]]): Missing keywords
            scores (Dict[str, float]): Calculated scores
            
        Returns:
            Dict[str, any]: Summary of results
        """
        # Categorize matches by importance
        high_importance_matches = []
        medium_importance_matches = []
        low_importance_matches = []
        
        for match in exact_matches + fuzzy_matches + partial_matches:
            importance = max(match.get('resume_importance', 0), match.get('job_importance', 0))
            if importance >= 0.8:
                high_importance_matches.append(match)
            elif importance >= 0.5:
                medium_importance_matches.append(match)
            else:
                low_importance_matches.append(match)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(missing_keywords, scores)
        
        return {
            'high_importance_matches': len(high_importance_matches),
            'medium_importance_matches': len(medium_importance_matches),
            'low_importance_matches': len(low_importance_matches),
            'missing_keywords_count': len(missing_keywords),
            'recommendations': recommendations,
            'overall_assessment': self._assess_overall_match(scores['overall_score'])
        }
    
    def _generate_recommendations(self, missing_keywords: List[Dict[str, any]], 
                                 scores: Dict[str, float]) -> List[str]:
        """
        Generate recommendations based on missing keywords and scores.
        
        Args:
            missing_keywords (List[Dict[str, any]]): Missing keywords
            scores (Dict[str, float]): Calculated scores
            
        Returns:
            List[str]: List of recommendations
        """
        recommendations = []
        
        # Score-based recommendations
        if scores['overall_score'] < 50:
            recommendations.append("Overall match is low. Consider adding more relevant keywords to your resume.")
        elif scores['overall_score'] < 70:
            recommendations.append("Match is moderate. Focus on adding high-importance missing keywords.")
        else:
            recommendations.append("Good match! Your resume aligns well with the job requirements.")
        
        # Missing keywords recommendations
        if missing_keywords:
            high_importance_missing = [kw for kw in missing_keywords if kw['importance'] >= 0.8]
            if high_importance_missing:
                recommendations.append(f"Add {len(high_importance_missing)} high-importance keywords to improve your match.")
            
            if len(missing_keywords) > 10:
                recommendations.append("Consider adding more relevant skills and technologies to your resume.")
        
        return recommendations
    
    def _assess_overall_match(self, overall_score: float) -> str:
        """
        Assess the overall match quality.
        
        Args:
            overall_score (float): Overall matching score
            
        Returns:
            str: Assessment description
        """
        if overall_score >= 90:
            return "Excellent Match"
        elif overall_score >= 80:
            return "Very Good Match"
        elif overall_score >= 70:
            return "Good Match"
        elif overall_score >= 60:
            return "Fair Match"
        elif overall_score >= 50:
            return "Poor Match"
        else:
            return "Very Poor Match" 