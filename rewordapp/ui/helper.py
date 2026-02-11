"""
rewordapp.ui.helper
===================

Utility functions for constructing and managing Tkinter UI components
in the Rewordapp GUI application. These helpers are designed to simplify
layout code and avoid runtime errors when working with varying widget types.

"""


from typing import Any, Optional, Tuple, Dict
from typing import Union

import webbrowser

from tkinter import ttk
from tkinter.font import Font
import tkinter as tk
from tkinter import messagebox

import rewordapp.ui as ui
import rewordapp.config as config


class Position:
    """Simple counter that tracks a numeric position."""

    def __init__(self, value: int = 0) -> None:
        self.value = value

    def increment(self) -> int:
        """Increase the position by one and return the new value."""
        self.value += 1
        return self.value


class RewriteSync:
    """Track and validate whether user text and rewritten text are in sync."""

    def __init__(self, app=None):
        self.initial_input = ""
        self.initial_output = ""
        self.is_application_app = is_application_app(app)
        if self.is_application_app:
            self.initial_input = extract_text(app.user_textarea)
            self.initial_output = extract_text(app.output_textarea)

    def __bool__(self):
        return self.is_application_app

    def __len__(self):
        return 1 if self.is_application_app else 0

    def is_synced(self, app) -> bool:
        """Return True if both input and output match the stored originals."""

        if not is_application_app(app) or not self:
            return False

        current_in = extract_text(app.user_textarea)
        current_out = extract_text(app.output_textarea)

        return (
            current_in.strip()
            and current_out.strip()
            and current_in == self.initial_input
            and current_out == self.initial_output
        )

    def is_outdated(self, app) -> bool:
        """Return True if input changed but output still matches the old rewrite."""
        if not is_application_app(app) or not self:
            return False

        current_in = extract_text(app.user_textarea)
        current_out = extract_text(app.output_textarea)

        return (
            current_in.strip()
            and current_in != self.initial_input
            and current_out == self.initial_output
        )

    def is_unrewritten(self, app) -> bool:
        """Return True if user input exists but no rewritten text is present."""
        if not is_application_app(app) or not self:
            return False

        current_in = extract_text(app.user_textarea).strip()
        current_out = extract_text(app.output_textarea).strip()
        return bool(current_in) and not current_out

    def is_input_empty(self, app) -> bool:
        """Return True if user input is empty."""
        if not is_application_app(app) or not self:
            return False
        return len(extract_text(app.user_textarea).strip()) == 0


def is_application_app(app):
    return type(app).__name__ == "Application"


def get_center_coordinates(
        parent: tk.Tk, child_width: int, child_height: int
) -> Tuple[int, int]:
    """Calculate coordinates to center a child window within its parent.

    Parameters
    ----------
    parent : tkinter.Tk or tkinter.Toplevel
        Parent window whose geometry is used as reference.
    child_width : int
        Width of the child window.
    child_height : int
        Height of the child window.

    Returns
    -------
    tuple of int
        (x, y) coordinates for placing the child window centered
        relative to the parent window.
    """
    geometry = parent.winfo_geometry()  # format: "WxH+X+Y"
    size, x_str, y_str = geometry.split("+")
    parent_x, parent_y = int(x_str), int(y_str)
    parent_w, parent_h = map(int, size.split("x"))

    x = parent_x + (parent_w - child_width) // 2
    y = parent_y + (parent_h - child_height) // 2
    return x, y


def center_window(
    parent: Union[tk.Tk, tk.Toplevel],
    window: Union[tk.Tk, tk.Toplevel],
    width: int,
    height: int,
    x_resizable: bool = False,
    y_resizable: bool = False
) -> None:
    """Center a Tkinter window relative to its parent.

    Parameters
    ----------
    parent : tkinter.Tk or tkinter.Toplevel
        The parent window used as reference for positioning.
    window : tkinter.Tk or tkinter.Toplevel
        The child window to be centered.
    width : int
        Desired width of the child window.
    height : int
        Desired height of the child window.
    x_resizable : bool, optional
        Whether the window can be resized horizontally. Default is False.
    y_resizable : bool, optional
        Whether the window can be resized vertically. Default is False.

    Returns
    -------
    None
        Configures geometry and resizability of the child window.
    """
    x, y = get_center_coordinates(parent, width, height)
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.resizable(x_resizable, y_resizable)


def make_modal(dialog: Union[tk.Toplevel, tk.Tk]) -> None:
    """Configure a Tkinter window to behave as a modal dialog.

    Parameters
    ----------
    dialog : tkinter.Toplevel or tkinter.Tk
        The dialog or window instance to make modal.

    Returns
    -------
    None
        Blocks interaction with other windows until the dialog is closed.
    """
    parent = dialog.master if dialog.master else None
    if dialog.master:
        dialog.transient(parent)

    dialog.wait_visibility()
    dialog.grab_set()
    dialog.wait_window()


