"""
Factory Task AI - Main Entry Point

Run this to start the GUI application
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the GUI app
from ui.app import main

if __name__ == "__main__":
    print("🏭 Factory Task AI System - Starting GUI...")
    main()
