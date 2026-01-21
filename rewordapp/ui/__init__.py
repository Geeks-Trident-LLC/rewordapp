"""
rewordapp.ui.__init__
---------------------

This module initializes the UI package for RewordApp CE.

Responsibilities include:
- Exposing core Tkinter/ttk widget classes and custom UI components.
- Providing decorators and helper utilities for consistent widget creation and layout.
- Serving as the entry point for importing UI functionality across submodules
  (e.g., `ui.menu`, `ui.about`, `ui.helper`).
"""

from typing import Any, Callable, Dict, Optional
import platform
import functools

import tkinter as tk
from tkinter import ttk


is_macos = platform.system() == 'Darwin'
is_linux = platform.system() == 'Linux'
is_window = platform.system() == 'Windows'


Tk = tk.Tk

Toplevel = tk.Toplevel

Frame = ttk.Frame
PanedWindow = ttk.PanedWindow

LabelFrame = ttk.LabelFrame
Label = ttk.Label

Button = ttk.Button

TextBox = ttk.Entry
TextArea = tk.Text

Scrollbar = ttk.Scrollbar

RadioButton = tk.Radiobutton if is_linux else ttk.Radiobutton
CheckBox = tk.Checkbutton if is_linux else ttk.Checkbutton

Menu = tk.Menu


def apply_layout(func: Callable) -> Callable:
    """Decorator to apply a Tkinter geometry manager (grid, pack, place) to a widget."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        widget = func(*args, **kwargs)
        layout = kwargs.pop("layout", None)
        if isinstance(layout, (list, tuple)) and len(layout) == 2:
            method_name, layout_options = layout
            method_name = str(method_name).lower()
            if method_name in {"grid", "pack", "place"}:
                layout_method = getattr(widget, method_name, None)
                if callable(layout_method):
                    layout_method(**layout_options)
        return widget
    return wrapper

