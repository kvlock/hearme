
import customtkinter as ctk
from ui.main_window import MainWindow
import os

def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Set window icon
    if os.path.exists("assets/icon.png"):
        ctk.set_window_icon("assets/icon.png")

    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()