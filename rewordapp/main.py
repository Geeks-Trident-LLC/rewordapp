"""
rewordapp.main
=============
Main entry point for RewordApp's command‑line interface.

"""

import argparse

from rewordapp.libs import file
from rewordapp.libs.common import sys_exit
from rewordapp.libs.common import decorate_list_of_line

from rewordapp.core import RewordBuilder

from rewordapp.application import Application


def run_gui_application(options):
    """Launch the RewordApp GUI when the --gui flag is enabled."""
    if not options.gui:
        return

    app = Application()
    app.run()
    sys_exit(success=True)


def show_dependencies(options):
    """Display RewordApp dependency information when the --dependency flag is enabled."""
    if not options.dependency:
        return

    from platform import uname, python_version
    import rewordapp.config as config

    system = uname()
    python_ver = python_version()

    lines = [
        config.main_app_text,
        f"Platform: {system.system} {system.release} - Python {python_ver}",
        "--------------------",
        "Dependencies:",
    ]

    for pkg in config.get_dependency().values():
        lines.append(f"  + Package: {pkg['package']}")
        lines.append(f"             {pkg['url']}")

    message = decorate_list_of_line(lines)
    sys_exit(success=True, msg=message)

def show_version(options):
    """Print the installed RewordApp version and exit if requested."""
    if not options.version:
        return

    from rewordapp import version
    sys_exit(success=True, msg=f"rewordapp {version}")


def run_rewrite(options):
    """Rewrite input text using the provided rules and output settings."""

    if not options.data_file:
        return
    try:
        builder = RewordBuilder(
            data_file=options.data_file,
            rule_file=options.rule_file
        )
        if builder:
            rewrite_content = builder.rewritten

            # Write output to file or print to console
            if options.output_file or options.save_rule_file:
                if options.show_header:
                    print(decorate_list_of_line([f"{'Save File(s)':<20}"]))
                if options.save_rule_file:
                    file.write(options.save_rule_file, builder.rules.text_with_rule_docs)
                    print(f"+++ Rewrite rule has been saved "
                          f"to {options.save_rule_file!r}.")

                if options.output_file:
                    file.write(options.output_file, builder.rewritten)
                    print(f"+++ Rewritten content has been saved "
                          f"to {options.output_file!r}.")

                sys_exit(success=True)

            if options.show_rules:
                if options.show_header:
                    print(decorate_list_of_line([f"{'Rewrite Rules':<20}"]))
                print(f"{builder.rules.text_with_rule_docs}\n")

            if options.show_data:
                if options.show_header:
                    print(decorate_list_of_line([f"{'Raw Data':<20}"]))
                print(f"{builder.raw}\n")

            if not options.output_file:
                if options.show_header:
                    print(decorate_list_of_line([f"{'Rewrite Content':<20}"]))
                print(f"{rewrite_content}")

            sys_exit(success=True)

        sys_exit(success=False, msg=f">>> data_file does not have any content.")

    except Exception as ex:
        sys_exit(success=False, msg=f">>> {type(ex).__name__}: {ex}")


class Cli:
    """Command-line interface handler for RewordApp."""

    def __init__(self):
        """Initialize the CLI parser and load command‑line options."""
        parser = argparse.ArgumentParser(
            prog="rewordapp",
            usage="%(prog)s [options]",
            description=(
                "RewordApp is a versatile text‑transformation utility providing both "
                "command‑line and GUI interfaces for rewriting, obfuscating, or "
                "rephrasing text to support secure collaboration, testing, and "
                "automation workflows."
            ),
        )

        parser.add_argument(
            "--gui",
            action="store_true",
            help=(
                "Launch the graphical interface for interactive text rewriting and "
                "configuration. Ideal for users who prefer a visual workflow."
            ),
        )

        parser.add_argument(
            "-f", "--data-file",
            type=str,
            default="",
            help="Path to the input data file used for rewrite processing.",
        )

        parser.add_argument(
            "-r", "--rule-file",
            type=str,
            default="",
            help=(
                "Path to the rewrite rule file (dictionary‑style YAML) "
                "that defines the rewriting behavior."
            )
        )

        parser.add_argument(
            "--show-data",
            action="store_true",
            help="Display the content of the date file."
        )

        parser.add_argument(
            "--show-rules",
            action="store_true",
            help="Display the rewrite rules in the console after rewriting."
        )

        parser.add_argument(
            "--show-header",
            action="store_true",
            help="Display a header above the output."
        )

        parser.add_argument(
            "-o", "--output-file",
            type=str,
            default="",
            help="Path to the file where rewritten content will be saved.",
        )

        parser.add_argument(
            "--save-rule-file",
            type=str,
            default="",
            help="Path to the file where rewrite rules will be saved.",
        )

        parser.add_argument(
            "--dependency",
            action="store_true",
            help="Display the list of packages required by RewordApp.",
        )

        parser.add_argument(
            "-v", "--version",
            action="store_true",
            help="Display the installed RewordApp version and exit.",
        )

        self.parser = parser
        self.options = parser.parse_args()
        self.kwargs = {}

    def validate_cli_flags(self, options):
        """Ensure at least one CLI flag is provided; otherwise show help and exit."""
        has_flag = any(bool(value) for value in vars(options).values())

        if not has_flag:
            self.parser.print_help()
            sys_exit(success=True)

        return True

    def run(self):
        """Process CLI arguments, validate flags, and dispatch CLI actions."""
        options = self.parser.parse_args()

        show_version(options)
        show_dependencies(options)
        self.validate_cli_flags(options)
        run_gui_application(options)
        run_rewrite(options)


def execute():
    """Start the RewordApp CLI by creating and running the main controller."""
    cli = Cli()
    cli.run()
