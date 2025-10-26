"""
Updated MaidCat Toolbar Registration using Toolbar Manager
This script replaces the original init_toolbar.py with a cleaner, data-driven approach
"""

import sys
import os

# Add the ToolbarManager path
ta_python_path = r"d:\GitHub\See1Unreal5\TA\TAPython\Python"
if ta_python_path not in sys.path:
    sys.path.insert(0, ta_python_path)

try:
    from ToolbarManager import create_toolbar_manager_with_basic_config
    
    # Use the basic config which includes the MaidCat button
    toolbar_manager = create_toolbar_manager_with_basic_config()
    
    if toolbar_manager:
        print("MaidCat Toolbar registered successfully using Toolbar Manager!")
    else:
        print("Failed to register MaidCat Toolbar")
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure ToolbarManager is in the Python path")
    
    # Fallback to direct path import
    try:
        sys.path.insert(0, r"d:\GitHub\See1Unreal5\TA\TAPython\Python\ToolbarManager")
        import toolbar_manager
        toolbar_manager = toolbar_manager.create_toolbar_manager_with_basic_config()
        if toolbar_manager:
            print("MaidCat Toolbar registered successfully (fallback method)!")
    except Exception as fallback_error:
        print(f"Fallback also failed: {fallback_error}")
        
except Exception as e:
    print(f"Error initializing MaidCat Toolbar: {e}")
    import traceback
    traceback.print_exc()