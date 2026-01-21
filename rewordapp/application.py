"""
rewordapp.application
---------------------

This module defines the core Application class for RewordApp CE.

The Application class serves as the entry point for the RewordApp CE GUI,
coordinating UI components from `ui.menu`, `ui.about`, and `ui.helper`.
"""

from regexapp.deps import genericlib_ensure_tkinter_available as ensure_tkinter_available

tk = ensure_tkinter_available(app_name="Rewordapp")

from typing import Optional

from tkinter import filedialog

import rewordapp.ui.helper as ui_helper
import rewordapp.ui.about as ui_about
import rewordapp.ui.menu as ui_menu


class Application:
    """Main class for initializing and running the RewordApp CE GUI."""

    def __init__(self) -> None:
        """Initialize the root window and build the menu bar."""
        self.root = tk.Tk()
        self.root.title("RewordApp CE")
        self.root.geometry("800x600+100+100")
        self.root.minsize(200, 200)
        self.root.option_add("*tearOff", False)

        self._init_menu_bar()

    def _init_menu_bar(self) -> None:
        """Create and attach the main menu bar with File and Help menus."""
        menu_bar = ui_menu.create_menu_bar(self.root)
        ui_menu.add_file_menu(menu_bar, self)
        ui_menu.add_help_menu(menu_bar, self)

    def show_file_open_dialog(self) -> Optional[str]:
        """Open a file selection dialog and display a placeholder message."""
        filetypes = [
            ("Text Files", "*.txt"),
            ("All Files", "*.*"),
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            ui_helper.show_message_dialog(
                title="File Selected",
                info=(
                    f"You selected: {filename}\n\n"
                    "File opening is not yet implemented in this preview build. "
                    "Support for loading and editing files will be "
                    "available in a future release."
                ),
            )
        return filename

    def show_about_dialog(self) -> None:
        """Display the About dialog with panels for app info,
        repository, dependencies, and license."""
        about = ui_about.create_window(self.root)

        top_frame = ui_about.create_main_frame(about)
        paned_window = ui_about.create_panel_window(top_frame)

        # Main panel
        frame = ui_about.add_main_panel(paned_window)

        # Repository section
        ui_about.add_repository_link(frame)

        # Dependencies section
        ui_about.add_dependency_panel(frame)

        # License section
        ui_about.add_license_panel(paned_window)

        # Footer section
        ui_about.create_footer(paned_window)

        ui_helper.make_modal(about)

    def run(self) -> None:
        """Start the main application loop."""
        self.root.mainloop()


def execute():
    """Initialize and run the RewordApp CE application."""
    app = Application()
    app.run()
