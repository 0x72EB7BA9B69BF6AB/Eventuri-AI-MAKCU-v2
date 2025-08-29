NEON = "#ff1744"
BG = "#000000"

import customtkinter as ctk
def neon_button(*args, **kwargs):
    return ctk.CTkButton(*args, fg_color=NEON, hover_color="#d50000", text_color="#fff", **kwargs)
