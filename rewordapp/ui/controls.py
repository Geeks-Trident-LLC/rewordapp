"""
rewordapp.ui.controls
---------------------

UI controls and reusable widget components for RewordApp CE.

"""


import rewordapp.ui as ui
import re

from rewordapp.ui import helper as ui_helper
from rewordapp.ui import comparison

from rewordapp.deps import genericlib_file_module as file

from rewordapp.core import RewordBuilder

button_width = 5.5 if ui.is_macos else 8


class Position:
    """Simple counter that tracks a numeric position."""

    def __init__(self, value: int = 0) -> None:
        self.value = value

    def increment(self) -> int:
        """Increase the position by one and return the new value."""
        self.value += 1
        return self.value


def build_controls_frame(parent, app) -> None:
    """Create a control frame with buttons for file operations and text management."""
    frame = ui.create_widget(
        "frame", parent=parent,
        width=600, height=30, relief=ui.tk.RIDGE
    )

    build_action_buttons(frame, app)

    return frame


def build_action_buttons(parent, app) -> None:
    """Create action buttons for file operations and text management within the given parent frame."""

    position = Position()

    ui.create_widget(
        "button", parent=parent, text="Open", width=button_width,
        command=lambda: import_file_to_input(app),
        layout = ("grid", dict(row=0, column=position.value, pady=2))
    )

    ui.create_widget(
        "button", parent=parent, text="Save", width=button_width,
        command=lambda: export_output_to_file(app),
        layout = ("grid", dict(row=0, column=position.increment(), pady=2))
    )

    ui.create_widget(
        "button", parent=parent, text="Copy", width=button_width,
        command=lambda: copy_output_to_clipboard(app),
        layout = ("grid", dict(row=0, column=position.increment(), pady=2))
    )

    ui.create_widget(
        "button", parent=parent, text="Paste", width=button_width,
        command=lambda: paste_from_clipboard(app),
        layout = ("grid", dict(row=0, column=position.increment(), pady=2))
    )

    ui.create_widget(
        "button", parent=parent, text="Clear", width=button_width,
        command=lambda: reset_textarea(app),
        layout = ("grid", dict(row=0, column=position.increment(), pady=2))
    )

    sep = ui.ttk.Separator(parent, orient="vertical")
    sep.grid(row=0, column=position.increment(), sticky="ns", padx=2, pady=2)

    ui.create_widget(
        "button", parent=parent, text="Reword", width=button_width,
        command=lambda: perform_reword(app),
        layout = ("grid", dict(row=0, column=position.increment(), pady=2))
    )

    sep = ui.ttk.Separator(parent, orient="vertical")
    sep.grid(row=0, column=position.increment(), sticky="ns", padx=2, pady=2)

    ui.create_widget(
        "button", parent=parent, text="Weave", width=button_width,
        command=lambda: comparison.show_diff(app, "interleave"),
        layout=("grid", dict(row=0, column=position.increment(), pady=2))
    )

    ui.create_widget(
        "button", parent=parent, text="Stack", width=button_width,
        command=lambda: comparison.show_diff(app, "stack"),
        layout=("grid", dict(row=0, column=position.increment(), pady=2))
    )

    ui.create_widget(
        "button", parent=parent, text="Pair", width=button_width,
        command=lambda: comparison.show_diff(app, "side-by-side"),
        layout=("grid", dict(row=0, column=position.increment(), pady=2))
    )


def import_file_to_input(app) -> None:
    """Open a file dialog and load selected file content into the user input textarea."""
    filetypes = [
        ("Text Files", "*.txt"),
        ("All Files", "*.*"),
    ]
    try:
        filename = ui.filedialog.askopenfilename(filetypes=filetypes)
        if not filename:
            return

        content = file.read(filename)
        app.user_textarea.delete("1.0", "end")
        app.user_textarea.insert("1.0", content)

    except Exception as ex:
        error = f"{type(ex).__name__}: {ex}"
        print(error)
        ui_helper.show_message_dialog(
            title="File Open Error",
            error=error,
        )

def export_output_to_file(app) -> None:
    """Open a save dialog and write output textarea content to the chosen file."""
    try:
        filename = ui.filedialog.asksaveasfilename()
        if not filename:
            return

        content = app.output_textarea.get("1.0", "end")
        # Strip trailing newline characters
        content = re.sub(r"\r?\n|\r$", "", content, count=1)

        file.write(filename, content)
    except Exception as ex:
        error = f"{type(ex).__name__}: {ex}",
        print(error)
        ui_helper.show_message_dialog(
            title="File Save Error",
            error=f"{type(ex).__name__}: {ex}",
        )


def copy_output_to_clipboard(app) -> None:
    """Copy the content of the output textarea to the system clipboard."""
    content = app.output_textarea.get("1.0", "end")
    # Remove trailing newline characters
    content = re.sub(r"\r?\n|\r$", "", content, count=1)

    app.root.clipboard_clear()
    app.root.clipboard_append(content)
    app.root.update()


def paste_from_clipboard(app) -> None:
    """Paste clipboard content into the user textarea, replacing existing text."""
    try:
        data = app.root.clipboard_get()
        if not data:
            return

        app.user_textarea.delete("1.0", "end")
        app.user_textarea.insert("1.0", data)

    except Exception as ex:
        error = f"{type(ex).__name__}: {ex}"
        print(error)
        ui_helper.show_message_dialog(
            title="Pasting Clipboard Error",
            error=error,
        )

def reset_textarea(app) -> None:
    """Clear both user input and output textarea."""
    app.user_textarea.delete("1.0", "end")

    app.output_textarea.config(state=ui.tk.NORMAL)
    app.output_textarea.delete("1.0", "end")
    app.output_textarea.config(state=ui.tk.DISABLED)


def perform_reword(app) -> None:
    """Rewrite user text and display the result in the output area."""
    text = ui_helper.extract_text(app.user_textarea)

    # Check for any non‑whitespace content
    if len(re.sub(r"\s+", "", text)) > 0:
        builder = RewordBuilder(text)

        app.output_textarea.config(state=ui.tk.NORMAL)
        app.output_textarea.delete("1.0", "end")
        app.output_textarea.insert("1.0", builder.rewritten)
        app.output_textarea.config(state=ui.tk.DISABLED)

    else:
        ui_helper.show_message_dialog(
            title="Reword Feature",
            info="Cannot rewrite empty content."
        )
