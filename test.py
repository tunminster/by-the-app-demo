#!/usr/bin/env python3
"""
Quick Test Runner
Simple way to run tests from project root
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Change to project root directory
os.chdir(project_root)

if __name__ == "__main__":
    # Import and run the main test function
    try:
        from tests.run_all_tests import main
        main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the project root directory")
        print("💡 Try: python tests/run_all_tests.py quick")
        sys.exit(1)
