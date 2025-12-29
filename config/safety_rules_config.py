"""
Safety Rules Configuration

Defines keywords, rules, and thresholds for food safety
"""

# Critical safety keywords (always = HIGH priority)
CRITICAL_SAFETY_KEYWORDS = {
    'contamination', 'contaminated', 'mold', 'bacterial',
    'allergen', 'allergy', 'foreign object', 'glass',
    'chemical', 'toxic', 'poison', 'pest',
    'temperature', 'cold chain', 'freezer', 'refrigerator',
    'expired', 'spoiled', 'rotten',
    'recall', 'shutdown', 'emergency',
    'immediate', 'immediately', 'urgent', 'asap'
}

# Warning keywords (usually = HIGH priority)
WARNING_KEYWORDS = {
    'clean', 'sanitize', 'disinfect', 'wash',
    'hazard', 'risk', 'dangerous', 'unsafe',
    'failure', 'broken', 'leaking',
    'inspection', 'audit', 'compliance'
}

# Categories that are ALWAYS safety-critical
ALWAYS_SAFETY_CRITICAL_CATEGORIES = {
    'Hygiene & Safety',
    'Quality Control'
}

# Safety rules (if these trigger, override priority)
SAFETY_RULES = [
    {
        'name': 'Critical Contamination',
        'keywords': ['contamination', 'contaminated', 'mold', 'bacterial'],
        'override_priority': 'High',
        'reason': 'Food safety risk'
    },
    {
        'name': 'Allergen Risk',
        'keywords': ['allergen', 'allergy', 'cross contamination'],
        'override_priority': 'High',
        'reason': 'Allergen risk'
    },
    {
        'name': 'Temperature Control',
        'keywords': ['temperature', 'cold chain', 'freezer', 'refrigerator', 'overheat'],
        'override_priority': 'High',
        'reason': 'Temperature control critical'
    },
    {
        'name': 'Equipment Failure',
        'keywords': ['broken', 'failure', 'shutdown', 'emergency'],
        'override_priority': 'High',
        'reason': 'Equipment safety risk'
    },
    {
        'name': 'Expired Product',
        'keywords': ['expired', 'spoiled', 'rotten', 'recall'],
        'override_priority': 'High',
        'reason': 'Product safety'
    }
]

# Minimum priority allowed (can't go below this)
MINIMUM_PRIORITY_BY_CATEGORY = {
    'Hygiene & Safety': 'High',      # Safety never below HIGH
    'Quality Control': 'Medium',     # Quality at least MEDIUM
    'Production': 'Low',
    'Maintenance': 'Low',
    'Packaging': 'Low'
}

# Audit logging levels
AUDIT_LEVELS = {
    'INFO': 'Routine task creation',
    'WARNING': 'Priority overridden (safety)',
    'CRITICAL': 'Emergency condition detected'
}
