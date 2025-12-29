"""
Due-Date Suggestion Engine

Calculates due dates based on:
- Task priority
- Category
- Current time and shift
- Factory shift schedule
"""

import sys
import os

# Add parent directory to Python path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from config.due_date_config import (
    PRIORITY_HOURS,
    SHIFTS,
    CATEGORY_URGENCY,
    SAFETY_RULES
)

class DueDateCalculator:
    """Calculate due dates for factory tasks"""
    
    def __init__(self):
        self.priority_hours = PRIORITY_HOURS
        self.shifts = SHIFTS
        self.category_urgency = CATEGORY_URGENCY
    
    def get_current_shift(self, current_time=None):
        """Determine current shift based on time"""
        if current_time is None:
            current_time = datetime.now()
        
        hour = current_time.hour
        
        if 6 <= hour < 14:
            return 'Morning'
        elif 14 <= hour < 22:
            return 'Afternoon'
        else:
            return 'Night'
    
    def calculate_due_date(self, priority, category, current_time=None):
        """
        Calculate due date for a task
        
        Args:
            priority: 'High', 'Medium', or 'Low'
            category: Task category
            current_time: datetime object (default: now)
        
        Returns:
            dict with:
            - due_datetime: When task is due
            - hours_available: How many hours to complete
            - shift: Current shift
            - explanation: Human-readable explanation
        """
        
        if current_time is None:
            current_time = datetime.now()
        
        # Get base hours from priority
        base_hours = self.priority_hours.get(priority, 8)
        
        # Apply category urgency (safety faster)
        urgency_multiplier = self.category_urgency.get(category, 1.0)
        hours_available = int(base_hours * urgency_multiplier)
        
        # Ensure minimum 1 hour
        hours_available = max(1, hours_available)
        
        # Calculate due datetime
        due_datetime = current_time + timedelta(hours=hours_available)
        
        # Get shift info
        current_shift = self.get_current_shift(current_time)
        
        # Build explanation
        explanation = f"{priority} priority task (base: {base_hours}h)"
        
        if urgency_multiplier < 1.0:
            speedup = int((1 - urgency_multiplier) * 100)
            explanation += f" → {speedup}% faster for {category}"
        
        explanation += f" → {hours_available} hours available"
        
        return {
            'due_datetime': due_datetime,
            'hours_available': hours_available,
            'shift': current_shift,
            'explanation': explanation,
            'priority': priority,
            'category': category,
            'created_at': current_time
        }
    
    def format_due_date(self, due_info):
        """Format due date info for display"""
        due_dt = due_info['due_datetime']
        hours = due_info['hours_available']
        category = due_info['category']
        priority = due_info['priority']
        
        # Color coding
        priority_colors = {
            'High': '🔴',
            'Medium': '🟡',
            'Low': '🟢'
        }
        color = priority_colors.get(priority, '⚪')
        
        # Format output
        return f"""
{color} PRIORITY: {priority}
📅 DUE DATE: {due_dt.strftime('%Y-%m-%d %H:%M')}
⏱️  TIME AVAILABLE: {hours} hours
📂 CATEGORY: {category}
📝 REASON: {due_info['explanation']}
"""

# Example usage
if __name__ == "__main__":
    calculator = DueDateCalculator()
    
    # Test cases
    test_cases = [
        ('High', 'Hygiene & Safety'),
        ('Medium', 'Production'),
        ('Low', 'Packaging'),
        ('High', 'Quality Control'),
        ('Medium', 'Maintenance'),
    ]
    
    print("=" * 70)
    print("⏰ DUE-DATE CALCULATION EXAMPLES")
    print("=" * 70)
    
    for priority, category in test_cases:
        due_info = calculator.calculate_due_date(priority, category)
        formatted = calculator.format_due_date(due_info)
        print(formatted)
