"""
theme.py
--------
CustomTkinter theme bootstrap: dark appearance and shared font helpers.
"""

import customtkinter as ctk

from utils.config import FONT_FAMILY, FONT_BOLD, COLORS


def setup():
    """Apply the global dark theme once, before creating any window."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def font(size, bold=False):
    """Return a font family string for CTk widgets."""
    family = FONT_BOLD if bold else FONT_FAMILY
    return (family, size)


def color(key):
    """Read a design-token colour by key."""
    return COLORS[key]
