"""
rewordapp.ui.user
=================

This module defines the user-facing UI components for RewordApp CE.

Responsibilities include:
- Building frames and panels that capture user input.
- Providing text areas with scrollbars for entering and editing content.
- Attaching controls and layout options to ensure a responsive interface.
- Linking user input widgets to the main application state for processing.

"""

import rewordapp.ui as ui


def build_input_frame(parent, app):
    """Create the input frame with a textarea and attach it to the parent container."""
    frame = ui.create_widget(
        "frame", parent=parent, width=600, height=300, relief=ui.tk.RIDGE
    )
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    _add_textarea_with_scrollbars(frame, app)
    return frame


def _add_textarea_with_scrollbars(parent, app):
    """Add a textarea widget with vertical and horizontal scrollbars to the parent frame."""
    textarea = ui.create_widget(
        "textarea",
        parent=parent,
        width=20,
        height=20,
        wrap="none",
        layout=("grid", {"row": 0, "column": 0, "sticky": "nswe"}),
    )

    vscrollbar = ui.create_widget(
        "scrollbar",
        parent=parent,
        orient=ui.tk.VERTICAL,
        command=textarea.yview,
        layout=("grid", {"row": 0, "column": 1, "sticky": "ns"}),
    )

    hscrollbar = ui.create_widget(
        "scrollbar",
        parent=parent,
        orient=ui.tk.HORIZONTAL,
        command=textarea.xview,
        layout=("grid", {"row": 1, "column": 0, "sticky": "ew"}),
    )

    textarea.config(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
    app.user_textarea = textarea
