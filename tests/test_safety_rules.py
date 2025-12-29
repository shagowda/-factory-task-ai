"""
Unit Tests for Safety Rules Engine

Tests the safety override logic
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.safety_rules_engine import SafetyRulesEngine

class TestSafetyRulesEngine(unittest.TestCase):
    """Test safety rules engine"""
    
    def setUp(self):
        """Initialize engine for each test"""
        self.engine = SafetyRulesEngine()
    
    def test_critical_keyword_detection(self):
        """Test detection of critical safety keywords"""
        has_critical, keywords, warning_count = self.engine.check_safety_keywords(
            "Mold contamination detected"
        )
        
        # Should detect critical keywords
        self.assertTrue(has_critical)
        self.assertGreater(len(keywords), 0)
        self.assertIn('mold', keywords)
    
    def test_no_critical_keywords(self):
        """Test normal task without critical keywords"""
        has_critical, keywords, warning_count = self.engine.check_safety_keywords(
            "Label boxes for shipping"
        )
        
        # Should not detect critical keywords
        self.assertFalse(has_critical)
    
    def test_override_high_priority_if_contamination(self):
        """Test that contamination forces HIGH priority"""
        result = self.engine.apply_safety_rules(
            "Contaminated product found",
            "Quality Control",
            "Low"  # AI said LOW
        )
        
        # Should override to HIGH
        self.assertEqual(result['final_priority'], 'High')
        self.assertTrue(result['was_overridden'])
        self.assertIsNotNone(result['override_reason'])
    
    def test_hygiene_safety_minimum_high(self):
        """Test that Hygiene & Safety is minimum HIGH"""
        result = self.engine.apply_safety_rules(
            "Organize cleaning supplies",
            "Hygiene & Safety",
            "Low"  # AI said LOW
        )
        
        # Should override to HIGH (category minimum)
        self.assertEqual(result['final_priority'], 'High')
        self.assertTrue(result['was_overridden'])
    
    def test_no_override_if_high_already(self):
        """Test that HIGH priority doesn't get overridden"""
        result = self.engine.apply_safety_rules(
            "Clean tank",
            "Hygiene & Safety",
            "High"  # AI already said HIGH
        )
        
        # Should not override
        self.assertEqual(result['final_priority'], 'High')
        self.assertFalse(result['was_overridden'])
    
    def test_audit_logging(self):
        """Test audit log entry creation"""
        result = self.engine.apply_safety_rules(
            "Emergency shutdown",
            "Maintenance",
            "Low"
        )
        
        audit = self.engine.log_audit(1, "Emergency shutdown", "Maintenance", "Low", result)
        
        # Check audit entry
        self.assertEqual(audit['task_id'], 1)
        self.assertEqual(audit['ai_priority'], 'Low')
        self.assertEqual(audit['final_priority'], 'High')
        self.assertTrue(audit['was_overridden'])
    
    def test_audit_log_count(self):
        """Test that audit log stores multiple entries"""
        for i in range(3):
            result = self.engine.apply_safety_rules(
                f"Task {i}",
                "Hygiene & Safety",
                "Low"
            )
            self.engine.log_audit(i, f"Task {i}", "Hygiene & Safety", "Low", result)
        
        logs = self.engine.get_audit_log()
        self.assertEqual(len(logs), 3)

if __name__ == "__main__":
    unittest.main()
