"""
Safety Keywords Configuration

These keywords indicate safety-critical tasks
that should always be HIGH priority
"""

# Safety-critical keywords
SAFETY_KEYWORDS = [
    'clean', 'sanitize', 'disinfect',
    'contamination', 'contaminated',
    'urgent', 'immediately', 'asap',
    'dangerous', 'hazard', 'risk',
    'health', 'food safety', 'allergy',
    'temperature', 'bacteria', 'mold',
    'expired', 'disposal',
    'fire', 'emergency', 'shutdown'
]

# Category priority weights (base scores)
CATEGORY_PRIORITY_WEIGHTS = {
    'Hygiene & Safety': 3,
    'Quality Control': 2,
    'Production': 1,
    'Maintenance': 1,
    'Packaging': 0
}

# Keywords that indicate high priority
HIGH_PRIORITY_KEYWORDS = [
    'urgent', 'immediately', 'asap', 'critical',
    'contamination', 'contaminated', 'dangerous',
    'emergency', 'shutdown', 'broken', 'failed',
    'health', 'safety', 'allergy', 'expired'
]

# Keywords that indicate low priority
LOW_PRIORITY_KEYWORDS = [
    'organize', 'organize', 'schedule', 'plan',
    'nice to have', 'optional', 'when available'
]
