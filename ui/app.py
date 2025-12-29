"""
Factory Task AI - Main GUI Application

A professional Tkinter GUI for factory task management
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import joblib
from ml.priority_feature_extractor import PriorityFeatureExtractor
from ml.shift_aware_due_date_calculator import ShiftAwareDueDateCalculator
from ml.safety_rules_engine import SafetyRulesEngine
from database.db_manager import DatabaseManager

class FactoryTaskApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏭 Factory Task AI Management System")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Initialize systems
        self.setup_systems()
        
        # Create UI
        self.setup_ui()
        
        # Current suggestion (for approval/rejection)
        self.current_suggestion = None
    
    def setup_systems(self):
        """Load all models and initialize systems"""
        print("📂 Loading systems...")
        
        self.categorization_model = joblib.load('models/categorization_model.pkl')
        self.categorization_vectorizer = joblib.load('models/categorization_vectorizer.pkl')
        self.priority_model = joblib.load('models/priority_model.pkl')
        
        self.feature_extractor = PriorityFeatureExtractor()
        self.due_date_calculator = ShiftAwareDueDateCalculator()
        self.safety_engine = SafetyRulesEngine()
        self.db = DatabaseManager()
        self.db.initialize_database()
        
        print("✅ All systems loaded")
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Configure colors
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2196F3"
        self.danger_color = "#f44336"
        self.success_color = "#4CAF50"
        self.warning_color = "#ff9800"
        self.high_color = "#f44336"    # Red
        self.medium_color = "#ff9800"   # Orange
        self.low_color = "#4CAF50"      # Green
        
        self.root.configure(bg=self.bg_color)
        
        # Create main frame with padding
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_new_task_tab()
        self.create_pending_tasks_tab()
        self.create_statistics_tab()
        self.create_audit_tab()
    
    def create_new_task_tab(self):
        """Tab 1: Create new task"""
        
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📝 New Task")
        tab.configure(style="")
        
        # Title
        title = tk.Label(
            tab, 
            text="Create New Task", 
            font=("Arial", 18, "bold"),
            bg=self.bg_color
        )
        title.pack(pady=20)
        
        # Main content frame
        content_frame = tk.Frame(tab, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side: Input
        left_frame = tk.Frame(content_frame, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Task description input
        tk.Label(left_frame, text="Task Description:", font=("Arial", 12, "bold"), bg=self.bg_color).pack(anchor=tk.W)
        self.task_input = tk.Text(left_frame, height=6, width=40, font=("Arial", 10))
        self.task_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons frame
        button_frame = tk.Frame(left_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=10)
        
        submit_btn = tk.Button(
            button_frame,
            text="🚀 ANALYZE TASK",
            command=self.analyze_task,
            bg=self.primary_color,
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10
        )
        submit_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="🔄 CLEAR",
            command=self.clear_input,
            bg="#999999",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=10
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Right side: Suggestions
        right_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(right_frame, text="AI SUGGESTIONS", font=("Arial", 12, "bold"), bg="white").pack(anchor=tk.W, padx=15, pady=10)
        
        # Suggestion details frame
        details_frame = tk.Frame(right_frame, bg="white")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Category
        tk.Label(details_frame, text="Category:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        self.suggestion_category = tk.Label(details_frame, text="—", font=("Arial", 10), bg="white", fg="#666666")
        self.suggestion_category.pack(anchor=tk.W, padx=20)
        
        # AI Priority
        tk.Label(details_frame, text="AI Priority:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W, pady=(10, 0))
        self.suggestion_ai_priority = tk.Label(details_frame, text="—", font=("Arial", 10), bg="white", fg="#666666")
        self.suggestion_ai_priority.pack(anchor=tk.W, padx=20)
        
        # Final Priority
        tk.Label(details_frame, text="Final Priority:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W, pady=(10, 0))
        self.suggestion_final_priority = tk.Label(details_frame, text="—", font=("Arial", 10, "bold"), bg="white")
        self.suggestion_final_priority.pack(anchor=tk.W, padx=20)
        
        # Due Date
        tk.Label(details_frame, text="Due Date:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W, pady=(10, 0))
        self.suggestion_due = tk.Label(details_frame, text="—", font=("Arial", 10), bg="white", fg="#666666")
        self.suggestion_due.pack(anchor=tk.W, padx=20)
        
        # Override reason - FIXED: wraplength in Label, not pack()
        tk.Label(details_frame, text="Override Reason:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W, pady=(10, 0))
        self.suggestion_override = tk.Label(
            details_frame, 
            text="None", 
            font=("Arial", 9), 
            bg="white", 
            fg="#666666",
            wraplength=250,  # ✅ Put wraplength HERE
            justify=tk.LEFT
        )
        self.suggestion_override.pack(anchor=tk.W, padx=20)
        
        # Keywords - FIXED: wraplength in Label, not pack()
        tk.Label(details_frame, text="Keywords Found:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W, pady=(10, 0))
        self.suggestion_keywords = tk.Label(
            details_frame, 
            text="None", 
            font=("Arial", 9), 
            bg="white", 
            fg="#666666",
            wraplength=250,  # ✅ Put wraplength HERE
            justify=tk.LEFT
        )
        self.suggestion_keywords.pack(anchor=tk.W, padx=20)
        
        # Action buttons
        action_frame = tk.Frame(right_frame, bg="white")
        action_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.approve_btn = tk.Button(
            action_frame,
            text="✅ APPROVE & CREATE",
            command=self.approve_task,
            bg=self.success_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=8,
            state=tk.DISABLED
        )
        self.approve_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.reject_btn = tk.Button(
            action_frame,
            text="❌ REJECT",
            command=self.reject_task,
            bg=self.danger_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=8,
            state=tk.DISABLED
        )
        self.reject_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_pending_tasks_tab(self):
        """Tab 2: View pending tasks"""
        
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 Pending Tasks")
        
        # Title
        title = tk.Label(tab, text="Pending Tasks", font=("Arial", 18, "bold"), bg=self.bg_color)
        title.pack(pady=20)
        
        # Refresh button
        btn_frame = tk.Frame(tab, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        refresh_btn = tk.Button(
            btn_frame,
            text="🔄 REFRESH",
            command=self.refresh_pending_tasks,
            bg=self.primary_color,
            fg="white",
            font=("Arial", 10, "bold")
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Tasks listbox with scrollbar
        list_frame = tk.Frame(tab, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tasks_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10),
            height=20
        )
        self.tasks_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tasks_listbox.yview)
        
        # Status bar
        status_frame = tk.Frame(tab, bg="#e0e0e0")
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.pending_status = tk.Label(status_frame, text="Click 'Refresh' to load pending tasks", bg="#e0e0e0")
        self.pending_status.pack(anchor=tk.W, padx=10, pady=5)
        
        # Load initial data
        self.refresh_pending_tasks()
    
    def create_statistics_tab(self):
        """Tab 3: Statistics"""
        
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Statistics")
        
        # Title
        title = tk.Label(tab, text="Today's Statistics", font=("Arial", 18, "bold"), bg=self.bg_color)
        title.pack(pady=20)
        
        # Stats frame
        stats_frame = tk.Frame(tab, bg=self.bg_color)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create stat boxes
        self.create_stat_box(stats_frame, "Total Tasks", 0, 0, "#2196F3")
        self.create_stat_box(stats_frame, "🔴 HIGH", 0, 1, self.high_color)
        self.create_stat_box(stats_frame, "🟡 MEDIUM", 0, 2, self.medium_color)
        self.create_stat_box(stats_frame, "🟢 LOW", 1, 0, self.low_color)
        self.create_stat_box(stats_frame, "Completed", 1, 1, "#4CAF50")
        self.create_stat_box(stats_frame, "Pending", 1, 2, "#ff9800")
        
        # Refresh button
        refresh_btn = tk.Button(
            tab,
            text="🔄 REFRESH STATS",
            command=self.update_statistics,
            bg=self.primary_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=10
        )
        refresh_btn.pack(pady=20)
        
        # Load initial stats
        self.update_statistics()
    
    def create_stat_box(self, parent, label, row, col, color):
        """Create a statistics box"""
        
        box = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=2)
        box.grid(row=row, column=col, padx=10, pady=10, sticky="nsew", ipadx=20, ipady=20)
        
        # Make columns expandable
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        label_widget = tk.Label(box, text=label, font=("Arial", 12, "bold"), bg=color, fg="white")
        label_widget.pack()
        
        value_widget = tk.Label(box, text="0", font=("Arial", 28, "bold"), bg=color, fg="white")
        value_widget.pack()
        
        # Store reference
        if "Total" in label:
            self.stat_total = value_widget
        elif "HIGH" in label:
            self.stat_high = value_widget
        elif "MEDIUM" in label:
            self.stat_medium = value_widget
        elif "LOW" in label:
            self.stat_low = value_widget
        elif "Completed" in label:
            self.stat_completed = value_widget
        elif "Pending" in label:
            self.stat_pending = value_widget
    
    def create_audit_tab(self):
        """Tab 4: Audit log"""
        
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 Audit Log")
        
        # Title
        title = tk.Label(tab, text="Safety Audit Log", font=("Arial", 18, "bold"), bg=self.bg_color)
        title.pack(pady=20)
        
        # Refresh button
        btn_frame = tk.Frame(tab, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        refresh_btn = tk.Button(
            btn_frame,
            text="🔄 REFRESH",
            command=self.refresh_audit_log,
            bg=self.primary_color,
            fg="white",
            font=("Arial", 10, "bold")
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Audit log text area
        log_frame = tk.Frame(tab, bg=self.bg_color)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.audit_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            width=80,
            font=("Courier", 9),
            bg="#f5f5f5"
        )
        self.audit_text.pack(fill=tk.BOTH, expand=True)
        self.audit_text.config(state=tk.DISABLED)
        
        # Load initial data
        self.refresh_audit_log()
    
    def analyze_task(self):
        """Analyze task and show suggestions"""
        
        task_description = self.task_input.get("1.0", tk.END).strip()
        
        if not task_description:
            messagebox.showwarning("Input Error", "Please enter a task description")
            return
        
        try:
            # Step 1: Categorize
            task_vec = self.categorization_vectorizer.transform([task_description])
            ai_category = self.categorization_model.predict(task_vec)[0]
            
            # Step 2: Predict priority
            features = self.feature_extractor.extract_features(task_description, ai_category)
            feature_order = [
                'category_weight', 'high_priority_keywords', 'low_priority_keywords',
                'safety_keywords', 'task_length', 'has_urgent_words',
                'equipment_count', 'cleaning_count'
            ]
            X = [[features[f] for f in feature_order]]
            ai_priority = self.priority_model.predict(X)[0]
            
            # Step 3: Apply safety rules
            safety_result = self.safety_engine.apply_safety_rules(
                task_description, ai_category, ai_priority
            )
            final_priority = safety_result['final_priority']
            
            # Step 4: Calculate due date
            due_info = self.due_date_calculator.calculate_due_date_shift_aware(
                final_priority, ai_category
            )
            
            # Store suggestion
            self.current_suggestion = {
                'task_description': task_description,
                'ai_category': ai_category,
                'ai_priority': ai_priority,
                'final_priority': final_priority,
                'due_datetime': due_info['due_datetime'],
                'override_reason': safety_result['override_reason'],
                'critical_keywords': safety_result['critical_keywords']
            }
            
            # Update display
            priority_colors = {'High': self.high_color, 'Medium': self.medium_color, 'Low': self.low_color}
            
            self.suggestion_category.config(text=ai_category)
            self.suggestion_ai_priority.config(text=ai_priority)
            self.suggestion_final_priority.config(
                text=final_priority,
                fg=priority_colors.get(final_priority, "#000000")
            )
            self.suggestion_due.config(text=due_info['due_datetime'].strftime('%Y-%m-%d %H:%M'))
            
            override_text = safety_result['override_reason'] if safety_result['override_reason'] else "None"
            self.suggestion_override.config(text=override_text)
            
            keywords_text = ", ".join(safety_result['critical_keywords']) if safety_result['critical_keywords'] else "None"
            self.suggestion_keywords.config(text=keywords_text)
            
            # Enable action buttons
            self.approve_btn.config(state=tk.NORMAL)
            self.reject_btn.config(state=tk.NORMAL)
            
            messagebox.showinfo("Success", "Task analyzed! Review suggestions and approve/reject.")
        
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
    
    def approve_task(self):
        """Approve and create task"""
        
        if not self.current_suggestion:
            messagebox.showwarning("Error", "No task to approve")
            return
        
        try:
            suggestion = self.current_suggestion
            
            # Add to database
            task_id = self.db.add_task(
                suggestion['task_description'],
                suggestion['ai_category'],
                "worker1",  # TODO: Get actual user
                suggestion['due_datetime']
            )
            
            # Add prediction
            self.db.add_prediction(
                task_id,
                suggestion['ai_priority'],
                suggestion['ai_category'],
                suggestion['final_priority'],
                suggestion['ai_category'],
                bool(suggestion['override_reason']),
                suggestion['override_reason']
            )
            
            # Add audit log
            self.db.add_audit_log(
                task_id,
                "task_created",
                f"Priority: {suggestion['ai_priority']} → {suggestion['final_priority']}",
                suggestion['critical_keywords'],
                "CRITICAL" if suggestion['override_reason'] else "INFO"
            )
            
            messagebox.showinfo("Success", f"✅ Task #{task_id} created successfully!")
            
            # Clear input
            self.clear_input()
            
            # Refresh views
            self.refresh_pending_tasks()
            self.update_statistics()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create task: {str(e)}")
    
    def reject_task(self):
        """Reject task"""
        self.clear_input()
        messagebox.showinfo("Rejected", "Task rejected and not created.")
    
    def clear_input(self):
        """Clear input fields"""
        self.task_input.delete("1.0", tk.END)
        self.suggestion_category.config(text="—")
        self.suggestion_ai_priority.config(text="—")
        self.suggestion_final_priority.config(text="—")
        self.suggestion_due.config(text="—")
        self.suggestion_override.config(text="None")
        self.suggestion_keywords.config(text="None")
        self.approve_btn.config(state=tk.DISABLED)
        self.reject_btn.config(state=tk.DISABLED)
        self.current_suggestion = None
    
    def refresh_pending_tasks(self):
        """Load and display pending tasks"""
        try:
            self.tasks_listbox.delete(0, tk.END)
            
            pending = self.db.get_pending_tasks()
            
            if not pending:
                self.tasks_listbox.insert(tk.END, "No pending tasks! 🎉")
                self.pending_status.config(text="Total pending: 0")
                return
            
            for task in pending:
                priority = task.get('final_priority', 'Unknown')
                priority_emoji = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(priority, '⚪')
                
                display_text = f"{priority_emoji} [{task['task_id']}] {task['task_description'][:50]} (Due: {task['due_datetime']})"
                self.tasks_listbox.insert(tk.END, display_text)
            
            self.pending_status.config(text=f"Total pending: {len(pending)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {str(e)}")
    
    def update_statistics(self):
        """Update statistics display"""
        try:
            stats = self.db.get_task_statistics()
            
            self.stat_total.config(text=str(stats.get('total_tasks', 0)))
            self.stat_high.config(text=str(stats.get('high_priority', 0)))
            self.stat_medium.config(text=str(stats.get('medium_priority', 0)))
            self.stat_low.config(text=str(stats.get('low_priority', 0)))
            self.stat_completed.config(text=str(stats.get('completed', 0)))
            self.stat_pending.config(text=str(stats.get('pending', 0)))
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load statistics: {str(e)}")
    
    def refresh_audit_log(self):
        """Load and display audit log"""
        try:
            self.audit_text.config(state=tk.NORMAL)
            self.audit_text.delete(1.0, tk.END)
            
            logs = self.safety_engine.get_audit_log()
            
            if not logs:
                self.audit_text.insert(tk.END, "No audit logs yet.\n")
            else:
                for log in logs:
                    level_emoji = {'INFO': 'ℹ️', 'WARNING': '⚠️', 'CRITICAL': '🔴'}.get(log.get('audit_level', 'INFO'))
                    text = f"{level_emoji} [{log['timestamp']}] Task #{log['task_id']}: {log['action']}\n"
                    text += f"   Reason: {log['reason']}\n"
                    if log.get('critical_keywords'):
                        text += f"   Keywords: {', '.join(log['critical_keywords'])}\n"
                    text += "\n"
                    self.audit_text.insert(tk.END, text)
            
            self.audit_text.config(state=tk.DISABLED)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load audit log: {str(e)}")

def main():
    """Run the application"""
    root = tk.Tk()
    app = FactoryTaskApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
