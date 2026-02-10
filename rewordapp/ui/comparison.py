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


def show_diff(app, mode):
    """Validate text state and open the appropriate diff dialog."""

    # Extract normalized text
    user_input = ui_helper.extract_text(app.user_textarea)
    output = ui_helper.extract_text(app.output_textarea)

    user_len = len(user_input)
    out_len = len(output)

    # Ready to compare: lengths match but content differs
    if user_len == out_len and user_input != output:
        show_dialog(app, mode)
        return

    # Build error message
    title = f"{mode.title()} Feature"

    if out_len == 0 and user_len > 0:
        info = f"Cannot perform {mode} because there is no rewritten text."
    elif user_len > 0 and user_len != out_len:
        info = f"Cannot perform {mode} because the rewritten text is outdated."
    else:
        info = f"Cannot perform {mode} because the user input is empty."

    ui_helper.show_message_dialog(title=title, info=info)


def show_dialog(app, mode):
    """Display a mode‑specific dialog with header and styled text areas."""
    dialog = create_dialog(app.root, mode)
    add_app_header(dialog, mode)
    text_frame = create_frame(dialog, mode)

    user_input = ui_helper.extract_text(app.user_textarea)
    output = ui_helper.extract_text(app.output_textarea)
    add_textarea(text_frame, mode, user_input, output)


def create_dialog(parent, mode):
    """Create a resizable dialog window for the Weave tool."""
    dialog = ui.Toplevel(parent)
    dialog.title(f"{mode.title()} - RewordApp CE")
    dialog.resizable(True, True)

    # --- Layout configuration ---
    dialog.grid_rowconfigure(1, weight=1)      # Text area expands vertically
    dialog.grid_columnconfigure(0, weight=1)   # Everything expands horizontally

    ui_logo.set_window_icon(dialog)

    return dialog


def add_app_header(parent, mode):
    """Create a bold‑italic application header label."""
    header = tk.Label(
        parent,
        text=f"{mode.title()} View - {config.main_app_text}",
        anchor="center" if mode == "side-by-side" else "w",
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


def create_frame(parent, mode):
    """Create a resizable frame with padding and grid expansion."""

    frame = tk.Frame(parent)
    frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    frame.grid_rowconfigure(0, weight=1)
    if mode == "side-by-side":
        frame.grid_columnconfigure(1, weight=1)

    frame.grid_columnconfigure(0, weight=1)
    return frame


def add_textarea(parent, mode, user_input, output):
    """Add the appropriate text layout widget based on the selected mode."""
    if mode == "interleave":
        add_interleave(parent, user_input, output)
    elif mode == "side-by-side":
        add_side_by_side(parent, user_input, output)


def add_interleave(parent, user_input, output):
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
    blue_font = Font(family="Courier", size=size)

    # --- Define tags ---
    text.tag_configure("odd", font=normal_font, foreground="black")
    text.tag_configure("even", font=blue_font, foreground="blue")

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


def add_side_by_side(parent, user_input, output):
    """Display two synchronized text areas side by side."""
    # --- Create two text widgets ---
    font = Font(family="Courier", size=10)
    left = tk.Text(parent, font=font, wrap="none")
    left.grid(row=0, column=0, sticky="nsew")
    left.insert(tk.INSERT, user_input)

    right = tk.Text(parent, font=font, foreground="blue", wrap="none")
    right.grid(row=0, column=1, sticky="nsew")
    right.insert(tk.INSERT, output)

    # --- Shared scrollbars ---
    vscroll = tk.Scrollbar(parent, orient="vertical")
    hscroll = tk.Scrollbar(parent, orient="horizontal")

    vscroll.grid(row=0, column=2, sticky="ns")
    hscroll.grid(row=1, column=0, columnspan=2, sticky="ew")

    # Sync vertical scrolling
    def sync_y(*args):
        left.yview(*args)
        right.yview(*args)

    def on_left_y(*args):
        right.yview_moveto(args[0])
        vscroll.set(*args)

    def on_right_y(*args):
        left.yview_moveto(args[0])
        vscroll.set(*args)

    # Sync horizontal scrolling
    def sync_x(*args):
        left.xview(*args)
        right.xview(*args)

    def on_left_x(*args):
        right.xview_moveto(args[0])
        hscroll.set(*args)

    def on_right_x(*args):
        left.xview_moveto(args[0])
        hscroll.set(*args)

    # Connect scrollbars
    vscroll.config(command=sync_y)
    hscroll.config(command=sync_x)

    # Connect text widgets
    left.config(yscrollcommand=on_left_y, xscrollcommand=on_left_x)
    right.config(yscrollcommand=on_right_y, xscrollcommand=on_right_x)
