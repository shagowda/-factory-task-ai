"""
Safety Rules Engine

Applies safety overrides and maintains audit logs
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.safety_rules_config import (
    CRITICAL_SAFETY_KEYWORDS,
    WARNING_KEYWORDS,
    ALWAYS_SAFETY_CRITICAL_CATEGORIES,
    SAFETY_RULES,
    MINIMUM_PRIORITY_BY_CATEGORY,
    AUDIT_LEVELS
)

class SafetyRulesEngine:
    """Apply safety rules and generate audit logs"""
    
    def __init__(self):
        self.critical_keywords = CRITICAL_SAFETY_KEYWORDS
        self.warning_keywords = WARNING_KEYWORDS
        self.safety_rules = SAFETY_RULES
        self.min_priority = MINIMUM_PRIORITY_BY_CATEGORY
        self.always_critical = ALWAYS_SAFETY_CRITICAL_CATEGORIES
        self.audit_log = []
    
    def check_safety_keywords(self, task_description):
        """
        Check if task contains safety keywords
        Returns: (has_critical, critical_keywords, warning_count)
        """
        text = task_description.lower()
        words = text.split()
        
        critical_found = []
        warning_found = []
        
        for word in words:
            if word in self.critical_keywords:
                critical_found.append(word)
            elif word in self.warning_keywords:
                warning_found.append(word)
        
        return bool(critical_found), critical_found, len(warning_found)
    
    def apply_safety_rules(self, task_description, category, ai_priority):
        """
        Apply safety rules and potentially override AI priority
        
        Returns:
            {
                'final_priority': str,
                'ai_priority': str,
                'was_overridden': bool,
                'override_reason': str,
                'audit_level': str,
                'critical_keywords': list,
                'warning_count': int
            }
        """
        
        has_critical, critical_keywords, warning_count = self.check_safety_keywords(task_description)
        
        result = {
            'final_priority': ai_priority,
            'ai_priority': ai_priority,
            'was_overridden': False,
            'override_reason': None,
            'audit_level': 'INFO',
            'critical_keywords': critical_keywords,
            'warning_count': warning_count
        }
        
        # Rule 1: Category-based minimum priority
        min_priority = self.min_priority.get(category, 'Low')
        priority_order = {'Low': 0, 'Medium': 1, 'High': 2}
        
        if priority_order.get(ai_priority, 0) < priority_order.get(min_priority, 0):
            result['final_priority'] = min_priority
            result['was_overridden'] = True
            result['override_reason'] = f"Category '{category}' minimum is {min_priority}"
            result['audit_level'] = 'WARNING'
        
        # Rule 2: Critical safety keywords always = HIGH
        if has_critical and result['final_priority'] != 'High':
            result['final_priority'] = 'High'
            result['was_overridden'] = True
            result['override_reason'] = f"Critical keywords detected: {', '.join(critical_keywords)}"
            result['audit_level'] = 'CRITICAL'
        
        # Rule 3: Hygiene & Safety category always at least HIGH
        if category in self.always_critical and result['final_priority'] != 'High':
            result['final_priority'] = 'High'
            result['was_overridden'] = True
            result['override_reason'] = f"Category '{category}' is safety-critical"
            result['audit_level'] = 'WARNING'
        
        return result
    
    def log_audit(self, task_id, task_description, category, ai_priority, safety_result):
        """
        Create audit log entry (for compliance and debugging)
        """
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'task_description': task_description,
            'category': category,
            'ai_priority': ai_priority,
            'final_priority': safety_result['final_priority'],
            'was_overridden': safety_result['was_overridden'],
            'override_reason': safety_result['override_reason'],
            'audit_level': safety_result['audit_level'],
            'critical_keywords': safety_result['critical_keywords'],
            'warning_count': safety_result['warning_count']
        }
        
        self.audit_log.append(audit_entry)
        return audit_entry
    
    def get_audit_log(self):
        """Return all audit logs"""
        return self.audit_log
    
    def save_audit_log(self, filepath='logs/safety_audit.json'):
        """Save audit log to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
        print(f"✅ Audit log saved: {filepath}")
    
    def print_audit_summary(self):
        """Print summary of all overrides"""
        overrides = [log for log in self.audit_log if log['was_overridden']]
        
        print("\n" + "=" * 70)
        print("SAFETY AUDIT SUMMARY")
        print("=" * 70)
        print(f"Total tasks logged: {len(self.audit_log)}")
        print(f"Safety overrides: {len(overrides)}")
        
        if overrides:
            print("\nOVERRIDES APPLIED:")
            for override in overrides:
                print(f"\n  📋 Task: {override['task_description']}")
                print(f"     AI said: {override['ai_priority']} → Final: {override['final_priority']}")
                print(f"     Reason: {override['override_reason']}")
                print(f"     Level: {override['audit_level']}")

# Example usage
if __name__ == "__main__":
    engine = SafetyRulesEngine()
    
    print("=" * 70)
    print("🛡️ SAFETY RULES ENGINE TESTING")
    print("=" * 70)
    
    # Test cases: (task_description, category, ai_priority)
    test_cases = [
        ("Clean contaminated storage tank", "Hygiene & Safety", "Low"),
        ("Label boxes for shipping", "Packaging", "Low"),
        ("Mold found in fermentation vessel", "Quality Control", "Medium"),
        ("Organize warehouse shelves", "Production", "Low"),
        ("Temperature sensor not working", "Maintenance", "Medium"),
        ("Allergen contamination risk detected", "Quality Control", "Low"),
        ("Check packaging weight", "Quality Control", "Low"),
        ("Emergency - refrigerator broken", "Maintenance", "High"),
    ]
    
    for task, category, ai_priority in test_cases:
        safety_result = engine.apply_safety_rules(task, category, ai_priority)
        audit = engine.log_audit(len(engine.audit_log) + 1, task, category, ai_priority, safety_result)
        
        override_emoji = "⚠️ " if safety_result['was_overridden'] else "✅"
        print(f"\n{override_emoji} Task: {task}")
        print(f"   Category: {category}")
        print(f"   AI Priority: {ai_priority} → Final: {safety_result['final_priority']}")
        if safety_result['was_overridden']:
            print(f"   🔒 Override: {safety_result['override_reason']}")
            print(f"   📊 Level: {safety_result['audit_level']}")
        if safety_result['critical_keywords']:
            print(f"   ⚠️  Keywords: {', '.join(safety_result['critical_keywords'])}")
    
    # Print summary
    engine.print_audit_summary()
    
    # Save logs
    engine.save_audit_log()
