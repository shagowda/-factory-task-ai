"""
Feature Extraction for Priority Prediction
"""

import re
from config.priority_keywords import (
    SAFETY_KEYWORDS,
    CATEGORY_PRIORITY_WEIGHTS,
    HIGH_PRIORITY_KEYWORDS,
    LOW_PRIORITY_KEYWORDS
)

class PriorityFeatureExtractor:
    """Extract features from task description for priority prediction"""
    
    def __init__(self):
        self.high_priority_keywords = set(HIGH_PRIORITY_KEYWORDS)
        self.low_priority_keywords = set(LOW_PRIORITY_KEYWORDS)
        self.safety_keywords = set(SAFETY_KEYWORDS)
    
    def extract_features(self, task_description, category):
        """Extract features from task description and category"""
        text = task_description.lower()
        words = text.split()
        
        features = {}
        
        features['category_weight'] = CATEGORY_PRIORITY_WEIGHTS.get(category, 0)
        
        high_priority_count = sum(1 for word in words if word in self.high_priority_keywords)
        features['high_priority_keywords'] = high_priority_count
        
        low_priority_count = sum(1 for word in words if word in self.low_priority_keywords)
        features['low_priority_keywords'] = low_priority_count
        
        safety_count = sum(1 for word in words if word in self.safety_keywords)
        features['safety_keywords'] = safety_count
        
        features['task_length'] = len(words)
        
        urgent_words = ['immediately', 'asap', 'urgent', 'critical', 'emergency']
        features['has_urgent_words'] = 1 if any(word in words for word in urgent_words) else 0
        
        equipment_words = ['tank', 'conveyor', 'mixer', 'machine', 'line', 'motor', 'pump', 'valve']
        features['equipment_count'] = sum(1 for word in words if word in equipment_words)
        
        cleaning_words = ['clean', 'sanitize', 'disinfect', 'wash', 'scrub']
        features['cleaning_count'] = sum(1 for word in words if word in cleaning_words)
        
        return features
    
    def calculate_priority_score(self, task_description, category):
        """Calculate a priority score (0-10)"""
        features = self.extract_features(task_description, category)
        
        score = 0
        score += features['category_weight'] * 1.5
        score += features['high_priority_keywords'] * 2
        score -= features['low_priority_keywords'] * 1.5
        score += features['safety_keywords'] * 1.5
        score += features['has_urgent_words'] * 2
        score += features['equipment_count'] * 0.5
        score += features['cleaning_count'] * 1
        
        score = max(0, min(10, score))
        
        return score, features
