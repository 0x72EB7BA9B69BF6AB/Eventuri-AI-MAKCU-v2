from config import config
import customtkinter as ctk
from gui_constants import NEON, BG, neon_button
from mouse import test_move  # Added import for test_move

class GUISections:
    def build_ui(self):
        # --- STATUS BAR ---
        status_bar = ctk.CTkFrame(self, fg_color=BG)
        status_bar.pack(padx=0, pady=(6, 8), fill="x")
        ctk.CTkLabel(status_bar, text="MAKCU:", text_color="#ccc", bg_color=BG, font=("Segoe UI", 14)).pack(side="left", padx=(12, 2))
        self.conn_status_lbl = ctk.CTkLabel(status_bar, textvariable=self.connection_status, text_color=self.connection_color.get(), font=("Segoe UI", 14, "bold"))
        self.conn_status_lbl.pack(side="left", padx=(0, 18))
        self.fps_label = ctk.CTkLabel(status_bar, textvariable=self.fps_var, font=("Segoe UI", 13, "bold"), text_color="#00e676")
        self.fps_label.pack(side="right", padx=10)
        ctk.CTkLabel(status_bar, text="Aimbot:", text_color="#ccc", bg_color=BG, font=("Segoe UI", 14)).pack(side="left", padx=(2, 2))
        ctk.CTkLabel(status_bar, textvariable=self.aimbot_status, text_color=NEON, font=("Segoe UI", 14, "bold")).pack(side="left", padx=(0, 18))
        ctk.CTkLabel(status_bar, text="Model:", text_color="#ccc", bg_color=BG, font=("Segoe UI", 14)).pack(side="left", padx=(2, 2))
        ctk.CTkLabel(status_bar, textvariable=self.model_name, text_color="#00bcd4", font=("Segoe UI", 14, "bold")).pack(side="left", padx=(0, 5))
        ctk.CTkLabel(status_bar, textvariable=self.model_size, text_color="#B0B0B0", font=("Segoe UI", 12, "italic")).pack(side="left")
        self.error_lbl = ctk.CTkLabel(status_bar, textvariable=self.error_text, text_color=NEON, font=("Segoe UI", 13, "bold"))
        self.error_lbl.pack(side="right", padx=8)
        
        # --- MAKCU CONTROLS ---
        makcu_frame = ctk.CTkFrame(self, fg_color=BG)
        makcu_frame.pack(fill="x", padx=10, pady=(0, 8))
        self.connect_btn = neon_button(makcu_frame, text="Connect to MAKCU", command=self.on_connect)
        self.connect_btn.pack(side="left", padx=(10, 5), pady=8)
        ctk.CTkButton(makcu_frame, text="Test Move", command=test_move, fg_color="#181818", hover_color="#000000").pack(side="left", padx=8)
        self.debug_checkbox = ctk.CTkCheckBox(makcu_frame, text="Show Debug Window", variable=self.debug_checkbox_var, onvalue=True, offvalue=False, text_color="#fff", command=self.on_debug_toggle)
        self.debug_checkbox.pack(side="left", padx=8)
        self.input_check_checkbox = ctk.CTkCheckBox(makcu_frame, text="Show Input Check", variable=self.input_check_var, onvalue=True, offvalue=False, text_color="#fff", command=self.on_input_check_toggle)
        self.input_check_checkbox.pack(side="left", padx=8)
        
        # --- DETECTION SETTINGS (Enhanced) ---
        detection_frame = ctk.CTkFrame(self, fg_color=BG)
        detection_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        # Add detection settings label
        detection_label = ctk.CTkLabel(detection_frame, text="🎯 Detection Settings", text_color="#00e676", font=("Segoe UI", 16, "bold"))
        detection_label.grid(row=0, column=0, columnspan=3, pady=(8, 12), sticky="w", padx=6)
        
        # Confidence with enhanced feedback
        ctk.CTkLabel(detection_frame, text="Confidence Threshold", text_color="#fff", font=("Segoe UI", 12, "bold")).grid(row=1, column=0, sticky="w", padx=6)
        self.conf_slider = ctk.CTkSlider(
            detection_frame, from_=0.05, to=0.95, number_of_steps=18, command=self.update_conf
        )
        self.conf_slider.grid(row=1, column=1, padx=(2,2), sticky="ew")
        self.conf_value = ctk.CTkLabel(detection_frame, text=f"{config.conf:.2f}", text_color="#ff5e69", width=50, font=("Segoe UI", 12, "bold"))
        self.conf_value.grid(row=1, column=2, padx=2)
        
        # Confidence explanation
        conf_help = ctk.CTkLabel(detection_frame, text="Lower = more detections (less accurate), Higher = fewer detections (more accurate)", 
                                text_color="#888", font=("Segoe UI", 10, "italic"))
        conf_help.grid(row=2, column=0, columnspan=3, padx=6, pady=(2, 8), sticky="w")
        
        # Image Size
        ctk.CTkLabel(detection_frame, text="Detection Resolution", text_color="#fff", font=("Segoe UI", 12, "bold")).grid(row=3, column=0, sticky="w", padx=6)
        self.imgsz_slider = ctk.CTkSlider(
            detection_frame, from_=320, to=1280, number_of_steps=12, command=self.update_imgsz
        )
        self.imgsz_slider.grid(row=3, column=1, padx=(2,2), sticky="ew")
        self.imgsz_value = ctk.CTkLabel(detection_frame, text=str(config.imgsz), text_color="#ff5e69", width=50, font=("Segoe UI", 12, "bold"))
        self.imgsz_value.grid(row=3, column=2, padx=2)
        
        # Max Detections
        ctk.CTkLabel(detection_frame, text="Max Detections", text_color="#fff", font=("Segoe UI", 12, "bold")).grid(row=4, column=0, sticky="w", padx=6)
        self.max_detect_var = ctk.IntVar(value=config.max_detect)
        self.max_detect_slider = ctk.CTkSlider(
            detection_frame, from_=1, to=100, number_of_steps=99,
            command=self.update_max_detect
        )
        self.max_detect_slider.set(config.max_detect)
        self.max_detect_slider.grid(row=4, column=1, padx=(2, 2), sticky="ew")
        self.max_detect_label = ctk.CTkLabel(detection_frame, text=str(config.max_detect), text_color="#ff5e69", width=50, font=("Segoe UI", 12, "bold"))
        self.max_detect_label.grid(row=4, column=2, padx=2)
        
        # Configure column weights for proper stretching
        detection_frame.grid_columnconfigure(1, weight=1)
        
        # --- FOV / OFFSET / MOUSE BUTTONS ---
        control_frame = ctk.CTkFrame(self, fg_color=BG)
        control_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        # Add control settings label
        control_label = ctk.CTkLabel(control_frame, text="🎮 Aim Settings", text_color="#00e676", font=("Segoe UI", 16, "bold"))
        control_label.grid(row=0, column=0, columnspan=3, pady=(8, 12), sticky="w", padx=6)
        
        ctk.CTkLabel(control_frame, text="FOV Size", text_color="#fff").grid(row=1, column=0, sticky="w", padx=6)
        self.fov_slider = ctk.CTkSlider(control_frame, from_=20, to=250, command=self.update_fov, number_of_steps=180)
        self.fov_slider.grid(row=1, column=1, padx=(2,2), sticky="ew")
        self.fov_value = ctk.CTkLabel(control_frame, text=str(config.region_size), text_color="#ff5e69", width=40)
        self.fov_value.grid(row=1, column=2, padx=2)
        
        ctk.CTkLabel(control_frame, text="Player Y Offset", text_color="#fff").grid(row=2, column=0, sticky="w", padx=6)
        self.offset_slider = ctk.CTkSlider(control_frame, from_=0, to=20, command=self.update_offset, number_of_steps=20)
        self.offset_slider.grid(row=2, column=1, padx=(2,2), sticky="ew")
        self.offset_value = ctk.CTkLabel(control_frame, text=str(config.player_y_offset), text_color="#ff5e69", width=40)
        self.offset_value.grid(row=2, column=2, padx=2)
        
        ctk.CTkLabel(control_frame, text="In Game Sens", text_color="#fff").grid(row=3, column=0, sticky="w", padx=6)
        self.in_game_sens_slider = ctk.CTkSlider(
            control_frame, from_=0.1, to=8, number_of_steps=79, command=self.update_in_game_sens
        )
        self.in_game_sens_slider.grid(row=3, column=1, padx=(2,2), sticky="ew")
        self.in_game_sens_value = ctk.CTkLabel(
            control_frame, text=f"{config.in_game_sens:.2f}", text_color="#ff5e69", width=40
        )
        self.in_game_sens_value.grid(row=3, column=2, padx=2)
        self.in_game_sens_slider.set(config.in_game_sens)
        
        # Configure column weights
        control_frame.grid_columnconfigure(1, weight=1)
        
        # Mouse buttons
        ctk.CTkLabel(control_frame, text="Mouse Button:", text_color="#fff").grid(row=4, column=0, sticky="w", padx=6, pady=(8,0))
        self.btn_var = ctk.IntVar(value=config.selected_mouse_button)
        btnrow = ctk.CTkFrame(control_frame, fg_color=BG)
        btnrow.grid(row=4, column=1, pady=(8,0), columnspan=2, sticky="w")
        for i, txt in enumerate(["Left", "Right", "Middle", "Side 4", "Side 5"]):
            ctk.CTkRadioButton(btnrow, text=txt, variable=self.btn_var, value=i, command=self.update_mouse_btn, text_color="#fff", hover_color=NEON).pack(side="left", padx=5)
        
        # --- AIM MODES ---
        mode_frame = ctk.CTkFrame(self, fg_color=BG)
        mode_frame.pack(fill="x", padx=10, pady=(0, 8))
        self.mode_var = ctk.StringVar(value=config.mode)
        
        mode_label = ctk.CTkLabel(mode_frame, text="⚡ Aimbot Mode", text_color="#00e676", font=("Segoe UI", 16, "bold"))
        mode_label.pack(pady=(8, 8), padx=6, anchor="w")
        
        moderow = ctk.CTkFrame(mode_frame, fg_color=BG)
        moderow.pack(pady=(0, 8))
        for name in ["normal", "bezier", "silent", "smooth"]:
            ctk.CTkRadioButton(moderow, text=name.title(), variable=self.mode_var, value=name, command=self.update_mode, text_color="#fff", hover_color=NEON).pack(side="left", padx=12)
        
        self.dynamic_frame = ctk.CTkFrame(self, fg_color=BG)
        self.dynamic_frame.pack(fill="both", expand=False, padx=10, pady=(0, 8))
        
        # --- MODEL SETTINGS ---
        model_frame = ctk.CTkFrame(self, fg_color=BG)
        model_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        model_label = ctk.CTkLabel(model_frame, text="🤖 AI Model", text_color="#00e676", font=("Segoe UI", 16, "bold"))
        model_label.grid(row=0, column=0, columnspan=3, pady=(8, 8), sticky="w", padx=6)
        
        ctk.CTkLabel(model_frame, text="Model File:", text_color="#fff").grid(row=1, column=0, sticky="w", padx=6)
        self.model_menu = ctk.CTkOptionMenu(model_frame, values=self.get_model_list(), command=self.select_model, width=170)
        self.model_menu.grid(row=1, column=1, padx=(0,12))
        neon_button(model_frame, text="Reload Model", command=self.reload_model, width=100).grid(row=1, column=2)
        
        ctk.CTkLabel(model_frame, text="Classes:", text_color="#fff").grid(row=2, column=0, sticky="nw", padx=6, pady=(8,2))
        self.class_listbox = ctk.CTkTextbox(model_frame, height=60, width=240, fg_color="#16161a", text_color="#fff", font=("Segoe UI", 12))
        self.class_listbox.grid(row=2, column=1, columnspan=2, padx=(0,12), pady=(8,2))
        self.class_listbox.configure(state="normal")
        
        # --- CLASS SELECTION ---
        class_frame = ctk.CTkFrame(self, fg_color=BG)
        class_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        class_label = ctk.CTkLabel(class_frame, text="🎯 Target Classes", text_color="#00e676", font=("Segoe UI", 16, "bold"))
        class_label.grid(row=0, column=0, columnspan=2, pady=(8, 8), sticky="w", padx=6)
        
        ctk.CTkLabel(class_frame, text="Select Head Class:", text_color="#fff").grid(row=1, column=0, sticky="w", padx=6)
        self.head_class_var = ctk.StringVar(value=config.custom_head_label or "None")
        self.head_class_menu = ctk.CTkOptionMenu(
            class_frame,
            values=["None"] + self.get_available_classes(),
            variable=self.head_class_var,
            command=self.set_head_class
        )
        self.head_class_menu.grid(row=1, column=1, padx=(2, 12))
        
        ctk.CTkLabel(class_frame, text="Select Player Class:", text_color="#fff").grid(row=2, column=0, sticky="w", padx=6)
        self.player_class_var = ctk.StringVar(value=config.custom_player_label)
        self.player_class_menu = ctk.CTkOptionMenu(
            class_frame,
            values=self.get_available_classes(),
            variable=self.player_class_var,
            command=self.set_player_class
        )
        self.player_class_menu.grid(row=2, column=1, padx=(2, 12))
        
        ctk.CTkLabel(class_frame, text="💡 Tip: For numeric models, try class '0' or '1' for player targets", text_color="#ff5e69", font=("Segoe UI", 11, "italic")).grid(row=3, column=0, columnspan=2, pady=(8,4), padx=6, sticky="w")
        
        # --- PROFILE CONTROLS ---
        profile_frame = ctk.CTkFrame(self, fg_color=BG)
        profile_frame.pack(fill="x", padx=10, pady=(0, 8))
        neon_button(profile_frame, text="Save Profile", command=self.save_profile).pack(side="left", padx=7)
        ctk.CTkButton(profile_frame, text="Load Profile", command=self.load_profile, fg_color="#232323").pack(side="left", padx=7)
        ctk.CTkButton(profile_frame, text="Reset to Defaults", command=self.reset_defaults, fg_color="#232323").pack(side="left", padx=7)
        
        # --- AIMBOT CONTROLS ---
        aimbot_frame = ctk.CTkFrame(self, fg_color=BG)
        aimbot_frame.pack(fill="x", padx=10, pady=(0, 16))
        neon_button(aimbot_frame, text="Start Aimbot", command=self.start_aimbot, width=120, height=40, font=("Segoe UI", 14, "bold")).pack(side="left", padx=9)
        ctk.CTkButton(aimbot_frame, text="Stop Aimbot", command=self.stop_aimbot, fg_color="#232323", width=120, height=40, font=("Segoe UI", 14, "bold")).pack(side="left", padx=9)
        
        # Quick confidence presets
        preset_frame = ctk.CTkFrame(aimbot_frame, fg_color="#1a1a1a")
        preset_frame.pack(side="left", padx=(20, 0))
        ctk.CTkLabel(preset_frame, text="Quick Presets:", text_color="#ccc", font=("Segoe UI", 10)).pack(anchor="w", padx=4, pady=(4,0))
        preset_buttons = ctk.CTkFrame(preset_frame, fg_color="#1a1a1a")
        preset_buttons.pack(padx=4, pady=(0,4))
        
        def set_conf_preset(value):
            config.conf = value
            self.conf_slider.set(value)
            self.conf_value.configure(text=f"{value:.2f}")
        
        ctk.CTkButton(preset_buttons, text="Strict (0.8)", command=lambda: set_conf_preset(0.8), width=70, height=25, font=("Segoe UI", 9)).pack(side="left", padx=1)
        ctk.CTkButton(preset_buttons, text="Normal (0.5)", command=lambda: set_conf_preset(0.5), width=70, height=25, font=("Segoe UI", 9)).pack(side="left", padx=1)
        ctk.CTkButton(preset_buttons, text="Loose (0.2)", command=lambda: set_conf_preset(0.2), width=70, height=25, font=("Segoe UI", 9)).pack(side="left", padx=1)
        
        ctk.CTkLabel(
            self,
            text="Made with ♥ by Ahmo934 for Makcu Community",
            font=("Segoe UI", 13, "bold"),
            text_color=NEON
        ).pack(side="bottom", pady=(0, 5))
        
        self.update_dynamic_frame()
        self.update_idletasks()
        self.after(10, lambda: self._autosize())
        self.input_check_window = None

    def add_speed_section(self, label, min_key, max_key):
        f = ctk.CTkFrame(self.dynamic_frame, fg_color=BG)
        f.pack(fill="x", pady=4)
        ctk.CTkLabel(f, text=f"{label} X Speed:", text_color="#fff").grid(row=0, column=0, sticky="w")
        x_var = ctk.DoubleVar(value=getattr(config, min_key))
        x_slider = ctk.CTkSlider(f, from_=0.1, to=1, number_of_steps=9, variable=x_var)
        x_slider.grid(row=0, column=1)
        x_value_label = ctk.CTkLabel(f, text=f"{x_var.get():.2f}", text_color="#ff5555")
        x_value_label.grid(row=0, column=2, padx=2)
        def update_x(val):
            val = float(val)
            setattr(config, min_key, val)
            x_value_label.configure(text=f"{val:.2f}")
        x_slider.configure(command=update_x)
        ctk.CTkLabel(f, text=f"{label} Y Speed:", text_color="#fff").grid(row=1, column=0, sticky="w")
        y_var = ctk.DoubleVar(value=getattr(config, max_key))
        y_slider = ctk.CTkSlider(f, from_=0.1, to=1, number_of_steps=9, variable=y_var)
        y_slider.grid(row=1, column=1)
        y_value_label = ctk.CTkLabel(f, text=f"{y_var.get():.2f}", text_color="#ff5555")
        y_value_label.grid(row=1, column=2, padx=2)
        def update_y(val):
            val = float(val)
            setattr(config, max_key, val)
            y_value_label.configure(text=f"{val:.2f}")
        y_slider.configure(command=update_y)
        self.humanize_toggle = ctk.CTkCheckBox(
            f,
            text="Aim Humanization",
            variable=self.aim_humanize_var,
            onvalue=True, offvalue=False,
            command=self.toggle_humanize,
            text_color="#fff"
        )
        self.humanize_toggle.grid(row=2, column=0, sticky="w", padx=6, pady=(8, 0))
        self.humanize_slider = ctk.CTkSlider(
            f,
            from_=10, to=50,
            number_of_steps=39,
            command=self.update_humanization
        )
        self.humanize_slider.set(config.aim_humanization)
        self.humanize_slider_label = ctk.CTkLabel(
            f,
            text=f"{config.aim_humanization}",
            text_color="#ff5555"
        )
        self.toggle_humanize()

    def add_bezier_section(self, seg_key, cx_key, cy_key):
        f = ctk.CTkFrame(self.dynamic_frame, fg_color=BG)
        f.pack(fill="x", pady=4)
        ctk.CTkLabel(f, text="Bezier Segments:", text_color="#fff").grid(row=0, column=0)
        sseg = ctk.CTkSlider(f, from_=0, to=20, number_of_steps=20, command=lambda v: setattr(config, seg_key, int(float(v))))
        sseg.set(getattr(config, seg_key))
        sseg.grid(row=0, column=1)
        ctk.CTkLabel(f, text="Ctrl X:", text_color="#fff").grid(row=1, column=0)
        scx = ctk.CTkSlider(f, from_=0, to=60, number_of_steps=60, command=lambda v: setattr(config, cx_key, int(float(v))))
        scx.set(getattr(config, cx_key))
        scx.grid(row=1, column=1)
        ctk.CTkLabel(f, text="Ctrl Y:", text_color="#fff").grid(row=2, column=0)
        scy = ctk.CTkSlider(f, from_=0, to=60, number_of_steps=60, command=lambda v: setattr(config, cy_key, int(float(v))))
        scy.set(getattr(config, cy_key))
        scy.grid(row=2, column=1)

    def add_silent_section(self):
        f = ctk.CTkFrame(self.dynamic_frame, fg_color=BG)
        f.pack(fill="x", pady=4)
        ctk.CTkLabel(f, text="Silent Aim Speed:", text_color="#fff").grid(row=0, column=0)
        sspd = ctk.CTkSlider(f, from_=1, to=6, number_of_steps=5, command=lambda v: setattr(config, "silent_speed", int(float(v))))
        sspd.set(config.silent_speed)
        sspd.grid(row=0, column=1)
        ctk.CTkLabel(f, text="Cooldown:", text_color="#fff").grid(row=1, column=0)
        scd = ctk.CTkSlider(f, from_=0.00, to=0.5, number_of_steps=50, command=lambda v: setattr(config, "silent_cooldown", float(v)))
        scd.set(config.silent_cooldown)
        scd.grid(row=1, column=1)

    def add_smooth_section(self):
        """Add comprehensive smooth aim controls with WindMouse settings."""
        f = ctk.CTkFrame(self.dynamic_frame, fg_color="#0a0a0a")
        f.pack(fill="x", pady=4)
        
        # Title
        title = ctk.CTkLabel(f, text="🌪️ WindMouse Smooth Aim Settings", text_color="#00e676", font=("Segoe UI", 14, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=(8, 12), sticky="w", padx=6)
        
        # Core WindMouse parameters
        ctk.CTkLabel(f, text="Gravity:", text_color="#fff", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w", padx=6)
        gravity_slider = ctk.CTkSlider(f, from_=1, to=20, number_of_steps=19)
        gravity_slider.set(config.smooth_gravity)
        gravity_slider.grid(row=1, column=1, padx=2, sticky="ew")
        gravity_label = ctk.CTkLabel(f, text=f"{config.smooth_gravity:.1f}", text_color="#ff5555", width=40)
        gravity_label.grid(row=1, column=2, padx=2)
        def update_gravity(v):
            config.smooth_gravity = float(v)
            gravity_label.configure(text=f"{float(v):.1f}")
        gravity_slider.configure(command=update_gravity)
        
        ctk.CTkLabel(f, text="Wind:", text_color="#fff", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w", padx=6)
        wind_slider = ctk.CTkSlider(f, from_=1, to=20, number_of_steps=19)
        wind_slider.set(config.smooth_wind)
        wind_slider.grid(row=2, column=1, padx=2, sticky="ew")
        wind_label = ctk.CTkLabel(f, text=f"{config.smooth_wind:.1f}", text_color="#ff5555", width=40)
        wind_label.grid(row=2, column=2, padx=2)
        def update_wind(v):
            config.smooth_wind = float(v)
            wind_label.configure(text=f"{float(v):.1f}")
        wind_slider.configure(command=update_wind)
        
        # Speed settings
        ctk.CTkLabel(f, text="Close Speed:", text_color="#fff", font=("Segoe UI", 11, "bold")).grid(row=3, column=0, sticky="w", padx=6)
        close_speed_slider = ctk.CTkSlider(f, from_=0.1, to=1.0, number_of_steps=18)
        close_speed_slider.set(config.smooth_close_speed)
        close_speed_slider.grid(row=3, column=1, padx=2, sticky="ew")
        close_speed_label = ctk.CTkLabel(f, text=f"{config.smooth_close_speed:.2f}", text_color="#ff5555", width=40)
        close_speed_label.grid(row=3, column=2, padx=2)
        def update_close_speed(v):
            config.smooth_close_speed = float(v)
            close_speed_label.configure(text=f"{float(v):.2f}")
        close_speed_slider.configure(command=update_close_speed)
        
        ctk.CTkLabel(f, text="Far Speed:", text_color="#fff", font=("Segoe UI", 11, "bold")).grid(row=4, column=0, sticky="w", padx=6)
        far_speed_slider = ctk.CTkSlider(f, from_=0.1, to=1.0, number_of_steps=18)
        far_speed_slider.set(config.smooth_far_speed)
        far_speed_slider.grid(row=4, column=1, padx=2, sticky="ew")
        far_speed_label = ctk.CTkLabel(f, text=f"{config.smooth_far_speed:.2f}", text_color="#ff5555", width=40)
        far_speed_label.grid(row=4, column=2, padx=2)
        def update_far_speed(v):
            config.smooth_far_speed = float(v)
            far_speed_label.configure(text=f"{float(v):.2f}")
        far_speed_slider.configure(command=update_far_speed)
        
        # Reaction time
        ctk.CTkLabel(f, text="Reaction Time:", text_color="#fff", font=("Segoe UI", 11, "bold")).grid(row=5, column=0, sticky="w", padx=6)
        reaction_slider = ctk.CTkSlider(f, from_=0.01, to=0.3, number_of_steps=29)
        reaction_slider.set(config.smooth_reaction_max)
        reaction_slider.grid(row=5, column=1, padx=2, sticky="ew")
        reaction_label = ctk.CTkLabel(f, text=f"{config.smooth_reaction_max:.3f}s", text_color="#ff5555", width=40)
        reaction_label.grid(row=5, column=2, padx=2)
        def update_reaction(v):
            config.smooth_reaction_max = float(v)
            config.smooth_reaction_min = float(v) * 0.3  # Min is 30% of max
            reaction_label.configure(text=f"{float(v):.3f}s")
        reaction_slider.configure(command=update_reaction)
        
        # Max step size
        ctk.CTkLabel(f, text="Max Step:", text_color="#fff", font=("Segoe UI", 11, "bold")).grid(row=6, column=0, sticky="w", padx=6)
        step_slider = ctk.CTkSlider(f, from_=5, to=50, number_of_steps=45)
        step_slider.set(config.smooth_max_step)
        step_slider.grid(row=6, column=1, padx=2, sticky="ew")
        step_label = ctk.CTkLabel(f, text=f"{config.smooth_max_step:.0f}px", text_color="#ff5555", width=40)
        step_label.grid(row=6, column=2, padx=2)
        def update_step(v):
            config.smooth_max_step = float(v)
            step_label.configure(text=f"{float(v):.0f}px")
        step_slider.configure(command=update_step)
        
        # Presets
        preset_frame = ctk.CTkFrame(f, fg_color="#1a1a1a")
        preset_frame.grid(row=7, column=0, columnspan=3, pady=(12, 8), padx=6, sticky="ew")
        
        ctk.CTkLabel(preset_frame, text="Quick Presets:", text_color="#ccc", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=4, pady=(4,0))
        
        preset_buttons = ctk.CTkFrame(preset_frame, fg_color="#1a1a1a")
        preset_buttons.pack(padx=4, pady=(0,4))
        
        def apply_preset(preset_type):
            if preset_type == "human":
                # Human-like settings
                config.smooth_gravity = 9.0
                config.smooth_wind = 3.0
                config.smooth_close_speed = 0.3
                config.smooth_far_speed = 0.7
                config.smooth_reaction_max = 0.12
                config.smooth_max_step = 12.0
            elif preset_type == "precise":
                # Very precise, slow settings
                config.smooth_gravity = 15.0
                config.smooth_wind = 1.5
                config.smooth_close_speed = 0.2
                config.smooth_far_speed = 0.5
                config.smooth_reaction_max = 0.08
                config.smooth_max_step = 8.0
            elif preset_type == "aggressive":
                # Faster, more aggressive settings
                config.smooth_gravity = 12.0
                config.smooth_wind = 5.0
                config.smooth_close_speed = 0.5
                config.smooth_far_speed = 0.9
                config.smooth_reaction_max = 0.05
                config.smooth_max_step = 20.0
            
            # Update all sliders
            gravity_slider.set(config.smooth_gravity)
            wind_slider.set(config.smooth_wind)
            close_speed_slider.set(config.smooth_close_speed)
            far_speed_slider.set(config.smooth_far_speed)
            reaction_slider.set(config.smooth_reaction_max)
            step_slider.set(config.smooth_max_step)
            
            # Update labels
            gravity_label.configure(text=f"{config.smooth_gravity:.1f}")
            wind_label.configure(text=f"{config.smooth_wind:.1f}")
            close_speed_label.configure(text=f"{config.smooth_close_speed:.2f}")
            far_speed_label.configure(text=f"{config.smooth_far_speed:.2f}")
            reaction_label.configure(text=f"{config.smooth_reaction_max:.3f}s")
            step_label.configure(text=f"{config.smooth_max_step:.0f}px")
        
        ctk.CTkButton(preset_buttons, text="Human-like", command=lambda: apply_preset("human"), width=80, height=25, font=("Segoe UI", 9)).pack(side="left", padx=2)
        ctk.CTkButton(preset_buttons, text="Precise", command=lambda: apply_preset("precise"), width=80, height=25, font=("Segoe UI", 9)).pack(side="left", padx=2)
        ctk.CTkButton(preset_buttons, text="Aggressive", command=lambda: apply_preset("aggressive"), width=80, height=25, font=("Segoe UI", 9)).pack(side="left", padx=2)
        
        # Tips
        tips_text = "💡 Tips: Higher Gravity = more direct path | Higher Wind = more randomness | Lower speeds = smoother aim"
        ctk.CTkLabel(f, text=tips_text, text_color="#888", font=("Segoe UI", 9, "italic"), wraplength=400).grid(row=8, column=0, columnspan=3, pady=(4, 8), padx=6, sticky="w")
        
        # Configure column weights
        f.grid_columnconfigure(1, weight=1)

    def update_dynamic_frame(self):
        for w in self.dynamic_frame.winfo_children():
            w.destroy()
        mode = config.mode
        if mode == "normal":
            self.add_speed_section("Normal", "normal_x_speed", "normal_y_speed")
        elif mode == "bezier":
            self.add_bezier_section("bezier_segments", "bezier_ctrl_x", "bezier_ctrl_y")
        elif mode == "silent":
            self.add_bezier_section("silent_segments", "silent_ctrl_x", "silent_ctrl_y")
            self.add_silent_section()
        elif mode == "smooth":
            self.add_smooth_section()

    def _autosize(self):
        self.update_idletasks()
        req_width = self.winfo_reqwidth()
        req_height = self.winfo_reqheight()
        self.geometry(f"{req_width}x{req_height}")