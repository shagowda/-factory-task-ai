"""
Create enhanced training data with priority scores
"""

import pandas as pd
from ml.priority_feature_extractor import PriorityFeatureExtractor

df = pd.read_csv('data/factory_tasks.csv')

extractor = PriorityFeatureExtractor()

features_list = []
scores_list = []

for idx, row in df.iterrows():
    task_desc = row['task_description']
    category = row['category']
    priority = row['priority']
    
    score, features = extractor.calculate_priority_score(task_desc, category)
    scores_list.append(score)
    features_list.append(features)

features_df = pd.DataFrame(features_list)

df_enhanced = pd.concat([df, features_df, pd.DataFrame({'priority_score': scores_list})], axis=1)

print("Enhanced Dataset with Features:")
print(df_enhanced.head(10))

df_enhanced.to_csv('data/factory_tasks_enhanced.csv', index=False)
print(f"\n✅ Enhanced dataset saved: data/factory_tasks_enhanced.csv")
