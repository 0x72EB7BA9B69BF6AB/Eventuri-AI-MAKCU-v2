import os
import customtkinter as ctk
from tkinter import messagebox
from config import config
from mouse import Mouse,connect_to_makcu, test_move
import main
from main import (
    start_aimbot, stop_aimbot, is_aimbot_running,
    reload_model, get_model_classes, get_model_size
)
import glob
from gui_sections import *
from gui_callbacks import *
from gui_constants import NEON, BG, neon_button

ctk.set_appearance_mode("dark")


class EventuriGUI(ctk.CTk, GUISections, GUICallbacks):
    def __init__(self):
        super().__init__()
        self.title("EVENTURI-AI for MAKCU")
        
        # Get screen dimensions for responsive design
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Set initial size (90% of screen)
        initial_width = int(screen_width * 0.9)
        initial_height = int(screen_height * 0.9)
        
        # Center the window
        x = (screen_width - initial_width) // 2
        y = (screen_height - initial_height) // 2
        
        self.geometry(f"{initial_width}x{initial_height}+{x}+{y}")
        self.configure(bg=BG)
        self.resizable(True, True)  # Allow resizing
        self.minsize(900, 700)  # Set minimum size
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Configure grid weights for responsiveness
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Internal state
        self._makcu_connected = False
        self._last_model = None
        self.error_text = ctk.StringVar(value="")
        self.aimbot_status = ctk.StringVar(value="Stopped")
        self.connection_status = ctk.StringVar(value="Disconnected")
        self.connection_color = ctk.StringVar(value="#b71c1c")
        self.model_name = ctk.StringVar(value=config.model_path)
        self.model_size = ctk.StringVar(value="")
        self.aim_humanize_var = ctk.BooleanVar(value=bool(config.aim_humanization))
        self.debug_checkbox_var = ctk.BooleanVar(value=False)
        self.input_check_var = ctk.BooleanVar(value=False)
        self.button_mask_var = ctk.BooleanVar(value=bool(getattr(config, "button_mask", False)))
        self._building = True
        self.fps_var = ctk.StringVar(value="FPS: 0")
        self._updating_conf = False
        self._updating_imgsz = False
        self.always_on_var = ctk.BooleanVar(value=bool(getattr(config, "always_on_aim", False)))
        self.trigger_enabled_var   = ctk.BooleanVar(value=bool(getattr(config, "trigger_enabled", False)))
        self.trigger_always_on_var = ctk.BooleanVar(value=bool(getattr(config, "trigger_always_on", False)))
        self.trigger_btn_var       = ctk.IntVar(value=int(getattr(config, "trigger_button", 0)))


        # Build UI and initialize
        self.build_responsive_ui()
        self._building = False
        self.refresh_all()
        self.poll_fps()

        # Auto-connect on startup and start polling status
        self.on_connect()
        self.after(500, self._poll_connection_status)

        # Bind resize event
        self.bind("<Configure>", self.on_window_resize)

    def build_responsive_ui(self):
        """Build the responsive UI with proper scaling"""
        
        # Create main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color=BG,
            scrollbar_button_color=NEON,
            scrollbar_button_hover_color="#d50000"
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # --- STATUS BAR (Enhanced) ---
        self.build_status_bar()
        
        # Create two-column layout for larger screens
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        
        # Left column
        self.left_column = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.left_column.grid_columnconfigure(0, weight=1)
        
        # Right column  
        self.right_column = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.right_column.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.right_column.grid_columnconfigure(0, weight=1)
        
        # Build sections in columns
        self.build_left_column()
        self.build_right_column()
        
        # Footer
        self.build_footer()

    def build_status_bar(self):
        """Enhanced status bar with better visual indicators"""
        status_frame = ctk.CTkFrame(self.main_frame, fg_color="#1a1a1a", height=80)
        status_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        status_frame.grid_columnconfigure(1, weight=1)
        status_frame.grid_propagate(False)
        
        # --- Connection status with visual indicator (left) ---
        conn_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        conn_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=0)
        conn_frame.grid_rowconfigure(0, weight=1)
        
        # Connection indicator circle
        self.conn_indicator = ctk.CTkFrame(
            conn_frame, width=10, height=10, corner_radius=5, fg_color="#b71c1c"
        )
        self.conn_indicator.grid(row=0, column=0, padx=(0, 8))
        self.conn_indicator.grid_propagate(False)
        
        conn_text_frame = ctk.CTkFrame(conn_frame, fg_color="transparent")
        conn_text_frame.grid(row=0, column=1)
        ctk.CTkLabel(
            conn_text_frame, 
            text="MAKCU Device", 
            font=("Segoe UI", 12, "bold"),
            text_color="#ccc"
        ).grid(row=0, column=0, sticky="w")
        self.conn_status_lbl = ctk.CTkLabel(
            conn_text_frame,
            textvariable=self.connection_status,
            font=("Segoe UI", 14, "bold"),
            text_color=self.connection_color.get()
        )
        self.conn_status_lbl.grid(row=1, column=0, sticky="w", pady=(0, 27))
        
        # --- Info panel (center/right) ---
        info_frame = ctk.CTkFrame(status_frame, fg_color="#2a2a2a", corner_radius=10)
        info_frame.grid(row=0, column=1, sticky="ew", padx=15, pady=10)
        info_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # --- Aimbot status ---
        aimbot_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        aimbot_frame.grid(row=0, column=0, padx=10, pady=8, sticky="nsew")
        ctk.CTkLabel(aimbot_frame, text="Aimbot", font=("Segoe UI", 11), text_color="#ccc") \
            .grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(aimbot_frame, textvariable=self.aimbot_status, font=("Segoe UI", 13, "bold"), text_color=NEON) \
            .grid(row=1, column=0, sticky="w")
        
        # --- Model info ---
        model_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        model_frame.grid(row=0, column=1, padx=10, pady=8, sticky="nsew")
        ctk.CTkLabel(model_frame, text="AI Model", font=("Segoe UI", 11), text_color="#ccc") \
            .grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(model_frame, textvariable=self.model_name, font=("Segoe UI", 12, "bold"), text_color="#00bcd4") \
            .grid(row=1, column=0, sticky="w")
        ctk.CTkLabel(model_frame, textvariable=self.model_size, font=("Segoe UI", 10), text_color="#888") \
            .grid(row=2, column=0, sticky="w")
        
        # --- FPS ---
        fps_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        fps_frame.grid(row=0, column=2, padx=10, pady=8, sticky="nsew")
        ctk.CTkLabel(fps_frame, text="Performance", font=("Segoe UI", 11), text_color="#ccc") \
            .grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(fps_frame, textvariable=self.fps_var, font=("Segoe UI", 13, "bold"), text_color="#00e676") \
            .grid(row=1, column=0, sticky="w")
        
        # --- Error display (full width below status) ---
        self.error_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        self.error_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15)
        self.error_lbl = ctk.CTkLabel(
            self.error_frame, 
            textvariable=self.error_text, 
            font=("Segoe UI", 11, "bold"),
            text_color=NEON,
            wraplength=800
        )
        self.error_lbl.grid(row=0, column=0, sticky="ew")
        self.error_frame.grid_columnconfigure(0, weight=1)

    def build_left_column(self):
        row = 0
        self.build_device_controls(self.left_column, row); row += 1
        # NEW:
        self.build_capture_controls(self.left_column, row); row += 1
        # Detection, Aim, Mode, Dynamic, etc. follow:
        self.build_detection_settings(self.left_column, row); row += 1
        self.build_aim_settings(self.left_column, row); row += 1
        self.build_aimbot_mode(self.left_column, row); row += 1
        self.dynamic_frame = ctk.CTkFrame(self.left_column, fg_color=BG)
        self.dynamic_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        self.dynamic_frame.grid_columnconfigure(0, weight=1)

    def build_right_column(self):
        """Build right column content"""
        row = 0
        
        # Model Settings
        self.build_model_settings(self.right_column, row)
        row += 1
        
        # Class Selection
        self.build_class_selection(self.right_column, row)
        row += 1

        # Triggerbot section here
        self.build_triggerbot_settings(self.right_column, row); row += 1

        # Profile Controls
        self.build_profile_controls(self.right_column, row)
        row += 1
        
        # Main Controls
        self.build_main_controls(self.right_column, row)

    def build_device_controls(self, parent, row):
        """MAKCU device controls (top section)"""
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="🔌 Device Controls", font=("Segoe UI", 16, "bold"),
                    text_color="#00e676").grid(row=0, column=0, columnspan=3, pady=(15, 10), padx=15, sticky="w")

        self.connect_btn = neon_button(frame, text="Connect to MAKCU", command=self.on_connect, width=150, height=35)
        self.connect_btn.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")

        ctk.CTkButton(frame, text="Test Move", command=test_move, width=100, height=35,
                    fg_color="#333", hover_color="#555").grid(row=1, column=1, padx=10, pady=(0, 15), sticky="w")
        
        self.input_check_checkbox = ctk.CTkCheckBox(
            frame, text="Input Monitor", variable=self.input_check_var,
            command=self.on_input_check_toggle, text_color="#fff"
        )
        self.input_check_checkbox.grid(row=1, column=2, padx=15, pady=(0, 15), sticky="w")

        self.button_mask_switch = ctk.CTkSwitch(
        frame,
        text="Button Masking",
        variable=self.button_mask_var,
        command=self.on_button_mask_toggle,
        text_color="#fff"
    )
        self.button_mask_switch.grid(row=1, column=3, padx=15, pady=(0, 15), sticky="w")
        
        


    def build_capture_controls(self, parent, row):
        """Capture controls (bottom section): capture method + NDI source + toggles"""
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="📷 Capture Controls", font=("Segoe UI", 16, "bold"),
                    text_color="#00e676").grid(row=0, column=0, columnspan=4, pady=(15, 10), padx=15, sticky="w")

        # Capture Method
        ctk.CTkLabel(frame, text="Capture Method:", font=("Segoe UI", 14), text_color="#ffffff")\
            .grid(row=1, column=0, sticky="w", padx=15)
        self.capture_mode_var = ctk.StringVar(value=config.capturer_mode.upper())
        self.capture_mode_menu = ctk.CTkOptionMenu(
            frame, values=["MSS", "NDI"], variable=self.capture_mode_var,
            command=self.on_capture_mode_change, width=110
        )
        self.capture_mode_menu.grid(row=1, column=1, sticky="w", padx=(5, 15), pady=10)

        # --- NDI-only block (shown only when capture mode = NDI) ---
        self.ndi_block = ctk.CTkFrame(frame, fg_color="transparent")
        # we'll grid/place this in _update_ndi_controls_state()
        # internal grid for the block
        self.ndi_block.grid_columnconfigure(1, weight=1)

        # NDI Source dropdown (auto-refreshing)
        ctk.CTkLabel(self.ndi_block, text="NDI Source:", font=("Segoe UI", 14), text_color="#ffffff")\
            .grid(row=0, column=0, sticky="w", padx=15)
        self.ndi_source_var = ctk.StringVar(value=self._initial_ndi_source_value())
        self.ndi_source_menu = ctk.CTkOptionMenu(
            self.ndi_block,
            values=self._ndi_menu_values(),
            variable=self.ndi_source_var,
            command=self.on_ndi_source_change,
            width=260
        )
        self.ndi_source_menu.grid(row=0, column=1, sticky="w", padx=(5, 15), pady=(0, 8))

        # Main PC Resolution (width × height)
        ctk.CTkLabel(self.ndi_block, text="Main PC Resolution:", font=("Segoe UI", 14), text_color="#ffffff")\
            .grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

        res_wrap = ctk.CTkFrame(self.ndi_block, fg_color="transparent")
        res_wrap.grid(row=1, column=1, sticky="w", padx=(5, 15), pady=(0, 10))

        self.main_res_w_entry = ctk.CTkEntry(res_wrap, width=90, justify="center")
        self.main_res_w_entry.pack(side="left")
        self.main_res_w_entry.insert(0, str(getattr(config, "main_pc_width", 1920)))

        ctk.CTkLabel(res_wrap, text=" × ", font=("Segoe UI", 14), text_color="#ffffff")\
            .pack(side="left", padx=6)

        self.main_res_h_entry = ctk.CTkEntry(res_wrap, width=90, justify="center")
        self.main_res_h_entry.pack(side="left")
        self.main_res_h_entry.insert(0, str(getattr(config, "main_pc_height", 1080)))

        def _commit_main_res(event=None):
            try:
                w = int(self.main_res_w_entry.get().strip())
                h = int(self.main_res_h_entry.get().strip())
                w = max(320, min(7680, w))
                h = max(240, min(4320, h))
                config.main_pc_width = w
                config.main_pc_height = h
                self.main_res_w_entry.delete(0, "end"); self.main_res_w_entry.insert(0, str(w))
                self.main_res_h_entry.delete(0, "end"); self.main_res_h_entry.insert(0, str(h))
                if hasattr(config, "save") and callable(config.save):
                    config.save()
            except Exception:
                self.main_res_w_entry.delete(0, "end"); self.main_res_w_entry.insert(0, str(getattr(config, "main_pc_width", 1920)))
                self.main_res_h_entry.delete(0, "end"); self.main_res_h_entry.insert(0, str(getattr(config, "main_pc_height", 1080)))

        self.main_res_w_entry.bind("<Return>", _commit_main_res)
        self.main_res_h_entry.bind("<Return>", _commit_main_res)
        self.main_res_w_entry.bind("<FocusOut>", _commit_main_res)
        self.main_res_h_entry.bind("<FocusOut>", _commit_main_res)

        # Toggles
        self.debug_checkbox = ctk.CTkCheckBox(
            frame, text="Debug Window", variable=self.debug_checkbox_var,
            command=self.on_debug_toggle, text_color="#fff"
        )
        self.debug_checkbox.grid(row=4, column=0, sticky="w", padx=15, pady=(5, 15))

        # Initial enable/disable state
        self._update_ndi_controls_state()

        # Start polling for source list updates
        self.after(1000, self._poll_ndi_sources)

    def _ndi_menu_values(self):
        # Show something friendly when empty
        return config.ndi_sources if config.ndi_sources else ["(no NDI sources found)"]

    def _initial_ndi_source_value(self):
        # If we have a persisted selection and it still exists, use it; else first
        sel = config.ndi_selected_source
        if isinstance(sel, str) and sel in config.ndi_sources:
            return sel
        # fallbacks
        return config.ndi_sources[0] if config.ndi_sources else "(no NDI sources found)"

    def _update_ndi_controls_state(self):
        is_ndi = (self.capture_mode_var.get().upper() == "NDI")

        # Show/hide the whole NDI block
        try:
            if is_ndi:
                self.ndi_block.grid(row=2, column=0, columnspan=2, sticky="ew")
            else:
                self.ndi_block.grid_remove()
        except Exception:
            pass

        # Enable/disable internal controls just in case
        try:
            state = "normal" if is_ndi else "disabled"
            self.ndi_source_menu.configure(state=state)
            self.main_res_w_entry.configure(state=state)
            self.main_res_h_entry.configure(state=state)
        except Exception:
            pass

        try:
            self.debug_checkbox.grid_configure(row=4 if is_ndi else 2)
        except Exception:
            pass

    def _poll_ndi_sources(self):
        latest = list(config.ndi_sources) if isinstance(config.ndi_sources, list) else []

        # 1) Always push the latest values into the menu
        if not latest:
            latest = ["(Start Aimbot to find avalible NDI sources)"]

        try:
            self.ndi_source_menu.configure(values=latest)
        except Exception:
            # widget not ready yet, try again next tick
            self.after(1000, self._poll_ndi_sources)
            return

        # 2) Keep the selection sensible
        current = self.ndi_source_var.get()
        if current not in latest:
            # Prefer persisted selection if still present
            if isinstance(config.ndi_selected_source, str) and config.ndi_selected_source in latest:
                choice = config.ndi_selected_source
            else:
                choice = latest[0]

            # Update both the variable and the widget
            self.ndi_source_var.set(choice)
            try:
                self.ndi_source_menu.set(choice)
            except Exception:
                pass

            if self.capture_mode_var.get().upper() == "NDI" and not choice.startswith("("):
                config.ndi_selected_source = choice
                config.save()

        self._update_ndi_controls_state()

        # tick again
        self.after(1000, self._poll_ndi_sources)
    
    
    def build_triggerbot_settings(self, parent, row):
        """Standalone Triggerbot section (right column)."""
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="🧨 Triggerbot", font=("Segoe UI", 16, "bold"),
                    text_color="#00e676").grid(row=0, column=0, columnspan=2,
                                                pady=(15, 10), padx=15, sticky="w")

        # --- toggles
        toggles = ctk.CTkFrame(frame, fg_color="transparent")
        toggles.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 10))
        toggles.grid_columnconfigure(1, weight=1)

        def _on_enabled_then_focus():
            self.on_trigger_enabled_toggle()
            if self.trigger_enabled_var.get():
                try:
                    self.tb_radius_entry.focus_set()
                    self.tb_radius_entry.select_range(0, "end")
                except Exception:
                    pass

        ctk.CTkSwitch(toggles, text="Enabled", text_color="#fff",
                    variable=self.trigger_enabled_var,
                    command=_on_enabled_then_focus).pack(side="left", padx=(0, 15))

        ctk.CTkSwitch(toggles, text="Always on", text_color="#fff",
                    variable=self.trigger_always_on_var,
                    command=self.on_trigger_always_on_toggle).pack(side="left")

        # --- hotkey row
        ctk.CTkLabel(frame, text="Trigger Key:", font=("Segoe UI", 12, "bold"),
                    text_color="#fff").grid(row=2, column=0, sticky="w", padx=15, pady=(0, 8))
        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.grid(row=2, column=1, sticky="w", padx=15, pady=(0, 8))
        for i, txt in enumerate(["Left", "Right", "Middle", "Side 4", "Side 5"]):
            ctk.CTkRadioButton(btns, text=txt, variable=self.trigger_btn_var, value=i,
                            command=self.update_trigger_button, text_color="#fff").pack(side="left", padx=8)

        # --- params
        params = ctk.CTkFrame(frame, fg_color="#2a2a2a", corner_radius=10)
        params.grid(row=3, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 15))
        params.grid_columnconfigure((1,3,5,7), weight=1)

        # validators
        v_int   = self.register(lambda s: (s == "") or s.isdigit())
        def _is_float(s):
            if s == "" or s == ".": return True
            try: float(s); return True
            except: return False
        v_float = self.register(_is_float)

        def _entry(parent, value, width=80, vcmd=None):
            e = ctk.CTkEntry(parent, width=width, justify="center",
                            font=("Segoe UI", 12, "bold"), text_color=NEON)
            e.insert(0, value)
            if vcmd is not None:
                # validate on keypress
                e.configure(validate="key", validatecommand=(vcmd, "%P"))
            return e

        ctk.CTkLabel(params, text="Radius(px)", font=("Segoe UI", 12, "bold"),
                    text_color="#fff").grid(row=0, column=0, padx=(10,6), pady=10, sticky="w")
        self.tb_radius_entry = _entry(params, str(getattr(config, "trigger_radius_px", 8)),
                                    vcmd=v_int);  self.tb_radius_entry.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(params, text="Delay(ms)", font=("Segoe UI", 12, "bold"),
                    text_color="#fff").grid(row=0, column=2, padx=(16,6), pady=10, sticky="w")
        self.tb_delay_entry  = _entry(params, str(getattr(config, "trigger_delay_ms", 30)),
                                    vcmd=v_int);  self.tb_delay_entry.grid(row=0, column=3, sticky="w")

        ctk.CTkLabel(params, text="Cooldown(ms)", font=("Segoe UI", 12, "bold"),
                    text_color="#fff").grid(row=0, column=4, padx=(16,6), pady=10, sticky="w")
        self.tb_cd_entry     = _entry(params, str(getattr(config, "trigger_cooldown_ms", 120)),
                                    vcmd=v_int); self.tb_cd_entry.grid(row=0, column=5, sticky="w")

        ctk.CTkLabel(params, text="Min conf", font=("Segoe UI", 12, "bold"),
                    text_color="#fff").grid(row=0, column=6, padx=(16,6), pady=10, sticky="w")
        self.tb_conf_entry   = _entry(params, f"{getattr(config, 'trigger_min_conf', 0.35):.2f}",
                                    vcmd=v_float); self.tb_conf_entry.grid(row=0, column=7, sticky="w")

        def _commit_tb_numbers(event=None):
            try:
                # ints
                r  = int(self.tb_radius_entry.get() or 0)
                d  = int(self.tb_delay_entry.get() or 0)
                cd = int(self.tb_cd_entry.get() or 0)
                # float
                cf = float(self.tb_conf_entry.get() or 0.0)

                # basic bounds
                r  = max(1, min(200, r))
                d  = max(0, min(1000, d))
                cd = max(0, min(2000, cd))
                cf = max(0.0, min(1.0, cf))

                config.trigger_radius_px   = r
                config.trigger_delay_ms    = d
                config.trigger_cooldown_ms = cd
                config.trigger_min_conf    = cf

                # normalize UI
                self.tb_radius_entry.delete(0, "end"); self.tb_radius_entry.insert(0, str(r))
                self.tb_delay_entry.delete(0, "end");  self.tb_delay_entry.insert(0, str(d))
                self.tb_cd_entry.delete(0, "end");     self.tb_cd_entry.insert(0, str(cd))
                self.tb_conf_entry.delete(0, "end");   self.tb_conf_entry.insert(0, f"{cf:.2f}")

                if hasattr(config, "save") and callable(config.save):
                    config.save()
            except Exception as e:
                print(f"[WARN] Bad triggerbot param: {e}")
                # revert to config
                self.tb_radius_entry.delete(0,"end"); self.tb_radius_entry.insert(0, str(getattr(config, "trigger_radius_px", 8)))
                self.tb_delay_entry.delete(0,"end");  self.tb_delay_entry.insert(0, str(getattr(config, "trigger_delay_ms", 30)))
                self.tb_cd_entry.delete(0,"end");     self.tb_cd_entry.insert(0, str(getattr(config, "trigger_cooldown_ms", 120)))
                self.tb_conf_entry.delete(0,"end");   self.tb_conf_entry.insert(0, f"{getattr(config, 'trigger_min_conf', 0.35):.2f}")

        for w in (self.tb_radius_entry, self.tb_delay_entry, self.tb_cd_entry, self.tb_conf_entry):
            w.bind("<Return>", _commit_tb_numbers)
            w.bind("<FocusOut>", _commit_tb_numbers)

        self._update_trigger_widgets_state()

    def build_detection_settings(self, parent, row):
        """Enhanced detection settings with better layout"""
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(frame, text="🎯 Detection Settings", font=("Segoe UI", 16, "bold"), text_color="#00e676").grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        # Settings grid
        settings_frame = ctk.CTkFrame(frame, fg_color="transparent")
        settings_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Confidence (row 0)
        ctk.CTkLabel(settings_frame, text="Confidence", font=("Segoe UI", 12, "bold"), text_color="#fff")\
            .grid(row=0, column=0, sticky="w", pady=5)

        self.conf_slider = ctk.CTkSlider(
            settings_frame, from_=0.05, to=0.95, number_of_steps=18, command=self.update_conf
        )
        self.conf_slider.grid(row=0, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.conf_slider.set(config.conf)

        # Manual entry (replaces the old value label)
        self.conf_entry = ctk.CTkEntry(
            settings_frame, width=70, justify="center",
            font=("Segoe UI", 12, "bold"), text_color=NEON
        )
        self.conf_entry.grid(row=0, column=2, pady=5)
        self.conf_entry.insert(0, f"{config.conf:.2f}")

        self.conf_entry.bind("<Return>", self.on_conf_entry_commit)
        self.conf_entry.bind("<FocusOut>", self.on_conf_entry_commit)
        
        # Resolution (row 1)
        ctk.CTkLabel(settings_frame, text="Model Image Size", font=("Segoe UI", 12, "bold"), text_color="#fff")\
            .grid(row=1, column=0, sticky="w", pady=5)

        self.imgsz_slider = ctk.CTkSlider(
            settings_frame, from_=128, to=1280, number_of_steps=18, command=self.update_imgsz
        )
        self.imgsz_slider.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.imgsz_slider.set(config.imgsz)

        # Manual entry (replaces the value label)
        self.imgsz_entry = ctk.CTkEntry(
            settings_frame, width=70, justify="center",
            font=("Segoe UI", 12, "bold"), text_color=NEON
        )
        self.imgsz_entry.grid(row=1, column=2, pady=5)
        self.imgsz_entry.insert(0, str(config.imgsz))

        # Commit on Enter or focus-out
        self.imgsz_entry.bind("<Return>", self.on_imgsz_entry_commit)
        self.imgsz_entry.bind("<FocusOut>", self.on_imgsz_entry_commit)
        
        # Max Detections
        ctk.CTkLabel(settings_frame, text="Max Detections", font=("Segoe UI", 12, "bold"), text_color="#fff").grid(row=2, column=0, sticky="w", pady=5)
        self.max_detect_slider = ctk.CTkSlider(settings_frame, from_=1, to=100, number_of_steps=99, command=self.update_max_detect)
        self.max_detect_slider.grid(row=2, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.max_detect_label = ctk.CTkLabel(settings_frame, text=str(config.max_detect), font=("Segoe UI", 12, "bold"), text_color=NEON, width=50)
        self.max_detect_label.grid(row=2, column=2, pady=5)
        
        # Quick presets
        preset_frame = ctk.CTkFrame(settings_frame, fg_color="#2a2a2a", corner_radius=8)
        preset_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        ctk.CTkLabel(preset_frame, text="Quick Presets:", font=("Segoe UI", 10, "bold"), text_color="#ccc").pack(pady=(8, 5))
        
        preset_buttons = ctk.CTkFrame(preset_frame, fg_color="transparent")
        preset_buttons.pack(pady=(0, 8))
        
        def set_conf_preset(value):
                value = round(float(value), 2)
                config.conf = value
                self.conf_slider.set(value)
                self._set_entry_text(self.conf_entry, f"{value:.2f}")
        
        ctk.CTkButton(preset_buttons, text="Strict (0.8)", command=lambda: set_conf_preset(0.8), width=80, height=25).pack(side="left", padx=2)
        ctk.CTkButton(preset_buttons, text="Normal (0.5)", command=lambda: set_conf_preset(0.5), width=80, height=25).pack(side="left", padx=2)
        ctk.CTkButton(preset_buttons, text="Loose (0.2)", command=lambda: set_conf_preset(0.2), width=80, height=25).pack(side="left", padx=2)

    def build_aim_settings(self, parent, row):
        """Aim configuration settings"""
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(frame, text="🎮 Aim Settings", font=("Segoe UI", 16, "bold"), text_color="#00e676").grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        settings_frame = ctk.CTkFrame(frame, fg_color="transparent")
        settings_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        settings_frame.grid_columnconfigure(1, weight=1)

        # Aim always on (toggle under Smoothing)
        self.always_on_switch = ctk.CTkSwitch(
            settings_frame,
            text="Aim always on",
            variable=self.always_on_var,
            command=self.on_always_on_toggle,
            text_color="#fff"
        )
        self.always_on_switch.grid(row=0, column=0, columnspan=3, sticky="w", pady=(8, 5))
        
        # FOV Size
        ctk.CTkLabel(settings_frame, text="FOV Size", font=("Segoe UI", 12, "bold"), text_color="#fff")\
            .grid(row=1, column=0, sticky="w", pady=5)

        self.fov_slider = ctk.CTkSlider(
            settings_frame, from_=20, to=500, command=self.update_fov, number_of_steps=180
        )
        self.fov_slider.grid(row=1, column=1, sticky="ew", padx=(10, 5), pady=5)

        # Manual entry box (replaces the label)
        self.fov_entry = ctk.CTkEntry(
            settings_frame, width=70, justify="center",
            font=("Segoe UI", 12, "bold"), text_color=NEON
        )
        self.fov_entry.grid(row=1, column=2, pady=5)
        self.fov_entry.insert(0, str(config.region_size))

        # Commit on Enter or focus-out
        self.fov_entry.bind("<Return>", self.on_fov_entry_commit)
        self.fov_entry.bind("<FocusOut>", self.on_fov_entry_commit)

        # guard to avoid feedback loops
        self._updating_fov = False

        # Player Y Offset
        ctk.CTkLabel(settings_frame, text="Y Offset", font=("Segoe UI", 12, "bold"), text_color="#fff").grid(row=2, column=0, sticky="w", pady=5)
        self.offset_slider = ctk.CTkSlider(settings_frame, from_=0, to=20, command=self.update_offset, number_of_steps=20)
        self.offset_slider.grid(row=2, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.offset_value = ctk.CTkLabel(settings_frame, text=str(config.player_y_offset), font=("Segoe UI", 12, "bold"), text_color=NEON, width=50)
        self.offset_value.grid(row=2, column=2, pady=5)
        
        # Sensitivity
        ctk.CTkLabel(settings_frame, text="Smoothing", font=("Segoe UI", 12, "bold"), text_color="#fff").grid(row=3, column=0, sticky="w", pady=5)
        self.in_game_sens_slider = ctk.CTkSlider(settings_frame, from_=0.1, to=20, number_of_steps=199, command=self.update_in_game_sens)
        self.in_game_sens_slider.grid(row=3, column=1, sticky="ew", padx=(10, 5), pady=5)
        self.in_game_sens_value = ctk.CTkLabel(settings_frame, text=f"{config.in_game_sens:.2f}", font=("Segoe UI", 12, "bold"), text_color=NEON, width=50)
        self.in_game_sens_value.grid(row=3, column=2, pady=5)

        
        # Mouse Button Selection
        ctk.CTkLabel(settings_frame, text="Aim Key:", font=("Segoe UI", 12, "bold"), text_color="#fff").grid(row=4, column=0, sticky="nw", pady=(10, 5))
        
        self.btn_var = ctk.IntVar(value=config.selected_mouse_button)
        btn_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=1, columnspan=2, sticky="ew", pady=(10, 5))
        
        for i, txt in enumerate(["Left", "Right", "Middle", "Side 4", "Side 5"]):
            ctk.CTkRadioButton(btn_frame, text=txt, variable=self.btn_var, value=i, command=self.update_mouse_btn, text_color="#fff").pack(side="left", padx=8)

    def build_aimbot_mode(self, parent, row):
        """Aimbot mode selection"""
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(frame, text="⚡ Aimbot Mode", font=("Segoe UI", 16, "bold"), text_color="#00e676").grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        self.mode_var = ctk.StringVar(value=config.mode)
        mode_frame = ctk.CTkFrame(frame, fg_color="transparent")
        mode_frame.grid(row=1, column=0, padx=15, pady=(0, 15))
        
        for name in ["normal", "bezier", "silent", "smooth"]:
            ctk.CTkRadioButton(
                mode_frame, 
                text=name.title(), 
                variable=self.mode_var, 
                value=name, 
                command=self.update_mode, 
                text_color="#fff",
                font=("Segoe UI", 12, "bold")
            ).pack(side="left", padx=15)

    def build_model_settings(self, parent, row):
        """AI Model configuration"""
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(frame, text="🤖 AI Model", font=("Segoe UI", 16, "bold"), text_color="#00e676").grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        model_controls = ctk.CTkFrame(frame, fg_color="transparent")
        model_controls.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        model_controls.grid_columnconfigure(0, weight=1)
        
        self.model_menu = ctk.CTkOptionMenu(model_controls, values=self.get_model_list(), command=self.select_model)
        self.model_menu.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        neon_button(model_controls, text="Reload", command=self.reload_model, width=80).grid(row=0, column=1)
        
        # Class display
        ctk.CTkLabel(frame, text="Available Classes:", font=("Segoe UI", 12, "bold"), text_color="#fff").grid(row=2, column=0, sticky="w", padx=15, pady=(10, 5))
        
        self.class_listbox = ctk.CTkTextbox(frame, height=80, fg_color="#2a2a2a", text_color="#fff", font=("Segoe UI", 11))
        self.class_listbox.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))

    def build_class_selection(self, parent, row):
        """Target class selection"""
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(frame, text="🎯 Target Classes", font=("Segoe UI", 16, "bold"), text_color="#00e676").grid(row=0, column=0, columnspan=2, pady=(15, 10), padx=15, sticky="w")
        
        ctk.CTkLabel(frame, text="Player Class:", font=("Segoe UI", 12, "bold"), text_color="#fff").grid(row=1, column=0, sticky="w", padx=15, pady=5)
        self.player_class_var = ctk.StringVar(value=config.custom_player_label)
        self.player_class_menu = ctk.CTkOptionMenu(frame, values=self.get_available_classes(), variable=self.player_class_var, command=self.set_player_class)
        self.player_class_menu.grid(row=1, column=1, sticky="ew", padx=15, pady=5)
        
        ctk.CTkLabel(frame, text="Head Class:", font=("Segoe UI", 12, "bold"), text_color="#fff").grid(row=2, column=0, sticky="w", padx=15, pady=5)
        self.head_class_var = ctk.StringVar(value=config.custom_head_label or "None")
        self.head_class_menu = ctk.CTkOptionMenu(frame, values=["None"] + self.get_available_classes(), variable=self.head_class_var, command=self.set_head_class)
        self.head_class_menu.grid(row=2, column=1, sticky="ew", padx=15, pady=(5, 15))

    def build_profile_controls(self, parent, row):
        """Profile management"""
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(frame, text="💾 Profile Management", font=("Segoe UI", 16, "bold"), text_color="#00e676").grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=15, pady=(0, 15))
        
        neon_button(btn_frame, text="Save Profile", command=self.save_profile, width=100).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Load Profile", command=self.load_profile, width=100, fg_color="#333").pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="Reset Defaults", command=self.reset_defaults, width=100, fg_color="#333").pack(side="left")

    def build_main_controls(self, parent, row):
        """Main aimbot controls"""
        frame = ctk.CTkFrame(parent, fg_color="#1a1a1a")
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(frame, text="🚀 Aimbot Controls", font=("Segoe UI", 16, "bold"), text_color="#00e676").grid(row=0, column=0, pady=(15, 10), padx=15, sticky="w")
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=15, pady=(0, 15))
        
        neon_button(btn_frame, text="🎯 START AIMBOT", command=self.start_aimbot, width=150, height=45, font=("Segoe UI", 14, "bold")).pack(side="left", padx=(0, 15))
        ctk.CTkButton(btn_frame, text="⏹ STOP", command=self.stop_aimbot, width=100, height=45, fg_color="#333", font=("Segoe UI", 14, "bold")).pack(side="left")

    def build_footer(self):
        """Footer with credits"""
        footer = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=40)
        footer.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        footer.grid_propagate(False)
        
        ctk.CTkLabel(
            footer,
            text="Made with ♥ by Ahmo934 and Jealousyhaha for Makcu Community",
            font=("Segoe UI", 12, "bold"),
            text_color=NEON
        ).pack(expand=True)

    def on_window_resize(self, event):
        """Handle window resize events for responsive layout"""
        if event.widget == self:
            width = self.winfo_width()
            
            # Switch to single column layout on smaller screens
            if width < 1200:
                self.switch_to_single_column()
            else:
                self.switch_to_two_column()

    def switch_to_single_column(self):
        """Switch to single column layout for smaller screens"""
        if hasattr(self, '_is_single_column') and self._is_single_column:
            return
            
        self._is_single_column = True
        
        # Reconfigure content frame
        self.content_frame.grid_columnconfigure(1, weight=0)
        
        # Move right column content to left column
        for widget in self.right_column.winfo_children():
            widget.grid_forget()
        
        self.right_column.grid_forget()
        self.left_column.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=0)

    def switch_to_two_column(self):
        """Switch to two column layout for larger screens"""
        if hasattr(self, '_is_single_column') and not self._is_single_column:
            return
            
        self._is_single_column = False
        
        # Reconfigure content frame
        self.content_frame.grid_columnconfigure(1, weight=1)
        
        # Restore two column layout
        self.left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.right_column.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Rebuild right column if needed
        if not self.right_column.winfo_children():
            self.build_right_column()

    def on_connect(self):
        """Enhanced connection with visual feedback"""
        Mouse.cleanup()  # Ensure mouse is clean before connecting
        if connect_to_makcu():
            config.makcu_connected = True
            config.makcu_status_msg = "Connected"
            self.connection_status.set("Connected")
            self.connection_color.set("#00FF00")
            self.conn_indicator.configure(fg_color="#00FF00")
            self.error_text.set("✅ MAKCU device connected successfully!")
        else:
            config.makcu_connected = False
            config.makcu_status_msg = "Connection Failed"
            self.connection_status.set("Disconnected")
            self.connection_color.set("#b71c1c")
            self.conn_indicator.configure(fg_color="#b71c1c")
            self.error_text.set("❌ Failed to connect to MAKCU device")
        
        self.conn_status_lbl.configure(text_color=self.connection_color.get())

    def _poll_connection_status(self):
        """Enhanced status polling with visual updates"""
        if config.makcu_connected:
            self.connection_status.set("Connected")
            self.connection_color.set("#00FF00")
            self.conn_indicator.configure(fg_color="#00FF00")
        else:
            self.connection_status.set("Disconnected")
            self.connection_color.set("#b71c1c")
            self.conn_indicator.configure(fg_color="#b71c1c")
        
        self.conn_status_lbl.configure(text_color=self.connection_color.get())
        self.after(500, self._poll_connection_status)

    # Include all the callback methods from gui_callbacks.py
    def refresh_all(self):
        self.fov_slider.set(config.region_size)
        # update entry text safely
        self._set_entry_text(self.fov_entry, str(config.region_size))
        self.offset_slider.set(config.player_y_offset)
        self.offset_value.configure(text=str(config.player_y_offset))
        self.btn_var.set(config.selected_mouse_button)
        self.mode_var.set(config.mode)
        self.model_name.set(os.path.basename(config.model_path))
        self.model_menu.set(os.path.basename(config.model_path))
        self.model_size.set(get_model_size(config.model_path))
        self.aimbot_status.set("Running" if is_aimbot_running() else "Stopped")
        self.conf_slider.set(config.conf)
        self._set_entry_text(self.conf_entry, f"{config.conf:.2f}")
        self.in_game_sens_slider.set(config.in_game_sens)
        self.in_game_sens_value.configure(text=f"{config.in_game_sens:.2f}")
        self.always_on_var.set(bool(getattr(config, "always_on_aim", False)))
        self.imgsz_slider.set(config.imgsz)
        self._set_entry_text(self.imgsz_entry, str(config.imgsz))
        self.max_detect_slider.set(config.max_detect)
        self.max_detect_label.configure(text=str(config.max_detect))
        self.load_class_list()
        self.update_dynamic_frame()
        self.debug_checkbox_var.set(config.show_debug_window)
        self.input_check_var.set(False)
        self.button_mask_var.set(bool(getattr(config, "button_mask", False)))
        self.capture_mode_var.set(config.capturer_mode.upper())
        self.capture_mode_menu.set(config.capturer_mode.upper())
        self.trigger_enabled_var.set(bool(getattr(config, "trigger_enabled", False)))
        self.trigger_always_on_var.set(bool(getattr(config, "trigger_always_on", False)))
        self.trigger_btn_var.set(int(getattr(config, "trigger_button", 0)))

        try:
            self.tb_radius_entry.delete(0,"end"); self.tb_radius_entry.insert(0, str(config.trigger_radius_px))
            self.tb_delay_entry.delete(0,"end");  self.tb_delay_entry.insert(0, str(config.trigger_delay_ms))
            self.tb_cd_entry.delete(0,"end");     self.tb_cd_entry.insert(0, str(config.trigger_cooldown_ms))
            self.tb_conf_entry.delete(0,"end");   self.tb_conf_entry.insert(0, f"{config.trigger_min_conf:.2f}")
            self._update_trigger_widgets_state()
        except Exception:
            pass  

        # NDI source menu initial state
        try:
            self.ndi_source_menu.configure(values=self._ndi_menu_values())
            if isinstance(config.ndi_selected_source, str) and \
            config.ndi_selected_source in self._ndi_menu_values():
                self.ndi_source_var.set(config.ndi_selected_source)
            elif self._ndi_menu_values():
                self.ndi_source_var.set(self._ndi_menu_values()[0])
        except Exception:
            pass

        self._update_ndi_controls_state()

        # Main PC resolution entries
        try:
            self.main_res_w_entry.delete(0, "end"); self.main_res_w_entry.insert(0, str(config.main_pc_width))
            self.main_res_h_entry.delete(0, "end"); self.main_res_h_entry.insert(0, str(config.main_pc_height))
        except Exception:
            pass


    def on_capture_mode_change(self, value: str):
        m = {"MSS": "mss", "NDI": "ndi"}
        internal = m.get((value or "").upper(), "mss")
        if config.capturer_mode != internal:
            config.capturer_mode = internal
            self.error_text.set(f"🔁 Capture method set to: {value}")
            self._update_ndi_controls_state()  # <-- ensure UI updates immediately
            if is_aimbot_running():
                stop_aimbot(); start_aimbot()
            config.save()
        else:
            # still refresh UI if same value selected
            self._update_ndi_controls_state()

    def on_ndi_source_change(self, value: str):
        if self.capture_mode_var.get().upper() != "NDI":
            return
        if value and not value.startswith("("):
            config.ndi_selected_source = value
            self.ndi_source_var.set(value)
            try:
                self.ndi_source_menu.set(value)
            except Exception:
                pass
            self.error_text.set(f"🔁 NDI source: {value}")
            config.save()

    def update_fov(self, val):
        """Called by the slider."""
        if self._updating_fov:
            return
        self._apply_fov(int(round(val)), source="slider")

    def on_fov_entry_commit(self, event=None):
        """Called when user presses Enter or leaves the entry."""
        try:
            val = int(self.fov_entry.get().strip())
        except Exception:
            # revert to current config if invalid
            self._set_entry_text(self.fov_entry, str(config.region_size))
            return
        self._apply_fov(val, source="entry")

    def _apply_fov(self, value, source="code"):
        MIN_FOV, MAX_FOV = 20, 500
        value = max(MIN_FOV, min(MAX_FOV, int(value)))

        # prevent recursion loops
        self._updating_fov = True
        try:
            config.region_size = value
            # keep slider and entry in sync
            if source != "slider":
                self.fov_slider.set(value)
            if source != "entry":
                self._set_entry_text(self.fov_entry, str(value))
        finally:
            self._updating_fov = False

    def on_trigger_enabled_toggle(self):
        config.trigger_enabled = bool(self.trigger_enabled_var.get())
        self._update_trigger_widgets_state()
        try:
            if hasattr(config, "save") and callable(config.save):
                config.save()
        except Exception as e:
            print(f"[WARN] Failed to save trigger_enabled: {e}")

    def on_trigger_always_on_toggle(self):
        config.trigger_always_on = bool(self.trigger_always_on_var.get())
        try:
            if hasattr(config, "save") and callable(config.save):
                config.save()
        except Exception as e:
            print(f"[WARN] Failed to save trigger_always_on: {e}")

    def update_trigger_button(self):
        config.trigger_button = int(self.trigger_btn_var.get())
        try:
            if hasattr(config, "save") and callable(config.save):
                config.save()
        except Exception as e:
            print(f"[WARN] Failed to save trigger_button: {e}")

    def _update_trigger_widgets_state(self):
        state = "normal" if self.trigger_enabled_var.get() else "disabled"
        try:
            self.tb_radius_entry.configure(state=state)
            self.tb_delay_entry.configure(state=state)
            self.tb_cd_entry.configure(state=state)
            self.tb_conf_entry.configure(state=state)
        except Exception:
            pass

    def update_offset(self, val):
        config.player_y_offset = int(round(val))
        self.offset_value.configure(text=str(config.player_y_offset))

    def update_mouse_btn(self):
        config.selected_mouse_button = self.btn_var.get()

    def update_mode(self):
        config.mode = self.mode_var.get()
        self.update_dynamic_frame()

    def update_conf(self, val):
        """Called by the slider."""
        if getattr(self, "_updating_conf", False):
            return
        self._apply_conf(float(val), source="slider")

    def on_conf_entry_commit(self, event=None):
        """Called when user presses Enter or leaves the entry."""
        raw = self.conf_entry.get().strip()
        # allow ".3" style
        if raw.startswith("."):
            raw = "0" + raw
        try:
            val = float(raw)
        except Exception:
            # revert to current config if invalid
            self._set_entry_text(self.conf_entry, f"{config.conf:.2f}")
            return
        self._apply_conf(val, source="entry")

    def _apply_conf(self, value, source="code"):
        MIN_C, MAX_C = 0.05, 0.95
        # clamp and round to 2 decimals
        value = max(MIN_C, min(MAX_C, float(value)))
        value = round(value, 2)

        self._updating_conf = True
        try:
            config.conf = value
            # keep slider and entry in sync
            if source != "slider":
                self.conf_slider.set(value)
            if source != "entry":
                self._set_entry_text(self.conf_entry, f"{value:.2f}")
        finally:
            self._updating_conf = False

    def _set_entry_text(self, entry, text):
        entry.delete(0, "end")
        entry.insert(0, text)


    def update_imgsz(self, val):
        """Called by the slider."""
        if self._updating_imgsz:
            return
        self._apply_imgsz(int(round(float(val))), source="slider")

    def on_imgsz_entry_commit(self, event=None):
        """Called when user presses Enter or leaves the entry."""
        raw = self.imgsz_entry.get().strip()
        try:
            val = int(raw)
        except Exception:
            # revert to current config if invalid
            self._set_entry_text(self.imgsz_entry, str(config.imgsz))
            return
        self._apply_imgsz(val, source="entry")

    def _snap_to_multiple(self, value, base=32):
        """Snap to nearest multiple of 'base' (YOLO-friendly)."""
        if base <= 1:
            return value
        down = (value // base) * base
        up = down + base
        # choose nearest; prefer 'up' on ties
        return up if (value - down) >= (up - value) else down

    def _apply_imgsz(self, value, source="code"):
        MIN_S, MAX_S = 320, 1280
        value = max(MIN_S, min(MAX_S, int(value)))
        value = self._snap_to_multiple(value, base=32)

        self._updating_imgsz = True
        try:
            config.imgsz = value
            # keep slider and entry in sync
            if source != "slider":
                self.imgsz_slider.set(value)
            if source != "entry":
                self._set_entry_text(self.imgsz_entry, str(value))
        finally:
            self._updating_imgsz = False

    def update_max_detect(self, val):
        val = int(round(float(val)))
        config.max_detect = val
        self.max_detect_label.configure(text=str(val))

    def on_always_on_toggle(self):
        value = bool(self.always_on_var.get())
        config.always_on_aim = value
        try:
            if hasattr(config, "save") and callable(config.save):
                config.save()
        except Exception as e:
            print(f"[WARN] Failed to save config.always_on_aim: {e}")

    def update_in_game_sens(self, val):
        config.in_game_sens = round(float(val), 2)
        self.in_game_sens_value.configure(text=f"{config.in_game_sens:.2f}")

    def poll_fps(self):
        self.fps_var.set(f"FPS: {main.fps:.1f}")
        self.aimbot_status.set("Running" if is_aimbot_running() else "Stopped")
        self.after(200, self.poll_fps)

    def get_model_list(self):
        model_files = []
        for ext in ("pt", "onnx", "engine"):
            model_files.extend(glob.glob(f"models/*.{ext}"))
        return [os.path.basename(p) for p in model_files]

    def select_model(self, val):
        path = os.path.join("models", val)
        if os.path.isfile(path):
            config.model_path = path
            self.model_name.set(os.path.basename(path))
            self.model_size.set(get_model_size(path))
            try:
                reload_model(path)
                self.load_class_list()
                self.error_text.set(f"✅ Model '{val}' loaded successfully")
            except Exception as e:
                self.error_text.set(f"❌ Failed to load model: {e}")
        else:
            self.error_text.set(f"❌ Model file not found: {path}")

    def reload_model(self):
        try:
            reload_model(config.model_path)
            self.load_class_list()
            self.error_text.set("✅ Model reloaded successfully")
        except Exception as e:
            self.error_text.set(f"❌ Failed to reload model: {e}")

    def load_class_list(self):
        try:
            classes = get_model_classes(config.model_path)
            self.available_classes = classes
            self.class_listbox.delete("0.0", "end")
            
            for i, c in enumerate(classes):
                display_text = f"Class {i}: {c}\n"
                self.class_listbox.insert("end", display_text)
            
            class_options = [str(c) for c in classes]
            self.head_class_menu.configure(values=["None"] + class_options)
            self.player_class_menu.configure(values=class_options)
            
            current_head = config.custom_head_label
            current_player = config.custom_player_label
            
            self.head_class_var.set(str(current_head) if current_head is not None else "None")
            self.player_class_var.set(str(current_player) if current_player is not None else "0")
            
        except Exception as e:
            self.error_text.set(f"❌ Failed to load classes: {e}")

    def get_available_classes(self):
        classes = getattr(self, "available_classes", ["0", "1"])
        return [str(c) for c in classes]

    def set_head_class(self, val):
        if val == "None":
            config.custom_head_label = None
        else:
            config.custom_head_label = val
        print(f"[DEBUG] Head class set to: {config.custom_head_label}")

    def set_player_class(self, val):
        config.custom_player_label = val
        print(f"[DEBUG] Player class set to: {config.custom_player_label}")

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

    def add_speed_section(self, label, min_key, max_key):
        f = ctk.CTkFrame(self.dynamic_frame, fg_color="#1a1a1a")
        f.pack(fill="x", pady=5)
        f.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(f, text=f"⚙️ {label} Aim Settings", font=("Segoe UI", 14, "bold"), text_color="#00e676").grid(row=0, column=0, columnspan=3, pady=(10, 5), padx=10, sticky="w")
        
        ctk.CTkLabel(f, text="X Speed:", text_color="#fff").grid(row=1, column=0, sticky="w", padx=10, pady=2)
        x_slider = ctk.CTkSlider(f, from_=0.1, to=1, number_of_steps=9)
        x_slider.set(getattr(config, min_key))
        x_slider.grid(row=1, column=1, sticky="ew", padx=(5, 5), pady=2)
        x_value_label = ctk.CTkLabel(f, text=f"{getattr(config, min_key):.2f}", text_color=NEON, width=50)
        x_value_label.grid(row=1, column=2, padx=10, pady=2)
        
        def update_x(val):
            val = float(val)
            setattr(config, min_key, val)
            x_value_label.configure(text=f"{val:.2f}")
        x_slider.configure(command=update_x)
        
        ctk.CTkLabel(f, text="Y Speed:", text_color="#fff").grid(row=2, column=0, sticky="w", padx=10, pady=(2, 10))
        y_slider = ctk.CTkSlider(f, from_=0.1, to=1, number_of_steps=9)
        y_slider.set(getattr(config, max_key))
        y_slider.grid(row=2, column=1, sticky="ew", padx=(5, 5), pady=(2, 10))
        y_value_label = ctk.CTkLabel(f, text=f"{getattr(config, max_key):.2f}", text_color=NEON, width=50)
        y_value_label.grid(row=2, column=2, padx=10, pady=(2, 10))
        
        def update_y(val):
            val = float(val)
            setattr(config, max_key, val)
            y_value_label.configure(text=f"{val:.2f}")
        y_slider.configure(command=update_y)

    def add_bezier_section(self, seg_key, cx_key, cy_key):
        f = ctk.CTkFrame(self.dynamic_frame, fg_color="#1a1a1a")
        f.pack(fill="x", pady=5)
        f.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(f, text="🌀 Bezier Curve Settings", font=("Segoe UI", 14, "bold"), text_color="#00e676").grid(row=0, column=0, columnspan=3, pady=(10, 5), padx=10, sticky="w")
        
        ctk.CTkLabel(f, text="Segments:", text_color="#fff").grid(row=1, column=0, sticky="w", padx=10, pady=2)
        seg_slider = ctk.CTkSlider(f, from_=0, to=20, number_of_steps=20, command=lambda v: setattr(config, seg_key, int(float(v))))
        seg_slider.set(getattr(config, seg_key))
        seg_slider.grid(row=1, column=1, sticky="ew", padx=(5, 5), pady=2)
        
        ctk.CTkLabel(f, text="Control X:", text_color="#fff").grid(row=2, column=0, sticky="w", padx=10, pady=2)
        cx_slider = ctk.CTkSlider(f, from_=0, to=60, number_of_steps=60, command=lambda v: setattr(config, cx_key, int(float(v))))
        cx_slider.set(getattr(config, cx_key))
        cx_slider.grid(row=2, column=1, sticky="ew", padx=(5, 5), pady=2)
        
        ctk.CTkLabel(f, text="Control Y:", text_color="#fff").grid(row=3, column=0, sticky="w", padx=10, pady=(2, 10))
        cy_slider = ctk.CTkSlider(f, from_=0, to=60, number_of_steps=60, command=lambda v: setattr(config, cy_key, int(float(v))))
        cy_slider.set(getattr(config, cy_key))
        cy_slider.grid(row=3, column=1, sticky="ew", padx=(5, 5), pady=(2, 10))

    def add_silent_section(self):
        f = ctk.CTkFrame(self.dynamic_frame, fg_color="#2a2a2a")
        f.pack(fill="x", pady=5)
        f.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(f, text="🤫 Silent Aim Settings", font=("Segoe UI", 14, "bold"), text_color="#00e676").grid(row=0, column=0, columnspan=3, pady=(10, 5), padx=10, sticky="w")
        
        ctk.CTkLabel(f, text="Speed:", text_color="#fff").grid(row=1, column=0, sticky="w", padx=10, pady=2)
        speed_slider = ctk.CTkSlider(f, from_=1, to=6, number_of_steps=5, command=lambda v: setattr(config, "silent_speed", int(float(v))))
        speed_slider.set(config.silent_speed)
        speed_slider.grid(row=1, column=1, sticky="ew", padx=(5, 5), pady=2)
        
        ctk.CTkLabel(f, text="Cooldown:", text_color="#fff").grid(row=2, column=0, sticky="w", padx=10, pady=(2, 10))
        cooldown_slider = ctk.CTkSlider(f, from_=0.00, to=0.5, number_of_steps=50, command=lambda v: setattr(config, "silent_cooldown", float(v)))
        cooldown_slider.set(config.silent_cooldown)
        cooldown_slider.grid(row=2, column=1, sticky="ew", padx=(5, 5), pady=(2, 10))

    def add_smooth_section(self):
        f = ctk.CTkFrame(self.dynamic_frame, fg_color="#0a0a0a")
        f.pack(fill="x", pady=5)
        f.grid_columnconfigure(1, weight=1)
        
        # Title
        ctk.CTkLabel(f, text="🌪️ WindMouse Smooth Aim", font=("Segoe UI", 14, "bold"), text_color="#00e676").grid(row=0, column=0, columnspan=3, pady=(10, 10), padx=10, sticky="w")
        
        # Core parameters
        params = [
            ("Gravity:", "smooth_gravity", 1, 20, 19),
            ("Wind:", "smooth_wind", 1, 20, 19),
            ("Close Speed:", "smooth_close_speed", 0.1, 1.0, 18),
            ("Far Speed:", "smooth_far_speed", 0.1, 1.0, 18),
            ("Reaction Time:", "smooth_reaction_max", 0.01, 0.3, 29),
            ("Max Step:", "smooth_max_step", 5, 50, 45)
        ]
        
        for i, (label, key, min_val, max_val, steps) in enumerate(params):
            ctk.CTkLabel(f, text=label, text_color="#fff", font=("Segoe UI", 11, "bold")).grid(row=i+1, column=0, sticky="w", padx=10, pady=2)
            
            slider = ctk.CTkSlider(f, from_=min_val, to=max_val, number_of_steps=steps)
            slider.set(getattr(config, key))
            slider.grid(row=i+1, column=1, sticky="ew", padx=(5, 5), pady=2)
            
            if "time" in key.lower():
                value_text = f"{getattr(config, key):.3f}s"
            elif "step" in key.lower():
                value_text = f"{getattr(config, key):.0f}px"
            else:
                value_text = f"{getattr(config, key):.2f}"
                
            value_label = ctk.CTkLabel(f, text=value_text, text_color=NEON, width=60, font=("Segoe UI", 11, "bold"))
            value_label.grid(row=i+1, column=2, padx=10, pady=2)
            
            def make_update_func(param_key, label_widget):
                def update_func(val):
                    setattr(config, param_key, float(val))
                    if "time" in param_key.lower():
                        text = f"{float(val):.3f}s"
                        if param_key == "smooth_reaction_max":
                            config.smooth_reaction_min = float(val) * 0.7
                    elif "step" in param_key.lower():
                        text = f"{float(val):.0f}px"
                    else:
                        text = f"{float(val):.2f}"
                    label_widget.configure(text=text)
                return update_func
            
            slider.configure(command=make_update_func(key, value_label))
        
        # Presets
        preset_frame = ctk.CTkFrame(f, fg_color="#1a1a1a", corner_radius=8)
        preset_frame.grid(row=len(params)+1, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 10))
        
        ctk.CTkLabel(preset_frame, text="Quick Presets:", font=("Segoe UI", 11, "bold"), text_color="#ccc").pack(pady=(8, 5))
        
        preset_buttons = ctk.CTkFrame(preset_frame, fg_color="transparent")
        preset_buttons.pack(pady=(0, 8))
        
        def apply_preset(preset_type):
            presets = {
                "human": (9.0, 3.0, 0.3, 0.7, 0.12, 12.0),
                "precise": (15.0, 1.5, 0.2, 0.5, 0.08, 8.0),
                "aggressive": (12.0, 5.0, 0.5, 0.9, 0.05, 20.0)
            }
            
            if preset_type in presets:
                values = presets[preset_type]
                config.smooth_gravity = values[0]
                config.smooth_wind = values[1]
                config.smooth_close_speed = values[2]
                config.smooth_far_speed = values[3]
                config.smooth_reaction_max = values[4]
                config.smooth_max_step = values[5]
                config.smooth_reaction_min = values[4] * 0.3
                
                # Refresh the UI
                self.update_dynamic_frame()
        
        for preset_name in ["human", "precise", "aggressive"]:
            ctk.CTkButton(
                preset_buttons, 
                text=preset_name.title(), 
                command=lambda p=preset_name: apply_preset(p), 
                width=90, 
                height=28
            ).pack(side="left", padx=3)

    def save_profile(self):
        config.save()
        self.error_text.set("✅ Profile saved successfully!")

    def load_profile(self):
        config.load()
        self.refresh_all()
        self.error_text.set("✅ Profile loaded successfully!")

    def reset_defaults(self):
        config.reset_to_defaults()
        self.refresh_all()
        self.error_text.set("✅ Settings reset to defaults!")

    def start_aimbot(self):
        start_aimbot()
        button_names = ["Left", "Right", "Middle", "Side 4", "Side 5"]
        button_name = button_names[config.selected_mouse_button] if config.selected_mouse_button < len(button_names) else f"Button {config.selected_mouse_button}"
        self.error_text.set(f"🎯 Aimbot started in {config.mode} mode! Hold {button_name} to aim.")

    def stop_aimbot(self):
        stop_aimbot()
        self.aimbot_status.set("Stopped")
        self.error_text.set("⏹ Aimbot stopped.")

    def on_close(self):
        stop_aimbot()
        self.destroy()

    def on_debug_toggle(self):
        config.show_debug_window = self.debug_checkbox_var.get()
        if not config.show_debug_window:
            try:
                import cv2
                cv2.destroyWindow("AI Debug")
            except Exception:
                pass

    def on_input_check_toggle(self):
        if self.input_check_var.get():
            self.show_input_check_window()
        else:
            self.hide_input_check_window()
    def on_button_mask_toggle(self):
        value = bool(self.button_mask_var.get())
        config.button_mask = value
        try:
            if hasattr(config, "save") and callable(config.save):
                config.save()
        except Exception as e:
            print(f"[WARN] Failed to save config.button_mask: {e}")

    def show_input_check_window(self):
        if hasattr(self, 'input_check_window') and self.input_check_window is not None:
            return
        self.input_check_window = ctk.CTkToplevel(self)
        self.input_check_window.title("Button States Monitor")
        self.input_check_window.geometry("320x240")
        self.input_check_window.resizable(False, False)
        self.input_check_window.configure(fg_color="#181818")
        
        ctk.CTkLabel(self.input_check_window, text="🎮 Input Monitor", font=("Segoe UI", 16, "bold"), text_color="#00e676").pack(pady=(15, 10))
        
        self.input_check_labels = []
        for i in range(5):
            frame = ctk.CTkFrame(self.input_check_window, fg_color="transparent")
            frame.pack(pady=3, padx=20, fill="x")
            
            ctk.CTkLabel(frame, text=f"Button {i}:", font=("Segoe UI", 12, "bold"), text_color="#fff").pack(side="left")
            
            lbl = ctk.CTkLabel(frame, text="Released", font=("Segoe UI", 12, "bold"), text_color="#FF5555")
            lbl.pack(side="right")
            
            self.input_check_labels.append(lbl)
        
        self.update_input_check_window()
        self.input_check_window.protocol("WM_DELETE_WINDOW", self._on_input_check_close)

    def update_input_check_window(self):
        if not hasattr(self, 'input_check_window') or self.input_check_window is None:
            return
        
        from mouse import button_states, button_states_lock
        
        with button_states_lock:
            for i, lbl in enumerate(self.input_check_labels):
                state = button_states.get(i, False)
                color = "#00FF00" if state else "#FF5555"
                text = "PRESSED" if state else "Released"
                lbl.configure(text=text, text_color=color)
        
        self.after(50, self.update_input_check_window)

    def hide_input_check_window(self):
        if hasattr(self, 'input_check_window') and self.input_check_window:
            self.input_check_window.destroy()
            self.input_check_window = None

    def _on_input_check_close(self):
        self.input_check_var.set(False)
        self.hide_input_check_window()


if __name__ == "__main__":
    app = EventuriGUI()
    app.mainloop()