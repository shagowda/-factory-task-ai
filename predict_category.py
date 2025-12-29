"""
Task Categorization Prediction Script

This script loads the trained model and makes predictions
on new, unseen tasks.
"""

import joblib

print("=" * 70)
print("🔮 TASK CATEGORIZATION - PREDICTION")
print("=" * 70)

# Load the saved model and vectorizer
print("\n📂 Loading trained model...")
model = joblib.load('models/categorization_model.pkl')
vectorizer = joblib.load('models/categorization_vectorizer.pkl')
print("   ✅ Model loaded successfully")

# Function to predict category
def predict_category(task_description):
    """Predict category for a given task description"""
    # Vectorize the input
    task_vectorized = vectorizer.transform([task_description])
    
    # Predict category and confidence
    category = model.predict(task_vectorized)[0]
    confidence = model.predict_proba(task_vectorized)[0].max()
    
    return category, confidence

# Test with various tasks
print("\n" + "=" * 70)
print("TESTING PREDICTIONS ON NEW TASKS:")
print("=" * 70)

test_tasks = [
    "Sanitize cutting boards and utensils",
    "Run quality tests on batch samples",
    "Fix broken packaging machine",
    "Start fermentation process",
    "Organize warehouse shelves",
    "Check for mold in storage areas",
    "Replace conveyor belt bearings",
    "Seal boxes for shipping"
]

for i, task in enumerate(test_tasks, 1):
    category, confidence = predict_category(task)
    print(f"\n{i}. Task: '{task}'")
    print(f"   ✅ Category: {category}")
    print(f"   ✅ Confidence: {confidence:.1%}")

print("\n" + "=" * 70)
print("✅ PREDICTIONS COMPLETE!")
print("=" * 70)
