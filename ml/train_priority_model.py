"""
Priority Prediction Model Training Script
"""

import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

print("=" * 70)
print("🚦 PRIORITY PREDICTION MODEL TRAINING")
print("=" * 70)

print("\n📂 Step 1: Loading enhanced training data...")
df = pd.read_csv('data/factory_tasks_enhanced.csv')
print(f"   ✅ Loaded {len(df)} tasks with extracted features")

print("\n📊 Step 2: Preparing features...")
feature_columns = [
    'category_weight', 'high_priority_keywords', 'low_priority_keywords',
    'safety_keywords', 'task_length', 'has_urgent_words',
    'equipment_count', 'cleaning_count'
]

X = df[feature_columns]
y = df['priority']

print(f"   ✅ Features: {feature_columns}")
print(f"   ✅ Feature matrix shape: {X.shape}")
print(f"\n   Priority distribution:")
print(y.value_counts())

print("\n🔀 Step 3: Splitting data into train/test...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   ✅ Training samples: {len(X_train)}")
print(f"   ✅ Testing samples: {len(X_test)}")

print("\n🎓 Step 4: Training Decision Tree classifier...")
model = DecisionTreeClassifier(
    max_depth=5,
    min_samples_split=2,
    random_state=42
)
model.fit(X_train, y_train)
print(f"   ✅ Model trained successfully")

print("\n✅ Step 5: Evaluating model...")
y_train_pred = model.predict(X_train)
train_accuracy = accuracy_score(y_train, y_train_pred)
print(f"   ✅ Training accuracy: {train_accuracy:.2%}")

y_test_pred = model.predict(X_test)
test_accuracy = accuracy_score(y_test, y_test_pred)
print(f"   ✅ Test accuracy: {test_accuracy:.2%}")

print("\n" + "=" * 70)
print("DETAILED CLASSIFICATION REPORT:")
print("=" * 70)
print(classification_report(y_test, y_test_pred))

print("=" * 70)
print("CONFUSION MATRIX:")
print("=" * 70)
cm = confusion_matrix(y_test, y_test_pred, labels=['High', 'Medium', 'Low'])
print("\nActual vs Predicted:")
print(pd.DataFrame(
    cm,
    index=['Actual: High', 'Actual: Medium', 'Actual: Low'],
    columns=['Predicted: High', 'Predicted: Medium', 'Predicted: Low']
))

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE (What matters most?):")
print("=" * 70)
importance_df = pd.DataFrame({
    'Feature': feature_columns,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)
print(importance_df.to_string(index=False))

print("\n" + "=" * 70)
print("💾 Step 6: Saving model...")
os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/priority_model.pkl')
print(f"   ✅ Model saved: models/priority_model.pkl")

print("\n" + "=" * 70)
print("✅ TRAINING COMPLETE!")
print("=" * 70)
