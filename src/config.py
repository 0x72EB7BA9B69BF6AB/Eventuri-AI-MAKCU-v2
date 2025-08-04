import os
import json

class Config:
    def __init__(self):
        # --- General Settings ---
        self.region_size = 200
        self.screen_width = 1920  # Revert to original
        self.screen_height = 1080  # Revert to original
        self.player_y_offset = 5

        # --- Model and Detection ---
        self.models_dir = "models"
        self.model_path = os.path.join(self.models_dir, "load_a_model")
        self.custom_player_label = "player"  
        self.custom_head_label = "head"  
        self.model_file_size = 0
        self.model_load_error = ""
        self.conf = 0.2
        self.imgsz = 640
        self.max_detect = 50
        
        # --- Mouse / MAKCU ---
        self.selected_mouse_button = 3   
        self.makcu_connected = False
        self.makcu_status_msg = "Disconnected"  # Updated to reflect device type
        self.aim_humanization = 0
        self.in_game_sens = 0.3

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
        self.smooth_min_delay = 0.001      # Minimum delay between steps (seconds)
        self.smooth_max_delay = 0.008      # Maximum delay between steps (seconds)
        self.smooth_max_step = 15.0        # Maximum pixels per step
        self.smooth_min_step = 1.0         # Minimum pixels per step
        self.smooth_max_step_ratio = 0.1   # Max step as ratio of total distance
        self.smooth_target_area_ratio = 0.02  # Stop when within this ratio of distance
        
        # Human-like behavior settings
        self.smooth_reaction_min = 0.05    # Min reaction time to new targets (seconds)
        self.smooth_reaction_max = 0.15    # Max reaction time to new targets (seconds)
        self.smooth_close_range = 30       # Distance considered "close" (pixels)
        self.smooth_far_range = 150        # Distance considered "far" (pixels) 
        self.smooth_close_speed = 0.3      # Speed multiplier when close to target
        self.smooth_far_speed = 0.8        # Speed multiplier when far from target
        self.smooth_acceleration = 0.4     # Acceleration curve strength
        self.smooth_deceleration = 0.6     # Deceleration curve strength
        self.smooth_fatigue_effect = 2.0   # How much fatigue affects shakiness
        self.smooth_micro_corrections = 1  # Small random corrections (pixels)

        # --- Last error/status for GUI display
        self.last_error = ""
        self.last_info = ""

        # --- Debug window toggle ---
        self.show_debug_window = False

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