"""
Unit Tests for Priority Prediction

Tests the ML priority prediction model
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.priority_feature_extractor import PriorityFeatureExtractor

class TestPriorityFeatureExtractor(unittest.TestCase):
    """Test priority feature extraction"""
    
    def setUp(self):
        """Initialize extractor for each test"""
        self.extractor = PriorityFeatureExtractor()
    
    def test_extract_features_basic(self):
        """Test basic feature extraction"""
        task = "Clean tank"
        category = "Hygiene & Safety"
        
        features = self.extractor.extract_features(task, category)
        
        # Check features exist
        self.assertIn('category_weight', features)
        self.assertIn('high_priority_keywords', features)
        self.assertIn('safety_keywords', features)
    
    def test_category_weight_safety(self):
        """Test that safety category has high weight"""
        task = "Do something"
        category = "Hygiene & Safety"
        
        features = self.extractor.extract_features(task, category)
        
        # Safety category should have weight = 3
        self.assertEqual(features['category_weight'], 3)
    
    def test_category_weight_packaging(self):
        """Test that packaging category has low weight"""
        task = "Do something"
        category = "Packaging"
        
        features = self.extractor.extract_features(task, category)
        
        # Packaging should have weight = 0
        self.assertEqual(features['category_weight'], 0)
    
    def test_high_priority_keywords_detected(self):
        """Test detection of high priority keywords"""
        task = "Emergency shutdown immediately"
        category = "Production"
        
        features = self.extractor.extract_features(task, category)
        
        # Should detect 'emergency' and 'immediately'
        self.assertGreater(features['high_priority_keywords'], 0)
    
    def test_safety_keywords_detected(self):
        """Test detection of safety keywords"""
        task = "Clean contaminated tank"
        category = "Hygiene & Safety"
        
        features = self.extractor.extract_features(task, category)
        
        # Should detect 'clean', 'contaminated'
        self.assertGreater(features['safety_keywords'], 0)
    
    def test_task_length_calculation(self):
        """Test task length feature"""
        task = "Do work"
        category = "Production"
        
        features = self.extractor.extract_features(task, category)
        
        # 2 words
        self.assertEqual(features['task_length'], 2)
    
    def test_priority_score_calculation(self):
        """Test priority score calculation"""
        task = "Clean contaminated tank immediately"
        category = "Hygiene & Safety"
        
        score, features = self.extractor.calculate_priority_score(task, category)
        
        # Score should be between 0-10
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 10)
        
        # High priority task should have high score
        self.assertGreater(score, 5)

if __name__ == "__main__":
    unittest.main()
