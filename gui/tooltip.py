"""
Simple tooltip implementation for CustomTkinter widgets.
"""

import customtkinter as ctk
import tkinter as tk


class ToolTip:
    """Simple tooltip widget for CustomTkinter."""
    
    def __init__(self, widget, text="Widget info", delay=500, wrap_length=200):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wrap_length = wrap_length
        self.tooltip_window = None
        self.id = None
        
        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    
    def on_enter(self, event=None):
        """Called when mouse enters the widget."""
        self.schedule_tooltip()
    
    def on_leave(self, event=None):
        """Called when mouse leaves the widget."""
        self.cancel_tooltip()
        self.hide_tooltip()
    
    def on_motion(self, event=None):
        """Called when mouse moves over the widget."""
        self.cancel_tooltip()
        self.schedule_tooltip()
    
    def schedule_tooltip(self):
        """Schedule tooltip to appear after delay."""
        self.cancel_tooltip()
        self.id = self.widget.after(self.delay, self.show_tooltip)
    
    def cancel_tooltip(self):
        """Cancel scheduled tooltip."""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
    
    def show_tooltip(self):
        """Display the tooltip."""
        if self.tooltip_window:
            return
        
        # Get widget position
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Make tooltip stay on top but not focusable
        self.tooltip_window.wm_attributes("-topmost", True)
        
        # Create label with tooltip text
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#1a1a1a",
            foreground="#ffffff",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            wraplength=self.wrap_length,
            justify="left",
            padx=8,
            pady=4
        )
        label.pack()
    
    def hide_tooltip(self):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def create_info_button(parent, tooltip_text, **kwargs):
    """Create a small (i) info button with tooltip."""
    info_button = ctk.CTkButton(
        parent,
        text="ⓘ",
        width=20,
        height=20,
        font=("Segoe UI", 12, "bold"),
        fg_color="#333333",
        hover_color="#555555",
        text_color="#888888",
        corner_radius=10,
        **kwargs
    )
    
    # Add tooltip
    ToolTip(info_button, tooltip_text, delay=300, wrap_length=300)
    
    # Make button non-functional (just for display)
    info_button.configure(command=lambda: None)
    
    return info_button