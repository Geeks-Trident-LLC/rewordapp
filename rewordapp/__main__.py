"""'
rewordapp.__main__
=================
Entry point module for rewordapp.

This module provides the command-line interface (CLI) entry point
for rewordapp. When executed as a script (e.g., via
``python -m rewordapp``), it initializes the CLI application and
invokes its main runtime loop.

Features
--------
- Imports the `Cli` class from `rewordapp.main`.
- Instantiates a `Cli` object (`console`).
- Executes the CLI by calling `console.run()`.

Usage
-----
Run rewordapp directly from the command line:

    python -m rewordapp

This will launch the CLI interface, allowing users to interact
with rewordapp features such as pattern building, test script
generation, and reference management.

Notes
-----
- This module is intended to be executed, not imported.
- The CLI behavior is defined in `rewordapp.main.Cli`.
- Provides a convenient way to access rewordapp functionality
  without writing additional Python code.
"""

from rewordapp.main import Cli

console = Cli()
console.run()
