"""
Performance Tests

Measure system performance and identify bottlenecks
"""

import sys
import os
import unittest
import time
import joblib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.priority_feature_extractor import PriorityFeatureExtractor
from database.db_manager import DatabaseManager

class TestPerformance(unittest.TestCase):
    """Test system performance"""
    
    def setUp(self):
        """Setup for performance tests"""
        self.extractor = PriorityFeatureExtractor()
        self.categorization_vectorizer = joblib.load('models/categorization_vectorizer.pkl')
        self.categorization_model = joblib.load('models/categorization_model.pkl')
        self.priority_model = joblib.load('models/priority_model.pkl')
    
    def test_categorization_speed(self):
        """Test categorization model speed"""
        task = "Clean contaminated milk tank"
        
        start = time.time()
        for _ in range(100):
            vec = self.categorization_vectorizer.transform([task])
            self.categorization_model.predict(vec)
        end = time.time()
        
        avg_time = (end - start) / 100 * 1000  # Convert to ms
        
        print(f"\n⚡ Categorization: {avg_time:.2f}ms per prediction")
        
        # Should be fast (< 50ms)
        self.assertLess(avg_time, 50)
    
    def test_priority_prediction_speed(self):
        """Test priority prediction speed"""
        task = "Clean contaminated milk tank"
        category = "Hygiene & Safety"
        
        start = time.time()
        for _ in range(100):
            features = self.extractor.extract_features(task, category)
            feature_order = [
                'category_weight', 'high_priority_keywords', 'low_priority_keywords',
                'safety_keywords', 'task_length', 'has_urgent_words',
                'equipment_count', 'cleaning_count'
            ]
            X = [[features[f] for f in feature_order]]
            self.priority_model.predict(X)
        end = time.time()
        
        avg_time = (end - start) / 100 * 1000
        
        print(f"⚡ Priority prediction: {avg_time:.2f}ms per prediction")
        
        # Should be fast (< 30ms)
        self.assertLess(avg_time, 30)
    
    def test_feature_extraction_speed(self):
        """Test feature extraction speed"""
        task = "Clean contaminated milk tank"
        category = "Hygiene & Safety"
        
        start = time.time()
        for _ in range(1000):
            self.extractor.extract_features(task, category)
        end = time.time()
        
        avg_time = (end - start) / 1000 * 1000  # Convert to ms
        
        print(f"⚡ Feature extraction: {avg_time:.3f}ms per extraction")
        
        # Should be very fast (< 5ms)
        self.assertLess(avg_time, 5)

if __name__ == "__main__":
    unittest.main()
