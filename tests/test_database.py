"""
Unit Tests for Database Manager

Tests database operations
"""

import sys
import os
import unittest
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Create temporary database for each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        self.db = DatabaseManager(self.db_path)
        self.db.initialize_database()
    
    def tearDown(self):
        """Clean up database"""
        self.db.close()
        os.unlink(self.db_path)
    
    def test_add_task(self):
        """Test adding a task"""
        task_id = self.db.add_task(
            "Clean tank",
            "Hygiene & Safety",
            "worker1"
        )
        
        # Should return valid ID
        self.assertIsNotNone(task_id)
        self.assertGreater(task_id, 0)
    
    def test_get_task(self):
        """Test retrieving a task"""
        task_id = self.db.add_task(
            "Clean tank",
            "Hygiene & Safety",
            "worker1"
        )
        
        task = self.db.get_task(task_id)
        
        self.assertIsNotNone(task)
        self.assertEqual(task['task_description'], "Clean tank")
        self.assertEqual(task['category'], "Hygiene & Safety")
    
    def test_add_prediction(self):
        """Test adding prediction record"""
        task_id = self.db.add_task("Clean tank", "Hygiene & Safety", "worker1")
        
        self.db.add_prediction(
            task_id,
            "High",
            "Hygiene & Safety",
            "High",
            "Hygiene & Safety",
            False,
            None
        )
        
        # Get task to verify prediction was saved
        task = self.db.get_task(task_id)
        self.assertIsNotNone(task)
    
    def test_get_pending_tasks(self):
        """Test retrieving pending tasks"""
        # Add 3 tasks
        for i in range(3):
            self.db.add_task(f"Task {i}", "Production", "worker1")
        
        pending = self.db.get_pending_tasks()
        
        # Should have 3 pending tasks
        self.assertEqual(len(pending), 3)
    
    def test_complete_task(self):
        """Test marking task as completed"""
        task_id = self.db.add_task("Task", "Production", "worker1")
        
        # Complete it
        self.db.complete_task(task_id)
        
        # Get task
        task = self.db.get_task(task_id)
        
        # Should be marked complete
        self.assertEqual(task['completion_status'], 'completed')
        self.assertIsNotNone(task['completed_at'])
    
    def test_get_tasks_by_priority(self):
        """Test filtering tasks by priority"""
        task_id1 = self.db.add_task("High task", "Hygiene & Safety", "worker1")
        task_id2 = self.db.add_task("Low task", "Packaging", "worker1")
        
        self.db.add_prediction(task_id1, "High", "Hygiene & Safety", "High", "Hygiene & Safety", False, None)
        self.db.add_prediction(task_id2, "Low", "Packaging", "Low", "Packaging", False, None)
        
        high_tasks = self.db.get_tasks_by_priority("High")
        
        # Should get 1 HIGH task
        self.assertEqual(len(high_tasks), 1)
    
    def test_cache_hit(self):
        """Test prediction caching"""
        task = "Clean contaminated tank"
        
        # First check (miss)
        hit, cat, pri = self.db.check_cache(task)
        self.assertFalse(hit)
        
        # Add to cache
        self.db.add_to_cache(task, "Hygiene & Safety", "High")
        
        # Second check (hit)
        hit, cat, pri = self.db.check_cache(task)
        self.assertTrue(hit)
        self.assertEqual(cat, "Hygiene & Safety")
        self.assertEqual(pri, "High")
    
    def test_cache_hit_count(self):
        """Test cache hit counting"""
        task = "Clean tank"
        self.db.add_to_cache(task, "Hygiene & Safety", "High")
        
        # First hit
        self.db.check_cache(task)
        # Second hit
        self.db.check_cache(task)
        
        stats = self.db.get_cache_stats()
        
        # Should have 2 hits
        self.assertEqual(stats['total_hits'], 2)
    
    def test_task_statistics(self):
        """Test statistics calculation"""
        # Add tasks
        self.db.add_task("Task 1", "Hygiene & Safety", "worker1")
        self.db.add_task("Task 2", "Packaging", "worker1")
        
        stats = self.db.get_task_statistics()
        
        # Should have 2 total tasks
        self.assertEqual(stats['total_tasks'], 2)
        self.assertEqual(stats['pending'], 2)

if __name__ == "__main__":
    unittest.main()
