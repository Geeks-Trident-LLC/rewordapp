"""
rewordapp.ui.output
-------------------

This module defines the output UI components for RewordApp CE.

Responsibilities include:
- Building the output frame that displays processed text results.
- Providing a scrollable textarea for viewing application output.
- Attaching vertical and horizontal scrollbars to ensure smooth navigation.
- Linking the output widget to the main application state for updates.
"""

import rewordapp.ui as ui


def build_output_frame(parent, app):
    """Create the output frame and attach a scrollable textarea for displaying results."""
    frame = ui.create_widget(
        "frame", parent=parent, width=600, height=350, relief=ui.tk.RIDGE
    )
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    _add_textarea_with_scrollbars(frame, app)
    return frame


def _add_textarea_with_scrollbars(parent, app):
    """Insert a textarea with vertical and horizontal scrollbars into the given frame."""
    textarea = ui.create_widget(
        "textarea",
        parent=parent,
        width=20,
        height=20,
        wrap="none",
        layout=("grid", {"row": 0, "column": 0, "sticky": "nswe"}),
    )
    textarea.config(state=ui.tk.DISABLED)

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
    app.output_textarea = textarea
