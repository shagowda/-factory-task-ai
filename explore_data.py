import pandas as pd

# Load the dataset
df = pd.read_csv('data/factory_tasks.csv')

print("=" * 60)
print("📊 FACTORY TASK DATASET ANALYSIS")
print("=" * 60)

# Basic info
print(f"\n✅ Total tasks: {len(df)}")
print(f"✅ Columns: {list(df.columns)}")

# Category breakdown
print("\n" + "=" * 60)
print("CATEGORY BREAKDOWN:")
print("=" * 60)
print(df['category'].value_counts())

# Priority breakdown
print("\n" + "=" * 60)
print("PRIORITY BREAKDOWN:")
print("=" * 60)
print(df['priority'].value_counts())

# Priority by Category
print("\n" + "=" * 60)
print("PRIORITY BY CATEGORY:")
print("=" * 60)
print(pd.crosstab(df['category'], df['priority']))

# Average completion time by priority
print("\n" + "=" * 60)
print("AVERAGE COMPLETION TIME BY PRIORITY:")
print("=" * 60)
avg_time = df.groupby('priority')['completion_time_minutes'].mean()
print(avg_time.round(2))

# Shift breakdown
print("\n" + "=" * 60)
print("SHIFT BREAKDOWN:")
print("=" * 60)
print(df['shift'].value_counts())

# Show first few rows
print("\n" + "=" * 60)
print("FIRST 5 TASKS:")
print("=" * 60)
print(df.head())

print("\n✅ Data exploration complete!")
