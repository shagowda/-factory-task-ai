"""
Complete Task Processing Pipeline

Combines:
1. Categorization (ML)
2. Priority Prediction (ML)
3. Safety Rules (Rules Engine)
4. Due Date Calculation (Rules)
5. Audit Logging (Safety)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import joblib
from datetime import datetime
from ml.priority_feature_extractor import PriorityFeatureExtractor
from ml.shift_aware_due_date_calculator import ShiftAwareDueDateCalculator
from ml.safety_rules_engine import SafetyRulesEngine

print("=" * 70)
print("🏭 COMPLETE TASK PROCESSING PIPELINE")
print("=" * 70)

# Load models
print("\n📂 Loading models and engines...")
categorization_model = joblib.load('models/categorization_model.pkl')
categorization_vectorizer = joblib.load('models/categorization_vectorizer.pkl')
priority_model = joblib.load('models/priority_model.pkl')
print("   ✅ ML models loaded")

# Initialize engines
feature_extractor = PriorityFeatureExtractor()
due_date_calculator = ShiftAwareDueDateCalculator()
safety_engine = SafetyRulesEngine()
print("   ✅ Rules engines loaded")

def process_task(task_id, task_description):
    """
    Complete processing pipeline for a task
    
    Returns: Task suggestion with all AI + rules applied
    """
    
    # Step 1: Categorize
    task_vec = categorization_vectorizer.transform([task_description])
    ai_category = categorization_model.predict(task_vec)[0]
    
    # Step 2: Predict priority (AI)
    features = feature_extractor.extract_features(task_description, ai_category)
    feature_order = [
        'category_weight', 'high_priority_keywords', 'low_priority_keywords',
        'safety_keywords', 'task_length', 'has_urgent_words',
        'equipment_count', 'cleaning_count'
    ]
    X = [[features[f] for f in feature_order]]
    ai_priority = priority_model.predict(X)[0]
    
    # Step 3: Apply safety rules (override if needed)
    safety_result = safety_engine.apply_safety_rules(
        task_description, ai_category, ai_priority
    )
    final_priority = safety_result['final_priority']
    
    # Step 4: Calculate due date with final priority
    due_info = due_date_calculator.calculate_due_date_shift_aware(
        final_priority, ai_category
    )
    
    # Step 5: Log to audit trail
    audit = safety_engine.log_audit(
        task_id, task_description, ai_category, ai_priority, safety_result
    )
    
    return {
        'task_id': task_id,
        'task_description': task_description,
        'category': ai_category,
        'ai_priority': ai_priority,
        'final_priority': final_priority,
        'was_overridden': safety_result['was_overridden'],
        'override_reason': safety_result['override_reason'],
        'due_datetime': due_info['due_datetime'],
        'hours_available': due_info['hours_available'],
        'shift': due_info['shift'],
        'critical_keywords': safety_result['critical_keywords'],
        'audit_level': safety_result['audit_level']
    }

# Test pipeline
print("\n" + "=" * 70)
print("PROCESSING TASKS THROUGH COMPLETE PIPELINE:")
print("=" * 70)

test_tasks = [
    (1, "Clean contaminated milk storage tank immediately"),
    (2, "Label boxes for shipment"),
    (3, "Mold detected in fermentation tank"),
    (4, "Check temperature on production line"),
    (5, "Organize packaging materials"),
    (6, "Allergen cross-contamination risk found"),
    (7, "Replace worn conveyor belt"),
    (8, "Emergency - refrigerator shutdown"),
]

for task_id, task_desc in test_tasks:
    result = process_task(task_id, task_desc)
    
    priority_colors = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
    color = priority_colors.get(result['final_priority'], '⚪')
    override_emoji = "⚠️" if result['was_overridden'] else "✅"
    
    print(f"\n{override_emoji} Task #{result['task_id']}: {result['task_description']}")
    print(f"   📂 Category: {result['category']}")
    print(f"   {color} Priority: {result['ai_priority']} → {result['final_priority']}")
    
    if result['was_overridden']:
        print(f"   🔒 Safety Override: {result['override_reason']}")
    
    print(f"   📅 Due: {result['due_datetime'].strftime('%H:%M')} ({result['hours_available']}h)")
    
    if result['critical_keywords']:
        print(f"   ⚠️  Keywords: {', '.join(result['critical_keywords'])}")

# Print audit summary
safety_engine.print_audit_summary()

# Save audit log
safety_engine.save_audit_log()

print("\n" + "=" * 70)
print("✅ PIPELINE PROCESSING COMPLETE!")
print("=" * 70)
