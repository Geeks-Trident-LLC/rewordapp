"""
rewordapp.ui.comparison
=======================

Comparison dialog UI for original and rewritten text.
"""
import re

from rewordapp.ui import helper as ui_helper

from tkinter.font import Font

import rewordapp.ui as ui
import rewordapp.ui.logo as ui_logo

import rewordapp.config as config

import tkinter as tk

from rewordapp.libs.utils import split_by_matches


def show_diff(app, mode):
    """Validate text state and open the appropriate diff dialog."""

    if app.rewrite_sync.is_synced(app):
        show_dialog(app, mode)
        return

    # Build error message
    title = f"{mode.title()} View"

    if app.rewrite_sync.is_unrewritten(app):
        info = f"Cannot perform {mode} because there is no rewritten text."
    elif app.rewrite_sync.is_outdated(app):
        info = f"Cannot perform {mode} because the rewritten text is outdated."
    else:
        info = f"Cannot perform {mode} because the user input is empty."

    ui_helper.show_message_dialog(title=title, info=info)


def show_dialog(app, mode):
    """Display a mode‑specific dialog with header and styled text areas."""
    user_input = ui_helper.extract_text(app.user_textarea)
    output = ui_helper.extract_text(app.output_textarea)

    dialog = create_dialog(app.root, mode)
    add_app_header(dialog, mode)
    text_frame = create_frame(dialog, mode)
    add_textarea(text_frame, mode, user_input, output)


def create_dialog(parent, mode):
    """Create a resizable dialog window for the Weave tool."""
    dialog = ui.Toplevel(parent)
    dialog.title(f"{mode.title()} View - RewordApp CE")
    dialog.resizable(True, True)

    # Set size first
    width = 1000 if mode == "side-by-side" else 600
    height = 600 if mode == "interleave" else 800 if mode == "stack" else 400
    dialog.geometry(f"{width}x{height}")

    # Center relative to parent
    center_dialog(dialog, parent, width, height)

    # --- Layout configuration ---
    dialog.grid_columnconfigure(0, weight=1)    # Everything expands horizontally
    dialog.grid_rowconfigure(1, weight=1)       # Text area expands vertically
    if mode == "stack":
        dialog.grid_rowconfigure(2, weight=1)

    ui_logo.set_window_icon(dialog)

    return dialog


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
    if mode == "stack":
        frame.grid_rowconfigure(1, weight=1)

    frame.grid_columnconfigure(0, weight=1)
    if mode == "side-by-side":
        frame.grid_columnconfigure(1, weight=1)

    return frame


def add_textarea(parent, mode, user_input, output):
    """Add the appropriate text layout widget based on the selected mode."""
    mapping = {
        "interleave": add_interleave,
        "side-by-side": add_side_by_side,
        "stack": add_stack
    }
    func = mapping.get(mode, add_interleave)
    func(parent, user_input, output)


def add_interleave(parent, user_input, output):
    """Create a Text widget with scrollbars and interleaved diff-styled lines."""
    text = tk.Text(parent, wrap="none")
    text.grid(row=0, column=0, sticky="nsew")

    # Scrollbars
    vscroll = tk.Scrollbar(parent, orient="vertical", command=text.yview)
    vscroll.grid(row=0, column=1, sticky="ns")
    text.config(yscrollcommand=vscroll.set)

    hscroll = tk.Scrollbar(parent, orient="horizontal", command=text.xview)
    hscroll.grid(row=1, column=0, sticky="ew")
    text.config(xscrollcommand=hscroll.set)

    # Fonts
    base_font = Font(family="Courier", size=10)

    # Tags
    text.tag_configure("similar_odd", font=base_font, foreground="black")
    text.tag_configure("similar_even", font=base_font, foreground="#444444")
    text.tag_configure("diff_odd", font=base_font, foreground="#cc0000")
    text.tag_configure("diff_even", font=base_font, foreground="#22863A")

    left_lines = user_input.splitlines(keepends=True)
    right_lines = output.splitlines(keepends=True)

    def insert_pair(odd, even):
        """Insert a pair of lines with appropriate diff/similar tags."""
        tag_ = "similar" if odd.strip() == even.strip() else "diff"
        text.insert("end", odd, f"{tag_}_odd")
        if not odd.endswith(("\n", "\r")):
            text.insert("end", "\n", f"{tag_}_odd")
        text.insert("end", even, f"{tag_}_even")

    for i, left_line in enumerate(left_lines):
        right_line = right_lines[i] if i < len(right_lines) else ""

        if not left_line.strip():
            text.insert("end", left_line, "similar_odd")
            continue

        # Simple case: whole-line compare OR no whitespace → treat as one token
        if left_line.strip() == right_line.strip() or not re.search(r"\s", left_line):
            insert_pair(left_line, right_line)
            continue

        # Token-level diff
        left_tokens = split_by_matches(left_line)
        right_tokens = split_by_matches(right_line)

        # Odd side
        for idx, token in enumerate(left_tokens):
            other = right_tokens[idx] if idx < len(right_tokens) else ""
            tag = "similar" if token == other else "diff"
            text.insert("end", token, f"{tag}_odd")

        if not left_line.endswith(("\n", "\r")):
            text.insert("end", "\n", f"similar_odd")

        # Even side
        for idx, token in enumerate(right_tokens):
            other = left_tokens[idx] if idx < len(left_tokens) else ""
            tag = "similar" if token == other else "diff"
            text.insert("end", token, f"{tag}_even")

    text.config(state="disabled")


