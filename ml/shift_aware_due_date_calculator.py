"""
Shift-Aware Due-Date Calculation

Makes sure HIGH priority safety tasks complete
within the same shift (don't leave them for next shift)
"""

import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from ml.due_date_calculator import DueDateCalculator

class ShiftAwareDueDateCalculator(DueDateCalculator):
    """Extended calculator that respects shift boundaries"""
    
    def calculate_due_date_shift_aware(self, priority, category, current_time=None, respect_shift_boundary=True):
        """
        Calculate due date with shift awareness
        
        For HIGH priority safety tasks, ensure they finish in same shift
        """
        
        if current_time is None:
            current_time = datetime.now()
        
        # Get base calculation
        due_info = self.calculate_due_date(priority, category, current_time)
        
        # If HIGH priority safety, respect shift boundary
        if priority == 'High' and category == 'Hygiene & Safety' and respect_shift_boundary:
            current_shift = self.get_current_shift(current_time)
            shift_times = self.shifts[current_shift]
            
            # Calculate shift end time
            if current_shift == 'Night':
                # Night shift ends at 06:00 next day
                shift_end = current_time.replace(hour=6, minute=0, second=0, microsecond=0)
                if shift_end <= current_time:
                    shift_end += timedelta(days=1)
            else:
                shift_end = current_time.replace(hour=shift_times['end'], minute=0, second=0, microsecond=0)
            
            # If due date exceeds shift end, cap it
            if due_info['due_datetime'] > shift_end:
                due_info['due_datetime'] = shift_end
                due_info['hours_available'] = int((shift_end - current_time).total_seconds() / 3600)
                due_info['explanation'] += f" [CAPPED TO SHIFT END]"
        
        return due_info

# Test
if __name__ == "__main__":
    calculator = ShiftAwareDueDateCalculator()
    
    print("=" * 70)
    print("⏰ SHIFT-AWARE DUE-DATE EXAMPLES")
    print("=" * 70)
    
    # Test at different times
    test_times = [
        datetime(2025, 12, 29, 10, 0),  # Morning
        datetime(2025, 12, 29, 20, 0),  # Afternoon
        datetime(2025, 12, 29, 23, 0),  # Night
    ]
    
    for test_time in test_times:
        print(f"\n🕐 Current Time: {test_time.strftime('%H:%M')} ({calculator.get_current_shift(test_time)} Shift)")
        print("-" * 70)
        
        due_info = calculator.calculate_due_date_shift_aware(
            'High', 'Hygiene & Safety', test_time
        )
        print(f"Due: {due_info['due_datetime'].strftime('%H:%M')}")
        print(f"Hours: {due_info['hours_available']}h")
        print(f"Note: {due_info['explanation']}")
