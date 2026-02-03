"""
rewordapp.main
=============
Entry-point logic for the rewordapp project.

This module defines the console interface and supporting functions
for running RewordApp. It configures command-line options, handles
version and dependency reporting, and provides the ability to launch
the graphical interface.
"""

import argparse

from rewordapp.deps import genericlib_sys_exit as sys_exit
from rewordapp.deps import genericlib_decorate_list_of_line as decorate_list_of_line

from rewordapp.application import Application


def run_gui_application(options):
    """Run the RewordApp GUI if `options.gui` is True.

    Parameters
    ----------
    options : argparse.Namespace
        Parsed CLI arguments containing the `gui` flag.
    """
    if options.gui:
        app = Application()
        app.run()
        sys_exit(success=True)


def show_dependency(options):
    """Display RewordApp dependency information if `options.dependency` is True.

    Parameters
    ----------
    options : argparse.Namespace
        Parsed CLI arguments containing the `dependency` flag.
    """
    if options.dependency:
        from platform import uname
        from platform import python_version
        import rewordapp.config as config

        os_name = uname().system
        os_release = uname().release
        py_ver = python_version()
        lst = [
            config.main_app_text,
            f'Platform: {os_name} {os_release} - Python {py_ver}',
            '--------------------',
            'Dependencies:'
        ]

        for pkg in config.get_dependency().values():
            lst.append(f'  + Package: {pkg["package"]}')
            lst.append(f'             {pkg["url"]}')

        msg = decorate_list_of_line(lst)
        sys_exit(success=True, msg=msg)

def show_version(options):
    """Display the current RewordApp version if `options.version` is True.

    Parameters
    ----------
    options : argparse.Namespace
        Parsed CLI arguments containing the `version` flag.
    """
    if options.version:
        from rewordapp import version
        sys_exit(success=True, msg=f"rewordapp {version}")


class Cli:
    """Command-line interface handler for RewordApp.

    Parses arguments, validates flags, and dispatches actions such as
    showing version, listing dependencies, or launching the GUI.
    """

    def __init__(self):

        parser = argparse.ArgumentParser(
            prog='rewordapp',
            usage='%(prog)s [options]',
            description=(
                "RewordApp is a versatile text transformation utility. "
                "It provides both command-line and GUI interfaces for "
                "rewriting, obfuscating, or rephrasing text to support "
                "secure collaboration, testing, and automation workflows."
            ),
        )

        parser.add_argument(
            '--gui', action='store_true',
            help=(
                "Launch the graphical interface for interactive text "
                "rewriting and configuration. Ideal for users who prefer "
                "a visual workflow over command-line options."
            )
        )

        parser.add_argument(
            '-d', '--dependency', action='store_true',
            help="Display the list of packages required by RewordApp"
        )

        parser.add_argument(
            '-v', '--version', action='store_true',
            help="Display the installed RewordApp version and exit"
        )

        self.parser = parser
        self.options = self.parser.parse_args()
        self.kwargs = dict()

    def validate_cli_flags(self, options):
        """Validate parsed CLI flags.

        Parameters
        ----------
        options : argparse.Namespace
            Parsed command-line arguments to check for active flags.

        Returns
        -------
        bool
            True if at least one flag is set; otherwise prints help and exits.
        """

        chk = any(bool(i) for i in vars(options).values())

        if not chk:
            self.parser.print_help()
            sys_exit(success=True)

        return True

    def run(self):
        """Process CLI arguments and execute actions.

        Parses command-line options, validates flags, and dispatches
        tasks such as showing version, listing dependencies, or
        launching the GUI.
        """
        options = self.parser.parse_args()
        show_version(self.options)
        show_dependency(self.options)
        self.validate_cli_flags(options)
        run_gui_application(options)


def execute():
    """Initialize and run the RewordApp CLI entry point.

    Creates a Cli instance, parses arguments, and dispatches actions.
    """
    app = Cli()
    app.run()
