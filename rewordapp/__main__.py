"""'
rewordapp.__main__
=================
Entry point module for rewordapp.

This module provides the command-line interface (CLI) entry point
for rewordapp. When executed as a script (e.g., via
``python -m rewordapp``), it initializes the CLI application and
invokes its main runtime loop.
"""

from rewordapp.main import Cli

console = Cli()
console.run()