def add_side_by_side(parent, user_input, output):
    """Display two synchronized text widgets for side‑by‑side comparison."""
    font = Font(family="Courier", size=10)

    # --- Create text widgets ---
    left = tk.Text(parent, font=font, wrap="none")
    right = tk.Text(parent, font=font, wrap="none", foreground="blue")

    left.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
    right.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

    # --- Shared tag definitions ---
    def configure_tags(widget):
        widget.tag_configure("similar_left", font=font, foreground="black")
        widget.tag_configure("similar_right", font=font, foreground="#444444")
        widget.tag_configure("diff_left", font=font, foreground="#cc0000")
        widget.tag_configure("diff_right", font=font, foreground="#22863A")

    configure_tags(left)
    configure_tags(right)

    left_lines = user_input.splitlines(keepends=True)
    right_lines = output.splitlines(keepends=True)

    # --- Insert content ---
    for i, l_line in enumerate(left_lines):
        r_line = right_lines[i] if i < len(right_lines) else ""

        if l_line.strip() == r_line.strip():
            left.insert("end", l_line, "similar_left")
            right.insert("end", l_line, "similar_right")
            continue

        # Token-level diff
        l_tokens = split_by_matches(l_line)
        r_tokens = split_by_matches(r_line)

        for idx, l_tok in enumerate(l_tokens):
            r_tok = r_tokens[idx] if idx < len(r_tokens) else ""
            tag = "similar" if l_tok == r_tok else "diff"
            left.insert("end", l_tok, f"{tag}_left")
            right.insert("end", r_tok, f"{tag}_right")

    left.config(state="disabled")
    right.config(state="disabled")

    # --- Shared scrollbars ---
    vscroll = tk.Scrollbar(parent, orient="vertical")
    hscroll = tk.Scrollbar(parent, orient="horizontal")

    vscroll.grid(row=0, column=2, sticky="ns")
    hscroll.grid(row=1, column=0, columnspan=2, sticky="ew")

    # --- Scroll sync helpers ---
    def sync_y(*args):
        left.yview(*args)
        right.yview(*args)

    def sync_x(*args):
        left.xview(*args)
        right.xview(*args)

    def on_left_y(*args):
        right.yview_moveto(args[0])
        vscroll.set(*args)

    def on_right_y(*args):
        left.yview_moveto(args[0])
        vscroll.set(*args)

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


def add_stack(parent, user_input, output):
    """Display two synchronized text widgets in a vertical (stacked) layout."""
    font = Font(family="Courier", size=10)

    # --- Create text widgets ---
    top = tk.Text(parent, font=font, wrap="none")
    bottom = tk.Text(parent, font=font, wrap="none", foreground="blue")

    top.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
    bottom.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    # --- Shared tag configuration ---
    def configure_tags(widget):
        widget.tag_configure("similar_top", font=font, foreground="black")
        widget.tag_configure("similar_bottom", font=font, foreground="#444444")
        widget.tag_configure("diff_top", font=font, foreground="#cc0000")
        widget.tag_configure("diff_bottom", font=font, foreground="#22863A")

    configure_tags(top)
    configure_tags(bottom)

    top_lines = user_input.splitlines(keepends=True)
    bottom_lines = output.splitlines(keepends=True)

    # --- Insert content ---
    for i, t_line in enumerate(top_lines):
        b_line = bottom_lines[i] if i < len(bottom_lines) else ""

        if t_line.strip() == b_line.strip():
            top.insert("end", t_line, "similar_top")
            bottom.insert("end", t_line, "similar_bottom")
            continue

        # Token-level diff
        t_tokens = split_by_matches(t_line)
        b_tokens = split_by_matches(b_line)

        for idx, t_tok in enumerate(t_tokens):
            b_tok = b_tokens[idx] if idx < len(b_tokens) else ""
            tag = "similar" if t_tok == b_tok else "diff"
            top.insert("end", t_tok, f"{tag}_top")
            bottom.insert("end", b_tok, f"{tag}_bottom")

    top.config(state="disabled")
    bottom.config(state="disabled")

    # --- Shared scrollbars ---
    vscroll = tk.Scrollbar(parent, orient="vertical")
    hscroll = tk.Scrollbar(parent, orient="horizontal")

    vscroll.grid(row=0, column=1, rowspan=2, sticky="ns")
    hscroll.grid(row=2, column=0, sticky="ew")

    # --- Scroll sync helpers ---
    def sync_y(*args):
        top.yview(*args)
        bottom.yview(*args)

    def sync_x(*args):
        top.xview(*args)
        bottom.xview(*args)

    def on_top_y(*args):
        bottom.yview_moveto(args[0])
        vscroll.set(*args)

    def on_bottom_y(*args):
        top.yview_moveto(args[0])
        vscroll.set(*args)

    def on_top_x(*args):
        bottom.xview_moveto(args[0])
        hscroll.set(*args)

    def on_bottom_x(*args):
        top.xview_moveto(args[0])
        hscroll.set(*args)

    # Connect scrollbars
    vscroll.config(command=sync_y)
    hscroll.config(command=sync_x)

    # Connect text widgets
    top.config(yscrollcommand=on_top_y, xscrollcommand=on_top_x)
    bottom.config(yscrollcommand=on_bottom_y, xscrollcommand=on_bottom_x)
