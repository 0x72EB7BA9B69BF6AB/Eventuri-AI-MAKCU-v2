#!/usr/bin/env python3
"""
EVENTURI-AI for MAKCU v2 - Main Orchestrator

This is the main entry point for the Eventuri-AI application.
It orchestrates all the components and provides a clean interface
to start the application.

Author: Eventuri-AI Team
"""

import sys
import os

# Add src directory to Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """
    Main orchestrator function that starts the Eventuri-AI application.
    
    This function:
    1. Initializes the core configuration
    2. Sets up the AI detection system
    3. Configures hardware connections
    4. Launches the GUI application
    """
    
    print("🚀 Starting Eventuri-AI for MAKCU v2...")
    
    try:
        # Import core configuration
        from core.config import config
        print("✅ Core configuration loaded")
        
        # Initialize AI detection system
        from ai.detection import load_model
        print("✅ AI detection system initialized")
        
        # Initialize hardware systems
        from hardware.mouse import Mouse
        from hardware.capture import get_camera
        print("✅ Hardware systems initialized")
        
        # Launch GUI application
        from gui.application import EventuriGUI
        print("✅ GUI system loaded")
        
        print("🎯 Launching Eventuri-AI GUI...")
        app = EventuriGUI()
        app.mainloop()
        
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        print("Please ensure all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    
    print("👋 Eventuri-AI application closed.")

if __name__ == "__main__":
    main()