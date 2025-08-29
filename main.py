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

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing_deps = []
    
    try:
        import customtkinter
    except ImportError:
        missing_deps.append("customtkinter")
    
    try:
        import ultralytics
    except ImportError:
        missing_deps.append("ultralytics")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
        
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 Please install dependencies using:")
        print("   pip install " + " ".join(missing_deps))
        print("\n   Or run the setup scripts:")
        print("   - install_setup_cuda.bat (for NVIDIA GPUs)")
        print("   - install_setup_directml.bat (for AMD/Intel GPUs)")
        return False
    return True

def main():
    """
    Main orchestrator function that starts the Eventuri-AI application.
    
    This function:
    1. Checks dependencies
    2. Initializes the core configuration
    3. Sets up the AI detection system
    4. Configures hardware connections
    5. Launches the GUI application
    """
    
    print("🚀 Starting Eventuri-AI for MAKCU v2...")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
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
        
        print("=" * 50)
        print("🎯 Launching Eventuri-AI GUI...")
        print("💡 Use the GUI to configure and start the aimbot")
        print("=" * 50)
        
        app = EventuriGUI()
        app.mainloop()
        
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        print("Please ensure all dependencies are installed.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("👋 Eventuri-AI application closed.")

if __name__ == "__main__":
    main()