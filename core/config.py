import os
import json
import ctypes
import platform

# Only import wintypes on Windows
if platform.system() == "Windows":
    from ctypes import wintypes

# Structures
class RECT(ctypes.Structure):
    _fields_ = [
        ("left",   ctypes.c_long),
        ("top",    ctypes.c_long),
        ("right",  ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize",   ctypes.c_ulong),
        ("rcMonitor", RECT),
        ("rcWork",    RECT),
        ("dwFlags",   ctypes.c_ulong),
    ]

def get_foreground_monitor_resolution():
    # Only run on Windows
    if platform.system() != "Windows":
        return 1920, 1080  # Default resolution for non-Windows
    
    # DPI awareness so we get actual pixels
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    user32 = ctypes.windll.user32
    monitor = user32.MonitorFromWindow(user32.GetForegroundWindow(), 2)  # MONITOR_DEFAULTTONEAREST = 2
    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)

    if ctypes.windll.user32.GetMonitorInfoW(monitor, ctypes.byref(mi)):
        w = mi.rcMonitor.right - mi.rcMonitor.left
        h = mi.rcMonitor.bottom - mi.rcMonitor.top
        return w, h
    else:
        # fallback to primary if anything fails
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

w, h = get_foreground_monitor_resolution()

class Config:
    def __init__(self):
        # --- General Settings ---
        self.region_size = 200
        w, h = get_foreground_monitor_resolution()
        self.screen_width = w # Revert to original
        self.screen_height = h  # Revert to original
        self.player_y_offset = 5 # Offset for player detection
        self.capturer_mode = "NDI"  # Default to MSS mode
        self.always_on_aim = False
        self.main_pc_width = 1920  # Default width for main PC
        self.main_pc_height = 1080  # Default height for main PC

        # --- Model and Detection ---
        self.models_dir = "models"
        self.model_path = os.path.join(self.models_dir, "Click here to Load a model")
        self.custom_player_label = "Select a Player Class"  
        self.custom_head_label = "Select a Head Class"  
        self.model_file_size = 0
        self.model_load_error = ""
        self.conf = 0.2
        self.imgsz = 640
        self.max_detect = 50
        
        # --- Mouse / MAKCU ---
        self.selected_mouse_button = 3   # Default to middle mouse button
        self.makcu_connected = False # Updated to reflect device type
        self.makcu_status_msg = "Disconnected"  # Updated to reflect device type
        self.aim_humanization = 0 # Default to no humanization
        self.in_game_sens = 1.3 # Default smoothing
        self.button_mask = False # Default to no button masking

        # --- Trigger Settings ---
        self.trigger_enabled         = getattr(self, "trigger_enabled", False)   # master on/off
        self.trigger_always_on       = getattr(self, "trigger_always_on", False) # fire even without holding key
        self.trigger_button          = getattr(self, "trigger_button", 1)        # 0..4 -> Left, Right, Middle, Side4, Side5

        self.trigger_radius_px       = getattr(self, "trigger_radius_px", 8)     # how close to crosshair (px)
        self.trigger_delay_ms        = getattr(self, "trigger_delay_ms", 30)     # delay before click
        self.trigger_cooldown_ms     = getattr(self, "trigger_cooldown_ms", 120) # time between clicks
        self.trigger_min_conf        = getattr(self, "trigger_min_conf", 0.35)   # min conf to shoot


        # --- Aimbot Mode ---
        self.mode = "normal"    
        self.aimbot_running = False
        self.aimbot_status_msg = "Stopped"

        # --- Normal Aim ---
        self.normal_x_speed = 0.5
        self.normal_y_speed = 0.5

        # --- Bezier Aim ---
        self.bezier_segments = 8
        self.bezier_ctrl_x = 16
        self.bezier_ctrl_y = 16

        # --- Silent Aim ---
        self.silent_segments = 7
        self.silent_ctrl_x = 18
        self.silent_ctrl_y = 18
        self.silent_speed = 3
        self.silent_cooldown = 0.18

        # --- Smooth Aim (WindMouse) ---
        self.smooth_gravity = 9.0          # Gravitational pull towards target (1-20)
        self.smooth_wind = 3.0             # Wind randomness effect (1-20)  
        self.smooth_min_delay = 0.0      # Minimum delay between steps (seconds)
        self.smooth_max_delay = 0.002     # Maximum delay between steps (seconds)
        self.smooth_max_step = 40.0        # Maximum pixels per step
        self.smooth_min_step = 2.0         # Minimum pixels per step
        self.smooth_max_step_ratio = 0.20   # Max step as ratio of total distance
        self.smooth_target_area_ratio = 0.06  # Stop when within this ratio of distance
        
        # Human-like behavior settings
        self.smooth_reaction_min = 0.05    # Min reaction time to new targets (seconds)
        self.smooth_reaction_max = 0.21    # Max reaction time to new targets (seconds)
        self.smooth_close_range = 35       # Distance considered "close" (pixels)
        self.smooth_far_range = 250        # Distance considered "far" (pixels) 
        self.smooth_close_speed = 0.8      # Speed multiplier when close to target
        self.smooth_far_speed = 1.00        # Speed multiplier when far from target
        self.smooth_acceleration = 1.15     # Acceleration curve strength
        self.smooth_deceleration = 1.05     # Deceleration curve strength
        self.smooth_fatigue_effect = 1.2   # How much fatigue affects shakiness
        self.smooth_micro_corrections = 0  # Small random corrections (pixels)

        # --- Last error/status for GUI display
        self.last_error = ""
        self.last_info = ""

        # --- Debug window toggle ---
        self.show_debug_window = False

        # --- Ndi Settings ---
        self.ndi_width = 0
        self.ndi_height = 0
        self.ndi_sources = []
        self.ndi_selected_source = None

    # -- Profile functions --
    def save(self, path="config_profile.json"):
        data = self.__dict__.copy()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    def load(self, path="config_profile.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                self.__dict__.update(json.load(f))
    def reset_to_defaults(self):
        self.__init__()

    # --- Utility ---
    def list_models(self):
        return [f for f in os.listdir(self.models_dir)
                if f.endswith(".engine")]

config = Config()