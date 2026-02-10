"""
rewordapp.ui.weave
------------------

Weave dialog UI components for displaying original and rewritten text.
"""

from tkinter.font import Font

import rewordapp.ui as ui
import rewordapp.ui.logo as ui_logo

import rewordapp.config as config

import tkinter as tk


def show_interleave(app, user_input, output):
    """Display the Weave dialog with header and styled text areas."""
    dialog = create_dialog(app.root)
    add_app_header(dialog)
    text_frame = create_frame(dialog)
    add_textarea(text_frame, user_input, output)

def create_dialog(parent):
    """Create a resizable dialog window for the Weave tool."""
    dialog = ui.Toplevel(parent)
    dialog.title("Weave - RewordApp CE")
    dialog.resizable(True, True)

    # --- Layout configuration ---
    dialog.grid_rowconfigure(1, weight=1)      # Text area expands vertically
    dialog.grid_columnconfigure(0, weight=1)   # Everything expands horizontally

    ui_logo.set_window_icon(dialog)

    return dialog


def add_app_header(parent):
    """Create a bold‑italic application header label."""
    header = tk.Label(
        parent,
        text=f"Interleave Comparison - {config.main_app_text}",
        anchor="w",
        foreground="navy",
        background="lightgray",
    )
    header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

    # Build a bold‑italic font based on TkDefaultFont
    base = Font(name="TkDefaultFont", exists=True, root=header)
    header_font = [
        base.cget("family"),
        base.cget("size") + 4,
        "bold",
        "italic",
    ]

    header.configure(font=header_font)

    return header


def create_frame(parent):
    """Create a resizable frame with padding and grid expansion."""

    frame = tk.Frame(parent)
    frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    return frame


def add_textarea(parent, user_input, output):
    """Create a Text widget with scrollbars and alternating styled lines."""

    text = tk.Text(parent, wrap="none")
    text.grid(row=0, column=0, sticky="nsew")

    # Vertical scrollbar
    vscroll = tk.Scrollbar(parent, orient="vertical", command=text.yview)
    vscroll.grid(row=0, column=1, sticky="ns")
    text.config(yscrollcommand=vscroll.set)

    # Horizontal scrollbar
    hscroll = tk.Scrollbar(parent, orient="horizontal", command=text.xview)
    hscroll.grid(row=1, column=0, sticky="ew")
    text.config(xscrollcommand=hscroll.set)

    # --- Define fonts ---

    base = Font(name="TkDefaultFont", exists=True, root=text)
    size = base.cget("size")

    normal_font = Font(family="Courier", size=size)
    italic_blue = Font(family="Courier", size=size, slant="italic")

    # --- Define tags ---
    text.tag_configure("odd", font=normal_font, foreground="black")
    text.tag_configure("even", font=italic_blue, foreground="blue")

    # --- Insert sample lines with alternating styles ---

    lines = user_input.splitlines(keepends=True)
    other_lines = output.splitlines(keepends=True)

    for index, odd_line in enumerate(lines):
        even_line = other_lines[index] if index < len(other_lines) else ""
        if odd_line.strip():
            text.insert("end", odd_line, "odd")
            if not odd_line.endswith(("\n", "\r")):
                text.insert("end", "\n", "odd")
            text.insert("end", even_line, "even")
        else:
            text.insert("end", odd_line, "odd")
