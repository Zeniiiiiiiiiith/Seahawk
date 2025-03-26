"""
Wrapper script to run the Harvester GUI dashboard
with proper import paths.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now we can import modules from the project
from harvester.network_scanner import NetworkScanner

# Import and run the GUI
from harvester.gui.dashboard import main

if __name__ == "__main__":
    main()