import platform

import tkinter as tk
from tkinter import ttk


is_macos = platform.system() == 'Darwin'
is_linux = platform.system() == 'Linux'
is_window = platform.system() == 'Windows'


Tk = tk.Tk

Toplevel = tk.Toplevel

Frame = ttk.Frame
PanedWindow = ttk.PanedWindow

LabelFrame = ttk.LabelFrame
Label = ttk.LabelFrame

Button = ttk.Button

TextBox = ttk.Entry
TextArea = tk.Text

Scrollbar = ttk.Scrollbar

RadioButton = tk.Radiobutton if is_linux else ttk.Radiobutton
CheckBox = tk.Checkbutton if is_linux else ttk.Checkbutton

Menu = tk.Menu