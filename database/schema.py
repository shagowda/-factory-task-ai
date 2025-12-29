"""
Database Schema Design

Defines tables for:
- Tasks
- Predictions
- Audit logs
- Cache
"""

DATABASE_SCHEMA = '''

-- Tasks Table (stores all factory tasks)
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_description TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    due_datetime TIMESTAMP,
    completion_status TEXT DEFAULT 'pending',
    completed_at TIMESTAMP,
    notes TEXT
);

-- Predictions Table (stores ML predictions)
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    ai_priority TEXT,
    ai_category TEXT,
    final_priority TEXT,
    final_category TEXT,
    was_overridden INTEGER,
    override_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

-- Audit Log Table (stores all actions for compliance)
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    action TEXT,
    reason TEXT,
    critical_keywords TEXT,
    audit_level TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

-- Cache Table (stores predictions for repeated tasks)
CREATE TABLE IF NOT EXISTS prediction_cache (
    cache_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_hash TEXT UNIQUE,
    task_description TEXT,
    predicted_category TEXT,
    predicted_priority TEXT,
    cache_hit_count INTEGER DEFAULT 0,
    last_hit TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Statistics Table (for dashboard/reporting)
CREATE TABLE IF NOT EXISTS task_statistics (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_recorded DATE DEFAULT CURRENT_DATE,
    total_tasks INTEGER,
    high_priority_count INTEGER,
    medium_priority_count INTEGER,
    low_priority_count INTEGER,
    overridden_count INTEGER,
    completed_count INTEGER,
    avg_completion_hours REAL
);

'''
