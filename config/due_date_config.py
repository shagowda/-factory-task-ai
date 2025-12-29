"""
Due-Date Configuration

Rules for calculating due dates based on priority
and shift awareness.
"""

# Priority-to-hours mapping
PRIORITY_HOURS = {
    'High': 2,      # Complete within 2 hours
    'Medium': 8,    # Complete within 8 hours
    'Low': 24       # Complete within 24 hours
}

# Shift timings (24-hour format)
SHIFTS = {
    'Morning': {'start': 6, 'end': 14},      # 06:00 - 14:00
    'Afternoon': {'start': 14, 'end': 22},   # 14:00 - 22:00
    'Night': {'start': 22, 'end': 30}        # 22:00 - 06:00 (next day)
}

# Category-based priority boost (emergency overrides)
CATEGORY_URGENCY = {
    'Hygiene & Safety': 0.75,    # 25% faster for safety (multiply hours)
    'Quality Control': 0.9,       # 10% faster for quality
    'Production': 1.0,            # Normal speed
    'Maintenance': 0.85,          # 15% faster (equipment downtime costly)
    'Packaging': 1.0              # Normal speed
}

# Maximum task duration before forced split
MAX_TASK_DURATION_HOURS = 4

# Safety rules (never violate these)
SAFETY_RULES = {
    'Hygiene & Safety': 'High',     # Always HIGH if safety
    'Quality Control': 'High',      # Usually HIGH
}
