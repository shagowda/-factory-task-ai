"""
Database Manager

Handles all database operations:
- Create tables
- Insert tasks
- Query tasks
- Caching
- Statistics
"""

import sys
import os
import sqlite3
import hashlib
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.schema import DATABASE_SCHEMA

class DatabaseManager:
    """Manage all database operations"""
    
    def __init__(self, db_path='database/factory_tasks.db'):
        """Initialize database connection"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.connection = None
        self.connect()
    
    def connect(self):
        """Connect to database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Return rows as dicts
        print(f"✅ Connected to database: {self.db_path}")
    
    def initialize_database(self):
        """Create all tables"""
        cursor = self.connection.cursor()
        cursor.executescript(DATABASE_SCHEMA)
        self.connection.commit()
        print("✅ Database schema created")
    
    def add_task(self, task_description, category=None, created_by="system", due_datetime=None):
        """
        Add a new task
        Returns: task_id
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO tasks 
            (task_description, category, created_by, due_datetime)
            VALUES (?, ?, ?, ?)
        ''', (task_description, category, created_by, due_datetime))
        self.connection.commit()
        return cursor.lastrowid
    
    def add_prediction(self, task_id, ai_priority, ai_category, final_priority, 
                      final_category, was_overridden, override_reason):
        """Add prediction record"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO predictions
            (task_id, ai_priority, ai_category, final_priority, final_category, 
             was_overridden, override_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (task_id, ai_priority, ai_category, final_priority, final_category,
              1 if was_overridden else 0, override_reason))
        self.connection.commit()
    
    def add_audit_log(self, task_id, action, reason, critical_keywords, audit_level):
        """Add audit log entry"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO audit_log
            (task_id, action, reason, critical_keywords, audit_level)
            VALUES (?, ?, ?, ?, ?)
        ''', (task_id, action, reason, ','.join(critical_keywords) if critical_keywords else None, audit_level))
        self.connection.commit()
    
    def get_task(self, task_id):
        """Get task by ID"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_tasks(self, status=None):
        """Get all tasks, optionally filtered by status"""
        cursor = self.connection.cursor()
        if status:
            cursor.execute('SELECT * FROM tasks WHERE completion_status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_tasks_by_priority(self, priority):
        """Get all tasks with specific priority"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT t.*, p.final_priority FROM tasks t
            JOIN predictions p ON t.task_id = p.task_id
            WHERE p.final_priority = ?
            ORDER BY t.due_datetime ASC
        ''', (priority,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_tasks_by_category(self, category):
        """Get all tasks in specific category"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM tasks WHERE category = ? ORDER BY created_at DESC', (category,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_pending_tasks(self):
        """Get all pending (not completed) tasks"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT t.*, p.final_priority FROM tasks t
            LEFT JOIN predictions p ON t.task_id = p.task_id
            WHERE t.completion_status = 'pending'
            ORDER BY p.final_priority DESC, t.due_datetime ASC
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def complete_task(self, task_id):
        """Mark task as completed"""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE tasks 
            SET completion_status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE task_id = ?
        ''', (task_id,))
        self.connection.commit()
        return True
    
    # CACHING METHODS
    
    def hash_task_description(self, task_description):
        """Create hash of task description for caching"""
        return hashlib.md5(task_description.lower().encode()).hexdigest()
    
    def check_cache(self, task_description):
        """
        Check if prediction for this task exists in cache
        Returns: (hit, category, priority) or (False, None, None)
        """
        task_hash = self.hash_task_description(task_description)
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT predicted_category, predicted_priority, cache_hit_count 
            FROM prediction_cache 
            WHERE task_hash = ?
        ''', (task_hash,))
        row = cursor.fetchone()
        
        if row:
            # Update hit count
            cursor.execute('''
                UPDATE prediction_cache 
                SET cache_hit_count = cache_hit_count + 1, last_hit = CURRENT_TIMESTAMP
                WHERE task_hash = ?
            ''', (task_hash,))
            self.connection.commit()
            return True, row[0], row[1]
        
        return False, None, None
    
    def add_to_cache(self, task_description, predicted_category, predicted_priority):
        """Add prediction to cache"""
        task_hash = self.hash_task_description(task_description)
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO prediction_cache
                (task_hash, task_description, predicted_category, predicted_priority)
                VALUES (?, ?, ?, ?)
            ''', (task_hash, task_description, predicted_category, predicted_priority))
            self.connection.commit()
            return True
        except sqlite3.IntegrityError:
            # Already exists
            return False
    
    def get_cache_stats(self):
        """Get cache statistics"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_cached,
                SUM(cache_hit_count) as total_hits,
                AVG(cache_hit_count) as avg_hits
            FROM prediction_cache
        ''')
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    # STATISTICS METHODS
    
    def get_task_statistics(self):
        """Get today's task statistics"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT t.*, p.final_priority FROM tasks t
            LEFT JOIN predictions p ON t.task_id = p.task_id
            WHERE DATE(t.created_at) = DATE('now')
        ''')
        tasks = [dict(row) for row in cursor.fetchall()]
        
        stats = {
            'total_tasks': len(tasks),
            'high_priority': len([t for t in tasks if t.get('final_priority') == 'High']),
            'medium_priority': len([t for t in tasks if t.get('final_priority') == 'Medium']),
            'low_priority': len([t for t in tasks if t.get('final_priority') == 'Low']),
            'completed': len([t for t in tasks if t['completion_status'] == 'completed']),
            'pending': len([t for t in tasks if t['completion_status'] == 'pending']),
        }
        
        return stats
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("🗄️ DATABASE MANAGER TESTING")
    print("=" * 70)
    
    # Initialize
    db = DatabaseManager()
    db.initialize_database()
    
    # Add test tasks
    print("\n📝 Adding test tasks...")
    task_ids = []
    test_tasks = [
        ("Clean contaminated milk tank", "Hygiene & Safety"),
        ("Label boxes for shipping", "Packaging"),
        ("Check temperature sensors", "Quality Control"),
    ]
    
    for desc, cat in test_tasks:
        tid = db.add_task(desc, cat, "worker1")
        task_ids.append(tid)
        print(f"   ✅ Task {tid}: {desc}")
    
    # Add predictions
    print("\n🧠 Adding predictions...")
    db.add_prediction(task_ids[0], "High", "Hygiene & Safety", "High", 
                     "Hygiene & Safety", False, None)
    db.add_prediction(task_ids[1], "Low", "Packaging", "Low", 
                     "Packaging", False, None)
    
    # Test caching
    print("\n💾 Testing cache...")
    task = "Clean contaminated milk tank"
    hit, cat, pri = db.check_cache(task)
    if not hit:
        db.add_to_cache(task, "Hygiene & Safety", "High")
        print(f"   ✅ Added to cache")
    
    hit, cat, pri = db.check_cache(task)
    if hit:
        print(f"   ✅ Cache HIT: {cat} / {pri}")
    
    # Get pending tasks
    print("\n📋 Pending tasks:")
    pending = db.get_pending_tasks()
    for task in pending:
        print(f"   {task['task_id']}: {task['task_description']}")
    
    # Get statistics
    print("\n📊 Today's statistics:")
    stats = db.get_task_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Complete a task
    print(f"\n✅ Completing task {task_ids[0]}...")
    db.complete_task(task_ids[0])
    
    # Get updated stats
    print("\n📊 Updated statistics:")
    stats = db.get_task_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    db.close()
    print("\n✅ DATABASE TEST COMPLETE!")
