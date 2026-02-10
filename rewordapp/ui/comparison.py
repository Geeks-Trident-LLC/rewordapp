"""
rewordapp.ui.comparison
-----------------------

Comparison dialog UI for original and rewritten text.
"""

from rewordapp.ui import helper as ui_helper
import rewordapp.ui.weave as weave


def show_diff(app, mode):
    """Validate text state and open the appropriate diff dialog."""
    mode = str(mode).lower()

    # Extract normalized text
    user_text = ui_helper.extract_text(app.user_textarea)
    rewritten_text = ui_helper.extract_text(app.output_textarea)

    user_len = len(user_text)
    out_len = len(rewritten_text)

    # Ready to compare: lengths match but content differs
    if user_len == out_len and user_text != rewritten_text:
        if mode == "weave":
            weave.show_interleave(app, user_text, rewritten_text)
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