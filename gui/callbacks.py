from core.config import config
import customtkinter as ctk
from tkinter import messagebox
import core.aimbot as aimbot
from core.aimbot import start_aimbot, stop_aimbot, is_aimbot_running, reload_model, get_model_classes, get_model_size
from hardware.mouse import connect_to_makcu, button_states, button_states_lock
import os
import glob
import cv2

class GUICallbacks:
    def refresh_all(self):
        self.fov_slider.set(config.region_size)
        self.fov_value.configure(text=str(config.region_size))
        self.offset_slider.set(config.player_y_offset)
        self.offset_value.configure(text=str(config.player_y_offset))
        self.btn_var.set(config.selected_mouse_button)
        self.mode_var.set(config.mode)
        self.model_name.set(os.path.basename(config.model_path))
        self.model_menu.set(os.path.basename(config.model_path))
        self.model_size.set(get_model_size(config.model_path))
        
        # Update aimbot status 
        self.aimbot_status.set("Running" if is_aimbot_running() else "Stopped")
            
        if config.makcu_connected:
            self.connection_status.set(config.makcu_status_msg)
            self.connection_color.set("#00FF00")
        else:
            self.connection_status.set(config.makcu_status_msg)
            self.connection_color.set("#b71c1c")
        self.conn_status_lbl.configure(text_color=self.connection_color.get())
        self.conf_slider.set(config.conf)
        self.conf_value.configure(text=f"{config.conf:.2f}")
        self.in_game_sens_slider.set(config.in_game_sens)
        self.in_game_sens_value.configure(text=f"{config.in_game_sens:.2f}")  # Fixed typo here
        self.imgsz_slider.set(config.imgsz)
        self.imgsz_value.configure(text=str(config.imgsz))
        self.load_class_list()
        self.update_dynamic_frame()
        self.update_idletasks()
        self.after(10, lambda: self._autosize())
        self.toggle_humanize()
        self.debug_checkbox_var.set(config.show_debug_window)
        self.input_check_var.set(False)
        self.error_text.set("")

    def on_connect(self):
        if connect_to_makcu():
            self.error_text.set("")
        else:
            self.error_text.set("Failed to connect! " + config.makcu_status_msg)
        self.refresh_all()

    def update_fov(self, val):
        config.region_size = int(round(val))
        self.fov_value.configure(text=str(config.region_size))

    def update_offset(self, val):
        config.player_y_offset = int(round(val))
        self.offset_value.configure(text=str(config.player_y_offset))

    def update_mouse_btn(self):
        config.selected_mouse_button = self.btn_var.get()

    def update_mode(self):
        config.mode = self.mode_var.get()
        self.update_dynamic_frame()
        self.update_idletasks()
        self.after(10, lambda: self._autosize())

    def update_conf(self, val):
        config.conf = round(float(val), 2)
        self.conf_value.configure(text=f"{config.conf:.2f}")

    def update_imgsz(self, val):
        config.imgsz = int(round(val))
        self.imgsz_value.configure(text=str(config.imgsz))

    def update_max_detect(self, val):
        val = int(round(float(val)))
        config.max_detect = val
        self.max_detect_label.configure(text=str(val))

    def update_in_game_sens(self, val):
        config.in_game_sens = round(float(val), 2)
        self.in_game_sens_value.configure(text=f"{config.in_game_sens:.2f}")

    def toggle_humanize(self):
        if self.aim_humanize_var.get():
            self.humanize_slider.grid(row=2, column=1, padx=(2, 12))
            self.humanize_slider_label.grid(row=2, column=2, padx=(2, 8))
            config.aim_humanization = int(self.humanize_slider.get())
        else:
            self.humanize_slider.grid_remove()
            self.humanize_slider_label.grid_remove()
            config.aim_humanization = 0

    def update_humanization(self, val):
        val = int(round(float(val)))
        self.humanize_slider_label.configure(text=str(val))
        config.aim_humanization = val

    def poll_fps(self):
        self.fps_var.set(f"FPS: {aimbot.fps:.1f}")
        
        # Update aimbot status
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
            except Exception as e:
                self.error_text.set(str(e))
        else:
            self.error_text.set(f"File not found: {path}")

    def reload_model(self):
        try:
            reload_model(config.model_path)
            self.load_class_list()
            self.error_text.set("")
        except Exception as e:
            self.error_text.set(str(e))

    def load_class_list(self):
        try:
            classes = get_model_classes(config.model_path)
            self.available_classes = classes
            self.class_listbox.delete("0.0", "end")
            
            # Handle both numeric and text classes
            for i, c in enumerate(classes):
                # Show both class ID and name for clarity
                display_text = f"Class {i}: {c}\n"
                self.class_listbox.insert("end", display_text)
            
            # Create dropdown options with both ID and name
            class_options = []
            for i, c in enumerate(classes):
                if str(c).isdigit():
                    # For numeric classes, show "ID: name" format
                    class_options.append(f"{c}")
                else:
                    # For text classes, show as-is
                    class_options.append(c)
            
            self.head_class_menu.configure(values=["None"] + class_options)
            self.player_class_menu.configure(values=class_options)
            
            # Set current values - handle numeric classes
            current_head = config.custom_head_label
            current_player = config.custom_player_label
            
            self.head_class_var.set(str(current_head) if current_head is not None else "None")
            self.player_class_var.set(str(current_player) if current_player is not None else "0")
            
        except Exception as e:
            self.error_text.set(f"Failed to load classes: {e}")

    def get_available_classes(self):
        classes = getattr(self, "available_classes", ["0", "1"])
        # Return string versions of classes for dropdown
        return [str(c) for c in classes]

    def set_head_class(self, val):
        if val == "None":
            config.custom_head_label = None
        else:
            # Handle numeric classes
            if val.isdigit():
                config.custom_head_label = val  # Keep as string for consistent comparison
            else:
                config.custom_head_label = val
        print(f"[DEBUG] Head class set to: {config.custom_head_label}")

    def set_player_class(self, val):
        # Handle numeric classes
        if val.isdigit():
            config.custom_player_label = val  # Keep as string for consistent comparison
        else:
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

    def _autosize(self):
        self.update_idletasks()
        req_width = self.winfo_reqwidth()
        req_height = self.winfo_reqheight()
        self.geometry(f"{req_width}x{req_height}")

    def save_profile(self):
        config.save()
        messagebox.showinfo("Profile Saved", "Config saved!")

    def load_profile(self):
        config.load()
        self.refresh_all()

    def reset_defaults(self):
        config.reset_to_defaults()
        self.refresh_all()

    def start_aimbot(self):
        start_aimbot()
        button_names = ["Left", "Right", "Middle", "Side 4", "Side 5"]
        button_name = button_names[config.selected_mouse_button] if config.selected_mouse_button < len(button_names) else f"Button {config.selected_mouse_button}"
        self.error_text.set(f"Aimbot started. Hold {button_name} to aim.")

    def stop_aimbot(self):
        stop_aimbot()
        self.aimbot_status.set("Stopped")
        self.error_text.set("")

    def on_close(self):
        stop_aimbot()
        self.destroy()

    def on_debug_toggle(self):
        config.show_debug_window = self.debug_checkbox_var.get()
        if not config.show_debug_window:
            try:
                cv2.destroyWindow("AI Debug")
            except Exception:
                pass

    def on_input_check_toggle(self):
        if self.input_check_var.get():
            self.show_input_check_window()
        else:
            self.hide_input_check_window()

    def show_input_check_window(self):
        if hasattr(self, 'input_check_window') and self.input_check_window is not None:
            return
        self.input_check_window = ctk.CTkToplevel(self)
        self.input_check_window.title("Button States")
        self.input_check_window.geometry("220x160")
        self.input_check_window.resizable(False, False)
        self.input_check_window.configure(bg="#181818")
        self.input_check_labels = []
        for i in range(5):
            lbl = ctk.CTkLabel(self.input_check_window, text=f"Button {i}:", text_color="#fff", font=("Segoe UI", 16, "bold"))
            lbl.pack(anchor="w", padx=18, pady=6)
            self.input_check_labels.append(lbl)
        self.update_input_check_window()
        self.input_check_window.protocol("WM_DELETE_WINDOW", self._on_input_check_close)

    def update_input_check_window(self):
        if not hasattr(self, 'input_check_window') or self.input_check_window is None:
            return
        with button_states_lock:
            for i, lbl in enumerate(self.input_check_labels):
                state = button_states.get(i, False)
                color = "#00FF00" if state else "#FF5555"
                lbl.configure(text=f"Button {i}: {state}", text_color=color)
        self.after(50, self.update_input_check_window)

    def hide_input_check_window(self):
        if hasattr(self, 'input_check_window') and self.input_check_window:
            self.input_check_window.destroy()
            self.input_check_window = None

    def _on_input_check_close(self):
        self.input_check_var.set(False)
        self.hide_input_check_window()