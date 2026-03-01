"""
rewordapp.ui.about
==================

This module defines the UI components for the "About" dialog in RewordApp CE.
"""

from typing import Any, Union

import tkinter as tk
from tkinter import ttk

import rewordapp.ui as ui
import rewordapp.ui.helper as ui_helper

import rewordapp.config as config


def create_window(
    parent: Union[ui.Tk, ui.Toplevel],
    width: int = 460,
    height: int = 480
) -> ui.Toplevel:
    """Create and center the About dialog window within the given parent."""
    about = ui.Toplevel(parent)
    about.title("About - RewordApp CE")
    ui_helper.center_window(parent, about, width, height)
    return about


def create_main_frame(
    parent: Union[ui.Tk, ui.Toplevel, ui.Frame]
) -> ui.Frame:
    """Create and pack a main frame that fills and expands within the given container."""
    frame = ui.Frame(parent)
    frame.pack(fill="both", expand=True)
    return frame


def create_panel_window(parent: Any) -> ttk.PanedWindow:
    """Create and pack a vertical PanedWindow inside the given parent widget."""
    paned_window = ui.PanedWindow(parent, orient="vertical")
    paned_window.pack(fill="both", expand=True, padx=8, pady=12)
    return paned_window


def add_main_panel(parent: ui.PanedWindow, width: int = 450, height: int = 20) -> ui.Frame:
    """Add the main application panel with a styled header label to a PanedWindow."""
    frame = ui.Frame(parent, width=width, height=height)
    parent.add(frame, weight=4)

    ui_helper.create_styled_label(
        frame, text=config.main_app_text + " " * 30,
        options=dict(foreground="navy", background="lightgray"),
        increased_size=8, bold=True, italic=True,
        layout=("grid", dict(row=0, column=0, columnspan=2, sticky="nwe"))
    )

    return frame


def add_repository_link(
    parent: ui.Frame,
    width: int = 450,
    height: int = 5
) -> None:
    """Add a repository link section with labels to the given container."""
    cell_frame = ui.Frame(parent, width=width, height=height)
    cell_frame.grid(row=1, column=0, sticky=tk.W, columnspan=2)

    ui_helper.create_styled_label(
        cell_frame, text="Repository:", bold=True,
        layout=("pack", dict(side=tk.LEFT))
    )
    ui_helper.create_styled_label(
        cell_frame, text=config.repo_url, link=config.repo_url,
        layout=("pack", dict(side=tk.LEFT))
    )


def add_dependency_panel(parent: Any) -> None:
    """Add a panel displaying PyPI dependencies with clickable package links."""
    ui_helper.create_styled_label(
        parent, text="PyPI Dependencies:", bold=True,
        layout=("grid", dict(row=2, column=0, sticky=tk.W))
    )

    row, column = 3, 0
    for pkg_name, pkg in config.get_dependency().items():
        ui_helper.create_styled_label(
            parent,
            text=pkg.get("package", pkg_name),
            link=pkg.get("url", ""),
            layout=("grid", dict(row=row, column=column % 2, padx=(20, 0), sticky=tk.W))
        )

        row += column % 2
        column += 1


def add_license_panel(
    parent: Union[tk.Tk, ui.Toplevel, ui.PanedWindow],
    width: int = 450,
    height: int = 200
) -> None:
    """Create a scrollable license_text panel and add it to the given container."""

    label_frame = ui.LabelFrame(
        parent, height=height, width=width, text=config.license_name
    )
    parent.add(label_frame, weight=7)

    # Adjust text area size based on platform
    text_width = 58 if ui.is_macos else 51
    text_height = 18 if ui.is_macos else 14 if ui.is_linux else 15

    text_area = ui.TextArea(label_frame, width=text_width, height=text_height, wrap="word")
    text_area.grid(row=0, column=0, padx=5, pady=5)

    scrollbar = ui.Scrollbar(label_frame, orient="vertical", command=text_area.yview)
    scrollbar.grid(row=0, column=1, sticky="nsew")

    text_area.config(yscrollcommand=scrollbar.set)
    text_area.insert(tk.INSERT, config.license_text)

    text_area.config(state="disabled")


def create_footer(
    parent: Union[ui.Tk, ui.Toplevel, ui.PanedWindow],
    width: int = 450,
    height: int = 20
) -> None:
    """Create and add a footer with copyright and company info to the given container."""
    frame = ui.Frame(parent, width=width, height=height)
    parent.add(frame, weight=1)

    ui_helper.create_styled_label(
        frame, text=config.copyright_text,
        layout=("pack", dict(side=tk.LEFT, pady=(10, 10))),
    )

    ui_helper.create_styled_label(
        frame, text=config.company, link=config.company_url,
        layout=("pack", dict(side=tk.LEFT, pady=(10, 10))),
    )

    ui_helper.create_styled_label(
        frame, text=".  All rights reserved.",
        layout=("pack", dict(side=tk.LEFT, pady=(10, 10))),
    )
