"""
Priority Prediction - Real-time Inference
"""

import joblib
from ml.priority_feature_extractor import PriorityFeatureExtractor

print("=" * 70)
print("🚦 PRIORITY PREDICTION - INFERENCE")
print("=" * 70)

print("\n📂 Loading trained models...")
priority_model = joblib.load('models/priority_model.pkl')
extractor = PriorityFeatureExtractor()
print("   ✅ Priority model loaded")

def predict_priority(task_description, category):
    """Predict priority for a task"""
    
    features = extractor.extract_features(task_description, category)
    
    feature_order = [
        'category_weight', 'high_priority_keywords', 'low_priority_keywords',
        'safety_keywords', 'task_length', 'has_urgent_words',
        'equipment_count', 'cleaning_count'
    ]
    X = [[features[f] for f in feature_order]]
    
    priority = priority_model.predict(X)[0]
    priority_proba = priority_model.predict_proba(X)[0]
    
    confidence = max(priority_proba)
    
    color_map = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
    color = color_map.get(priority, '⚪')
    
    return priority, confidence, features

print("\n" + "=" * 70)
print("TESTING PRIORITY PREDICTIONS:")
print("=" * 70)

test_cases = [
    ("Clean contaminated storage tank immediately", "Hygiene & Safety"),
    ("Label boxes for shipping", "Packaging"),
    ("Test bacterial samples in lab", "Quality Control"),
    ("Replace broken motor on production line", "Maintenance"),
    ("Load ingredients into mixer", "Production"),
    ("Sanitize cutting surfaces immediately", "Hygiene & Safety"),
    ("Organize warehouse inventory", "Production"),
    ("Check pH level of fermentation batch", "Quality Control")
]

for i, (task, category) in enumerate(test_cases, 1):
    priority, confidence, features = predict_priority(task, category)
    
    color_map = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
    color = color_map.get(priority, '⚪')
    
    print(f"\n{i}. Task: '{task}'")
    print(f"   Category: {category}")
    print(f"   {color} Priority: {priority}")
    print(f"   ✅ Confidence: {confidence:.1%}")
    print(f"   📊 Keywords found: high={features['high_priority_keywords']}, safety={features['safety_keywords']}")

print("\n" + "=" * 70)
print("✅ PRIORITY PREDICTIONS COMPLETE!")
print("=" * 70)
