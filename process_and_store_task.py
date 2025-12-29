"""
Complete Task Processing with Database

Combines:
1. ML predictions
2. Safety rules
3. Database storage
4. Caching
5. Audit logging
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import joblib
from datetime import datetime
from ml.priority_feature_extractor import PriorityFeatureExtractor
from ml.shift_aware_due_date_calculator import ShiftAwareDueDateCalculator
from ml.safety_rules_engine import SafetyRulesEngine
from database.db_manager import DatabaseManager

print("=" * 70)
print("🏭 COMPLETE TASK PROCESSING WITH DATABASE")
print("=" * 70)

# Load models and initialize
print("\n📂 Initializing systems...")
categorization_model = joblib.load('models/categorization_model.pkl')
categorization_vectorizer = joblib.load('models/categorization_vectorizer.pkl')
priority_model = joblib.load('models/priority_model.pkl')
feature_extractor = PriorityFeatureExtractor()
due_date_calculator = ShiftAwareDueDateCalculator()
safety_engine = SafetyRulesEngine()
db = DatabaseManager()
db.initialize_database()
print("   ✅ All systems ready")

def submit_task(task_description, created_by="system"):
    """
    Complete task submission workflow:
    1. Check cache
    2. Predict category & priority
    3. Apply safety rules
    4. Calculate due date
    5. Store in database
    6. Log audit
    
    Returns: task_id
    """
    
    print(f"\n{'=' * 70}")
    print(f"📝 PROCESSING TASK: {task_description}")
    print(f"{'=' * 70}")
    
    # Step 1: Check cache
    print("\n1️⃣ Checking cache...")
    cache_hit, cached_category, cached_priority = db.check_cache(task_description)
    
    if cache_hit:
        print(f"   ✅ CACHE HIT! Category: {cached_category}, Priority: {cached_priority}")
        ai_category = cached_category
        ai_priority = cached_priority
    else:
        print(f"   Cache miss - predicting...")
        
        # Step 2: Categorize
        task_vec = categorization_vectorizer.transform([task_description])
        ai_category = categorization_model.predict(task_vec)[0]
        print(f"   ✅ Category: {ai_category}")
        
        # Step 3: Predict priority
        features = feature_extractor.extract_features(task_description, ai_category)
        feature_order = [
            'category_weight', 'high_priority_keywords', 'low_priority_keywords',
            'safety_keywords', 'task_length', 'has_urgent_words',
            'equipment_count', 'cleaning_count'
        ]
        X = [[features[f] for f in feature_order]]
        ai_priority = priority_model.predict(X)[0]
        print(f"   ✅ AI Priority: {ai_priority}")
        
        # Add to cache
        db.add_to_cache(task_description, ai_category, ai_priority)
        print(f"   ✅ Added to cache")
    
    # Step 4: Apply safety rules
    print("\n2️⃣ Applying safety rules...")
    safety_result = safety_engine.apply_safety_rules(
        task_description, ai_category, ai_priority
    )
    final_priority = safety_result['final_priority']
    
    if safety_result['was_overridden']:
        print(f"   ⚠️ OVERRIDE DETECTED!")
        print(f"   Reason: {safety_result['override_reason']}")
        print(f"   Level: {safety_result['audit_level']}")
    else:
        print(f"   ✅ No override needed")
    
    print(f"   ✅ Final Priority: {final_priority}")
    
    # Step 5: Calculate due date
    print("\n3️⃣ Calculating due date...")
    due_info = due_date_calculator.calculate_due_date_shift_aware(
        final_priority, ai_category
    )
    print(f"   ✅ Due: {due_info['due_datetime'].strftime('%Y-%m-%d %H:%M')}")
    print(f"   ✅ Hours available: {due_info['hours_available']}h")
    
    # Step 6: Store in database
    print("\n4️⃣ Storing in database...")
    task_id = db.add_task(
        task_description,
        ai_category,
        created_by,
        due_info['due_datetime']
    )
    print(f"   ✅ Task stored with ID: {task_id}")
    
    # Step 7: Store prediction
    db.add_prediction(
        task_id,
        ai_priority,
        ai_category,
        final_priority,
        ai_category,
        safety_result['was_overridden'],
        safety_result['override_reason']
    )
    print(f"   ✅ Prediction stored")
    
    # Step 8: Audit log
    db.add_audit_log(
        task_id,
        "task_created",
        f"Priority: {ai_priority} → {final_priority}",
        safety_result['critical_keywords'],
        safety_result['audit_level']
    )
    print(f"   ✅ Audit logged")
    
    print(f"\n✅ TASK #{task_id} FULLY PROCESSED AND STORED!")
    
    return task_id

# Test the system
print("\n" + "=" * 70)
print("SUBMITTING TASKS:")
print("=" * 70)

test_tasks = [
    "Clean contaminated milk storage tank immediately",
    "Label boxes for shipping",
    "Mold detected in fermentation tank",
    "Organize warehouse shelves",
    "Check temperature on production line",
    "Clean contaminated milk storage tank immediately",  # Same as first (cache test)
]

submitted_tasks = []
for task in test_tasks:
    task_id = submit_task(task, "worker1")
    submitted_tasks.append(task_id)

# Show pending tasks
print("\n" + "=" * 70)
print("PENDING TASKS IN DATABASE:")
print("=" * 70)
pending = db.get_pending_tasks()
for task in pending:
    priority_colors = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
    color = priority_colors.get(task.get('final_priority'), '⚪')
    print(f"\n{color} Task #{task['task_id']}: {task['task_description']}")
    print(f"   Due: {task['due_datetime']}")

# Show statistics
print("\n" + "=" * 70)
print("TODAY'S STATISTICS:")
print("=" * 70)
stats = db.get_task_statistics()
for key, value in stats.items():
    print(f"  {key}: {value}")

# Show cache stats
print("\n" + "=" * 70)
print("CACHE STATISTICS:")
print("=" * 70)
cache_stats = db.get_cache_stats()
print(f"  Total cached: {cache_stats.get('total_cached', 0)}")
print(f"  Total hits: {cache_stats.get('total_hits', 0)}")
print(f"  Avg hits per entry: {cache_stats.get('avg_hits', 0):.1f}")

# Complete a task
print(f"\n" + "=" * 70)
print(f"COMPLETING TASK #{submitted_tasks[0]}...")
print(f"=" * 70)
db.complete_task(submitted_tasks[0])

# Show updated stats
print("\nUPDATED STATISTICS:")
stats = db.get_task_statistics()
for key, value in stats.items():
    print(f"  {key}: {value}")

db.close()
print("\n✅ COMPLETE WORKFLOW TEST FINISHED!")
