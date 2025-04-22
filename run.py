#!/usr/bin/env python3
"""
Quick launcher script for the Tarkov Map Assistant.
"""
import os
import sys

# Add the src directory to the Python path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

from tarkov_app.main import main

if __name__ == "__main__":
    sys.exit(main())