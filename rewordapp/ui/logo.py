import tkinter as tk
from os import path

def set_window_icon(widget) -> None:
    """Set the application window icon using the bundled logo image."""
    # Directory containing the current file
    base_dir = path.dirname(path.abspath(__file__))

    # Path to the logo image
    file_path = path.join(base_dir, "images", "logo.png")

    # Load logo (PhotoImage supports .png, .gif, .ppm)
    logo = tk.PhotoImage(file=file_path)
    widget.iconphoto(False, logo)