"""
Complete Due-Date Suggestion System

Combines:
- Priority prediction
- Due date calculation
- Shift awareness
- Human-readable output
"""

import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import joblib
from datetime import datetime
from ml.priority_feature_extractor import PriorityFeatureExtractor
from ml.shift_aware_due_date_calculator import ShiftAwareDueDateCalculator

print("=" * 70)
print("⏰ COMPLETE DUE-DATE SUGGESTION SYSTEM")
print("=" * 70)

# Load models
print("\n📂 Loading models...")
priority_model = joblib.load('models/priority_model.pkl')
categorization_model = joblib.load('models/categorization_model.pkl')
categorization_vectorizer = joblib.load('models/categorization_vectorizer.pkl')
print("   ✅ All models loaded")

# Initialize calculators
feature_extractor = PriorityFeatureExtractor()
due_date_calculator = ShiftAwareDueDateCalculator()

def suggest_task_deadline(task_description):
    """
    Complete workflow:
    1. Categorize task
    2. Predict priority
    3. Calculate due date
    4. Return formatted suggestion
    """
    
    # Step 1: Categorize
    task_vec = categorization_vectorizer.transform([task_description])
    category = categorization_model.predict(task_vec)[0]
    
    # Step 2: Predict priority
    features = feature_extractor.extract_features(task_description, category)
    feature_order = [
        'category_weight', 'high_priority_keywords', 'low_priority_keywords',
        'safety_keywords', 'task_length', 'has_urgent_words',
        'equipment_count', 'cleaning_count'
    ]
    X = [[features[f] for f in feature_order]]
    priority = priority_model.predict(X)[0]
    
    # Step 3: Calculate due date
    due_info = due_date_calculator.calculate_due_date_shift_aware(
        priority, category
    )
    
    return {
        'task_description': task_description,
        'category': category,
        'priority': priority,
        'due_datetime': due_info['due_datetime'],
        'hours_available': due_info['hours_available'],
        'shift': due_info['shift']
    }

# Test with real tasks
print("\n" + "=" * 70)
print("TESTING COMPLETE WORKFLOW:")
print("=" * 70)

test_tasks = [
    "Clean contaminated milk storage tank immediately",
    "Label boxes for shipment",
    "Check temperature on fermentation batch",
    "Replace broken conveyor motor",
    "Organize packaging materials"
]

for i, task in enumerate(test_tasks, 1):
    result = suggest_task_deadline(task)
    
    priority_colors = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
    color = priority_colors.get(result['priority'], '⚪')
    
    print(f"\n{i}. TASK: {task}")
    print(f"   📂 Category: {result['category']}")
    print(f"   {color} Priority: {result['priority']}")
    print(f"   📅 Due: {result['due_datetime'].strftime('%Y-%m-%d %H:%M')}")
    print(f"   ⏱️  Hours Available: {result['hours_available']}h")
    print(f"   🕐 Current Shift: {result['shift']}")

print("\n" + "=" * 70)
print("✅ WORKFLOW COMPLETE!")
print("=" * 70)
