import sqlite3

db = sqlite3.connect('database/factory_tasks.db')
db.row_factory = sqlite3.Row

# Show tasks
print("=" * 70)
print("TASKS IN DATABASE")
print("=" * 70)
cursor = db.execute('SELECT * FROM tasks')
for row in cursor:
    print(f"ID: {row['task_id']}, Status: {row['completion_status']}, Desc: {row['task_description'][:50]}")

# Show predictions
print("\n" + "=" * 70)
print("PREDICTIONS IN DATABASE")
print("=" * 70)
cursor = db.execute('SELECT * FROM predictions')
for row in cursor:
    print(f"Task: {row['task_id']}, AI: {row['ai_priority']}, Final: {row['final_priority']}, Overridden: {row['was_overridden']}")

# Show audit logs
print("\n" + "=" * 70)
print("AUDIT LOGS IN DATABASE")
print("=" * 70)
cursor = db.execute('SELECT * FROM audit_log')
for row in cursor:
    print(f"Task: {row['task_id']}, Action: {row['action']}, Level: {row['audit_level']}")

db.close()
