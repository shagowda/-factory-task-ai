"""
Task Categorization Model Training Script

This script:
1. Loads training data (factory_tasks.csv)
2. Preprocesses text (clean, lowercase)
3. Vectorizes text (TF-IDF)
4. Trains Logistic Regression model
5. Evaluates accuracy
6. Saves the model
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

print("=" * 70)
print("🧠 TASK CATEGORIZATION MODEL TRAINING")
print("=" * 70)

# Step 1: Load Data
print("\n📂 Step 1: Loading training data...")
df = pd.read_csv('data/factory_tasks.csv')
print(f"   ✅ Loaded {len(df)} tasks")
print(f"   ✅ Categories: {df['category'].unique().tolist()}")

# Step 2: Prepare Data
print("\n📊 Step 2: Preparing data...")
X = df['task_description']  # Input (what we read)
y = df['category']           # Output (what we predict)

# Split into training (80%) and testing (20%)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"   ✅ Training samples: {len(X_train)}")
print(f"   ✅ Testing samples: {len(X_test)}")

# Step 3: Text Preprocessing & Vectorization
print("\n🔤 Step 3: Text vectorization (TF-IDF)...")
vectorizer = TfidfVectorizer(
    lowercase=True,              # Convert to lowercase
    stop_words='english',        # Remove common words (the, a, and, etc)
    max_features=100,            # Keep top 100 important words
    ngram_range=(1, 2)           # Use single words and two-word combinations
)
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)
print(f"   ✅ Vectorizer created")
print(f"   ✅ Feature dimension: {X_train_vectorized.shape[1]} features")

# Step 4: Train Model
print("\n🎓 Step 4: Training Logistic Regression model...")
model = LogisticRegression(max_iter=200, random_state=42)
model.fit(X_train_vectorized, y_train)
print(f"   ✅ Model trained successfully")

# Step 5: Evaluate on Training Data
print("\n✅ Step 5: Evaluating model...")
y_train_pred = model.predict(X_train_vectorized)
train_accuracy = accuracy_score(y_train, y_train_pred)
print(f"   ✅ Training accuracy: {train_accuracy:.2%}")

# Evaluate on Test Data
y_test_pred = model.predict(X_test_vectorized)
test_accuracy = accuracy_score(y_test, y_test_pred)
print(f"   ✅ Test accuracy: {test_accuracy:.2%}")

# Detailed Classification Report
print("\n" + "=" * 70)
print("DETAILED CLASSIFICATION REPORT:")
print("=" * 70)
print(classification_report(y_test, y_test_pred))

# Confusion Matrix
print("=" * 70)
print("CONFUSION MATRIX (What predictions were wrong?):")
print("=" * 70)
cm = confusion_matrix(y_test, y_test_pred, labels=model.classes_)
print("\nActual vs Predicted:")
print(pd.DataFrame(
    cm,
    index=[f'Actual: {cat}' for cat in model.classes_],
    columns=[f'Predicted: {cat}' for cat in model.classes_]
))

# Step 6: Save Model and Vectorizer
print("\n" + "=" * 70)
print("💾 Step 6: Saving model...")

# Create models folder if it doesn't exist
os.makedirs('models', exist_ok=True)

joblib.dump(model, 'models/categorization_model.pkl')
print(f"   ✅ Model saved: models/categorization_model.pkl")

joblib.dump(vectorizer, 'models/categorization_vectorizer.pkl')
print(f"   ✅ Vectorizer saved: models/categorization_vectorizer.pkl")

# Step 7: Test with Example
print("\n" + "=" * 70)
print("🧪 Step 7: Testing with real examples...")
print("=" * 70)

test_tasks = [
    "Clean storage tank",
    "Check temperature on production line",
    "Load ingredients into mixer",
    "Replace broken conveyor belt",
    "Box and seal products"
]

for task in test_tasks:
    task_vectorized = vectorizer.transform([task])
    prediction = model.predict(task_vectorized)[0]
    confidence = model.predict_proba(task_vectorized)[0].max()
    print(f"\n📋 Task: '{task}'")
    print(f"   → Category: {prediction}")
    print(f"   → Confidence: {confidence:.1%}")

print("\n" + "=" * 70)
print("✅ TRAINING COMPLETE!")
print("=" * 70)
print("\nModel is ready for production use!")