def show_message_dialog(
    title: Optional[str] = None,
    error: Optional[str] = None,
    warning: Optional[str] = None,
    info: Optional[str] = None,
    question: Optional[str] = None,
    okcancel: Optional[str] = None,
    retrycancel: Optional[str] = None,
    yesno: Optional[str] = None,
    yesnocancel: Optional[str] = None,
    **options
) -> Any:
    """Display a tkinter message dialog based on the provided message type.

    Parameters
    ----------
    title : str, optional
        Title of the dialog window.
    error : str, optional
        Error message to display.
    warning : str, optional
        Warning message to display.
    info : str, optional
        Information message to display.
    question : str, optional
        Question prompt to display.
    okcancel : str, optional
        OK/Cancel prompt message.
    retrycancel : str, optional
        Retry/Cancel prompt message.
    yesno : str, optional
        Yes/No prompt message.
    yesnocancel : str, optional
        Yes/No/Cancel prompt message.
    options : dict, optional
        Additional keyword arguments passed to the messagebox.

    Returns
    -------
    Any
        Result of the dialog interaction (string, boolean, or None).
    """
    mapping = {
        error: messagebox.showerror,
        warning: messagebox.showwarning,
        info: messagebox.showinfo,
        question: messagebox.askquestion,
        okcancel: messagebox.askokcancel,
        retrycancel: messagebox.askretrycancel,
        yesno: messagebox.askyesno,
        yesnocancel: messagebox.askyesnocancel,
    }

    for message, func in mapping.items():
        if message:
            return func(title=title, message=message, **options)

    # Default fallback: show info dialog
    return messagebox.showinfo(title=title, message=info or "", **options)

@ui.apply_layout
def create_styled_label(
    parent: tk.Widget,
    text: str = "",
    link: str = "",
    options: dict = None,
    increased_size: int = 0,
    bold: bool = False,
    underline: bool = False,
    italic: bool = False,
    layout: Optional[Tuple[str, Dict[str, Any]]] = None     # noqa
) -> ttk.Label:
    """Create a styled Tkinter label with optional hyperlink behavior.

    Parameters
    ----------
    parent : tkinter.Widget
        The parent container for the label.
    text : str, optional
        Text to display in the label. Default is an empty string.
    link : str, optional
        URL to open when the label is clicked. Default is empty (no link).
    options : dict, optional
        other options initialize label
    increased_size : int, optional
        Amount to increase the base font size. Default is 0.
    bold : bool, optional
        If True, renders text in bold. Default is False.
    underline : bool, optional
        If True, underlines the text. Default is False.
    italic : bool, optional
        If True, italicizes the text. Default is False.
    layout : tuple, optional
        Layout method and kwargs, e.g. ("grid", {"row":0, "column":0}).

    Returns
    -------
    ttk.Label
        A styled label widget, optionally bound to open a hyperlink.
    """

    def mouse_over(event):
        if "underline" not in event.widget.font:
            event.widget.configure(
                font=event.widget.font + ["underline"],
                cursor="hand2"
            )

    def mouse_out(event):
        event.widget.config(font=event.widget.font, cursor="arrow")

    def mouse_press(event):
        webbrowser.open_new_tab(event.widget.link)

    options = options if isinstance(options, dict) else {}

    if link:
        style = ttk.Style()
        style.configure("Blue.TLabel", foreground="blue")
        label = ui.Label(parent, text=text, style="Blue.TLabel", **options)
        label.bind("<Enter>", mouse_over)
        label.bind("<Leave>", mouse_out)
        label.bind("<Button-1>", mouse_press)
    else:
        label = ui.Label(parent, text=text, **options)

    font = Font(name="TkDefaultFont", exists=True, root=label)
    font_spec = [font.cget("family"), font.cget("size") + increased_size]
    if bold:
        font_spec.append("bold")
    if underline:
        font_spec.append("underline")
    if italic:
        font_spec.append("italic")

    label.configure(font=font_spec)
    label.font = font_spec
    label.link = link

    return label


def open_app_resource(resource: str) -> None:
    """Open a specified application resource in a web browser.

    Parameters
    ----------
    resource : str
        The resource key to open. Supported values: "license", "documentation".
    """
    resources = {
        "license": config.license_url,
        "documentation": config.documentation_url,
    }
    url = resources.get(resource)
    if url:
        webbrowser.open_new_tab(url)


def extract_text(textarea) -> str:
    """Return textarea content without the trailing newline added by Tkinter."""
    text = textarea.get("1.0", "end")
    last_two = text[-2:]
    return text[:-2] if last_two == "\r\n" else text[:-1]
