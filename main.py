#!/usr/bin/env python3
"""
Main Entry Point for the TIMESAT Toolkit

This script serves as the primary entry point for running the TIMESAT toolkit.
It reads a JSON settings file that contains all necessary configurations and file paths,
and then calls the 'run()' function from the 'timesatimage' module to start processing.

Usage:
    python main.py [settings.json]

If no settings file is specified, the script defaults to using 'settings.json'.

For any further questions or assistance, please contact:
    zhanzhang.cai@nateko.lu.se
"""

import sys
import os
from timesatimage import run

def main():
    """
    Main function that initializes the TIMESAT processing.

    This function checks for a command-line argument to determine which settings
    file to use. If no argument is provided, it defaults to 'settings.json'. It then
    verifies that the settings file exists before proceeding with processing.

    Returns:
        None
    """
    # Default settings file
    settings_file = "settings.json"
    
    # If a settings file is provided as a command-line argument, use it instead
    if len(sys.argv) > 1:
        settings_file = sys.argv[1]
    
    print(f"Using settings file: {settings_file}")
    
    # Check if the settings file exists
    if not os.path.isfile(settings_file):
        print(f"Error: Settings file '{settings_file}' not found.")
        sys.exit(1)
    
    run(settings_file)

if __name__ == "__main__":
    main()
