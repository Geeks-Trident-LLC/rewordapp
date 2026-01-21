"""
rewordapp.ui.menu
-----------------

This module defines the menu bar and its submenus for the RewordApp CE GUI.

"""

import rewordapp.ui as ui
from rewordapp.ui import helper as ui_helper
from typing import Any


def create_menu_bar(parent: Any) -> ui.Menu:
    """Create and attach the main menu bar to the parent window."""
    menu_bar = ui.Menu(parent)
    parent.config(menu=menu_bar)
    return menu_bar


def add_file_menu(parent: ui.Menu, app: Any) -> ui.Menu:
    """Add a File menu with Open and Quit options to the menu bar."""
    file_menu = ui.Menu(parent)
    parent.add_cascade(menu=file_menu, label="File")

    file_menu.add_command(label="Open", command=app.show_file_open_dialog)
    file_menu.add_separator()
    file_menu.add_command(label="Quit", command=app.root.quit)

    return file_menu


def add_help_menu(parent: ui.Menu, app: Any) -> ui.Menu:
    """Add a Help menu with Documentation, Licenses, and About options to the menu bar."""
    help_menu = ui.Menu(parent)
    parent.add_cascade(menu=help_menu, label="Help")

    help_menu.add_command(
        label="Documentation",
        command=lambda: ui_helper.open_app_resource("documentation"),
    )
    help_menu.add_command(
        label="View Licenses",
        command=lambda: ui_helper.open_app_resource("license"),
    )
    help_menu.add_separator()
    help_menu.add_command(label="About", command=app.show_about_dialog)

    return help_menu