"""
rewordapp.ui.comparison
-----------------------

Comparison dialog UI for original and rewritten text.
"""

from rewordapp.ui import helper as ui_helper

from tkinter.font import Font

import rewordapp.ui as ui
import rewordapp.ui.logo as ui_logo

import rewordapp.config as config

import tkinter as tk


button_width = 5.5 if ui.is_macos else 8


def center_dialog(dialog, parent, width, height):
    """Center a Toplevel dialog relative to its parent window."""
    # parent.update_idletasks()
    # dialog.update_idletasks()

    # Parent geometry
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    pw = parent.winfo_width()
    ph = parent.winfo_height()

    # Compute centered position
    x = px + (pw - width) // 2
    y = py + (ph - height) // 2

    dialog.geometry(f"{width}x{height}+{x}+{y}")


def show(app):
    """Dialog with header, scrollable text area, and Cancel/Save buttons."""
    dialog = tk.Toplevel(app.root)
    dialog.title("Editor - Rewordapp CE")
    dialog.resizable(True, True)

    # Set size first
    width, height = 600, 400
    dialog.geometry(f"{width}x{height}")

    # Center relative to parent
    center_dialog(dialog, app.root, width, height)

    # Layout: header (0), text area (1), footer (2)
    dialog.grid_columnconfigure(0, weight=1)
    dialog.grid_rowconfigure(1, weight=1)

    ui_logo.set_window_icon(dialog)

    # --- Header ---
    header = tk.Label(
        dialog,
        text=f"Rules Editor - {config.main_app_text}",
        anchor="w",
        background="lightgray",
        foreground="navy",
        font=Font(size=14, weight="bold"),
    )
    header.grid(row=0, column=0, sticky="ew")

    # --- Text area with scrollbars ---
    text_frame = tk.Frame(dialog)
    text_frame.grid(row=1, column=0, sticky="nsew")
    text_frame.grid_columnconfigure(0, weight=1)
    text_frame.grid_rowconfigure(0, weight=1)

    text = tk.Text(text_frame, wrap="none", font=Font(family="Courier", size=10))
    text.grid(row=0, column=0, sticky="nsew")

    if app.rules.strip():
        text.insert("1.0", app.rules)

    vscroll = tk.Scrollbar(text_frame, orient="vertical", command=text.yview)
    vscroll.grid(row=0, column=1, sticky="ns")

    hscroll = tk.Scrollbar(text_frame, orient="horizontal", command=text.xview)
    hscroll.grid(row=1, column=0, sticky="ew")

    text.config(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)

    # --- Footer buttons ---
    footer = tk.Frame(dialog)
    footer.grid(row=2, column=0, pady=4)

    def on_cancel():
        dialog.destroy()

    def on_save():
        rules = ui_helper.extract_text(text)
        app.rules = rules
        dialog.destroy()

    ui.create_widget(
        "button", parent=footer, text="Cancel", width=button_width,
        command=on_cancel,
        layout=("grid", dict(row=0, column=0, padx=2))
    )

    ui.create_widget(
        "button", parent=footer, text="Save", width=button_width,
        command=on_save,
        layout=("grid", dict(row=0, column=1, padx=2))
    )

    return dialog
