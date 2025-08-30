import os
import sys
import subprocess

VENV_DIR = "venv"
REQUIREMENTS = "requirements.txt"
PYTHON_EXE = sys.executable  # path to current python

# 1. Create the venv if it doesn't exist
if not os.path.isdir(VENV_DIR):
    print("[*] Creating virtual environment...")
    subprocess.check_call([PYTHON_EXE, "-m", "venv", VENV_DIR])
else:
    print(f"[*] Virtual environment '{VENV_DIR}' already exists.")

# 2. Figure out path to venv python
if os.name == "nt":  # Windows
    venv_python = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:  # macOS/Linux
    venv_python = os.path.join(VENV_DIR, "bin", "python")

# 3. Upgrade pip
print("[*] Upgrading pip inside venv...")
subprocess.check_call([venv_python, "-m", "pip", "install", "--upgrade", "pip"])

# 4. Install requirements
if os.path.isfile(REQUIREMENTS):
    print(f"[*] Installing from {REQUIREMENTS}...")
    subprocess.check_call([venv_python, "-m", "pip", "install", "-r", REQUIREMENTS])
else:
    # Step 1: Install torch, torchvision, torchaudio with custom index
    print("[*] Installing torch, torchvision, torchaudio with CUDA from PyTorch index...")
    subprocess.check_call([
        venv_python, "-m", "pip", "install",
        "torch", "torchvision", "torchaudio",
        "--index-url", "https://download.pytorch.org/whl/cu126"
    ])
    # Step 2: Install remaining packages
    packages = [
        "customtkinter", "opencv-python", "pyserial", "mss", "ultralytics",
        "tensorrt==10.11.0.33", "onnx", "onnxruntime-directml", "cyndilib", "dxcam"
    ]
    print(f"[*] {REQUIREMENTS} not found. Installing default packages: {packages}")
    subprocess.check_call([venv_python, "-m", "pip", "install"] + packages)

# 5. Run patch.py using the venv's Python
patch_script = "utils/patch.py"
if os.path.exists(patch_script):
    print(f"[*] Running patch.py...")
    subprocess.check_call([venv_python, patch_script])
else:
    print("[!] patch.py not found! Skipping patch step.")

print("[+] Done! To activate the venv, run:")
if os.name == "nt":
    print(r"   venv\Scripts\activate")
else:
    print(r"   source venv/bin/activate")
