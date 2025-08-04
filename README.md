# EVENTURI-AI for MAKCU

The ultimate AI aimbot and detection GUI for Windows, supporting YOLOv8–v12 models and a range of USB serial devices.
Made for the MAKCU community, with custom class selection for multiple games and super-smooth, modern UI.

---

## Features

Supports YOLOv8–v12 (PyTorch .pt, ONNX .onnx, TensorRT .engine)

Device support out-of-the-box for:
- MAKCU (1A86:55D3)
- CH343 (1A86:5523)
- CH340 (1A86:7523)
- CH347 (1A86:5740)
- CP2102 (10C4:EA60)

Custom class selection for different games (target what matters)

Fast aimbot with multiple modes: Normal, Bezier, Silent, Smooth/WindMouse

Profile system: save, load, and reset configs

Built with CustomTkinter for a polished, dark, responsive GUI

DirectML and CUDA 12.6 support (choose the best for your GPU)

Visual feedback for device connection, FPS, and AI status

---

## Installation

NOTE: CUDA support is only for NVIDIA GPUs, and only CUDA 12.6 is supported at this time. If you’re on AMD or Intel GPU, use DirectML mode.

---

1. Clone the repo

git clone https://github.com/MAKCUAI/Eventuri-AI-MAKCU-v2
cd Eventuri-AI-MAKCU-v2

---

2. Setup for NVIDIA (CUDA 12.6 only)
Only for Nvidia gpus
Download and install CUDA 12.6:
NVIDIA CUDA 12.6 Download: https://developer.download.nvidia.com/compute/cuda/12.6.0/local_installers/cuda_12.6.0_560.76_windows.exe

Run the CUDA installer and make sure everything is installed properly.

In this folder, run:
```install_setup_cuda.bat```

When done, start the app:
```run_eventuri_ai.bat```

---

3. Setup for DirectML (AMD/Intel/NVIDIA)
only for (AMD/Intel) gpus
(No special driver install required.)

In this folder, run:
```install_setup_directml.bat```

When done, start the app:
```run_eventuri_ai.bat```

DirectML is easiest to install and works with most GPUs, but is typically 5–10% slower than CUDA.

---

## Usage

Connect your device (see supported list above).

Start the app with one of the .bat launchers.

Select your AI model (.pt, .onnx, .engine) from the dropdown.

Configure detection/aim settings, select your classes/game targets.

Press START AIMBOT, change sensitivity to your in-game sens, hold your activation key, and you’re set.

---

## Supported Devices

| VID:PID     | Name    |
|-------------|---------|
| 1A86:55D3   | MAKCU   |
| 1A86:5523   | CH343   |
| 1A86:7523   | CH340   |
| 1A86:5740   | CH347   |
| 10C4:EA60   | CP2102  |

---

## FAQ

Q: What YOLO versions does this support?
A: YOLOv8 to YOLOv12, in .pt, .onnx, and .engine formats.

Q: Can I use it for any game?
A: Yes—just select the correct model and target classes for your game in the GUI.

Q: Do I need NVIDIA?
A: No, you can use DirectML (for AMD, Intel, or NVIDIA). CUDA is just faster (NVIDIA only, CUDA 12.6 required).

Q: My device isn’t recognized.
A: Only the VID:PID list above is supported by default. For other hardware, ask in the issues.

---

## Troubleshooting

"CUDA not found": Make sure you installed CUDA 12.6, not any other version.

App crashes or fails to load models: Check your model file, device drivers, and dependencies.

---

## Credits

Made with ♥ by Ahmo934 and Jealousyhaha for the MAKCU Community.

---

Enjoy!
If you need more help or want to suggest a feature, open an issue or pull request.
