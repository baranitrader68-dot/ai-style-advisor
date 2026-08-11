"""
icons.py
--------
Icon loading for the UI. Tries to load a generated PNG icon from
assets/icons/ and falls back to an emoji label if the file is missing.
"""

from pathlib import Path

from PIL import Image
import customtkinter as ctk

from utils.config import ICONS_DIR


def icon_path(name: str) -> Path:
    """Absolute path of an icon PNG inside assets/icons/."""
    return ICONS_DIR / f"{name}.png"


def load_icon(name: str, size: int = 22):
    """Return a CTkImage for an icon, or None if it does not exist."""
    path = icon_path(name)
    if path.exists():
        image = Image.open(path)
        return ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))
    return None


def item_image(folder: str, name: str, size: int = 90):
    """
    Load a recommendation-item image from assets/<folder>/<name>.png
    (e.g. glasses/round.png). Returns a CTkImage or None.
    """
    path = Path("assets") / folder / f"{name.lower().replace(' ', '_')}.png"
    if path.exists():
        image = Image.open(path)
        return ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))
    return None
