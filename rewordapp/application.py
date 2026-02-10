"""
rewordapp.application
---------------------

This module defines the core Application class for RewordApp CE.

The Application class serves as the entry point for the RewordApp CE GUI,
coordinating UI components from `ui.menu`, `ui.about`, and `ui.helper`.
"""

from regexapp.deps import genericlib_ensure_tkinter_available as ensure_tkinter_available

tk = ensure_tkinter_available(app_name="Rewordapp")

import rewordapp.ui as ui
import rewordapp.ui.menu as ui_menu
import rewordapp.ui.about as ui_about
import rewordapp.ui.helper as ui_helper
import rewordapp.ui.user as ui_user
import rewordapp.ui.output as ui_output
import rewordapp.ui.controls as ui_controls
import rewordapp.ui.logo as ui_logo


class Application:
    """Main class for initializing and running the RewordApp CE GUI."""

    def __init__(self) -> None:
        """Initialize the root window and build the menu bar."""
        self.root = tk.Tk()
        self.root.title("RewordApp CE")
        self.root.geometry("800x600+100+100")
        self.root.minsize(200, 200)
        self.root.option_add("*tearOff", False)

        # Tkinter widgets for main layout
        self.main_paned_window = None   # container holding input, controls, and output frames

        self.user_frame = None         # frame containing the user input textarea
        self.user_textarea = None

        self.controls_frame = None      # frame containing action buttons to process text

        self.output_frame = None        # frame containing the output textarea
        self.output_textarea = None

        self.rules = ""

        # load icon logo
        ui_logo.set_window_icon(self.root)

        # methods call
        self._init_menu_bar()
        self._init_main_frames()

    def _init_menu_bar(self) -> None:
        """Create and attach the main menu bar with File and Help menus."""
        menu_bar = ui_menu.create_menu_bar(self.root)
        ui_menu.add_file_menu(menu_bar, self)
        ui_menu.add_help_menu(menu_bar, self)

    def _init_main_frames(self) -> None:
        """Initialize and arrange the main frames in the application window."""
        paned_window = ui.create_widget(
            "panedwindow", parent=self.root, orient=tk.VERTICAL,
            layout=("pack", dict(fill=tk.BOTH, expand=True, padx=2, pady=2))
        )

        self.user_frame = ui_user.build_input_frame(paned_window, self)

        self.controls_frame = ui_controls.build_controls_frame(paned_window, self)  # noqa

        self.output_frame = ui_output.build_output_frame(paned_window, self)

        paned_window.add(self.user_frame, weight=4)
        paned_window.add(self.controls_frame)
        paned_window.add(self.output_frame, weight=5)

        self.main_paned_window = paned_window

    def show_about_dialog(self) -> None:
        """Display the About dialog with panels for app info,
        repository, dependencies, and license."""
        about = ui_about.create_window(self.root)

        # load icon logo
        ui_logo.set_window_icon(about)

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
