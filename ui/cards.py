"""
cards.py
--------
Reusable, polished UI building blocks for the recommendation panel:
cards, chips, colour swatches, confidence bars and tip rows.
"""

import customtkinter as ctk

from utils.config import COLORS, FONT_FAMILY, FONT_BOLD
from utils.colors import named_color_to_hex
from ui.theme import font, color


# ----------------------------------------------------------------------
# Card container
# ----------------------------------------------------------------------
class Card(ctk.CTkFrame):
    """A rounded card with a border, optional title bar and accent strip."""

    def __init__(self, master, title=None, icon=None, accent=None, **kwargs):
        kwargs.setdefault("fg_color", COLORS["card"])
        kwargs.setdefault("corner_radius", 14)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", COLORS["border"])
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        if title or icon:
            header = ctk.CTkFrame(self, fg_color="transparent")
            header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 4))
            header.grid_columnconfigure(1, weight=1)
            if icon:
                ctk.CTkLabel(header, text=icon, font=font(18)).grid(row=0, column=0, padx=(0, 8))
            label = ctk.CTkLabel(header, text=title or "", font=font(15, True),
                                 text_color=accent or COLORS["text"])
            label.grid(row=0, column=1, sticky="w")
            self._body = 1
        else:
            self._body = 0

    def body(self, **kwargs):
        """Start the body row and return an inner frame."""
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=self._body, column=0, sticky="ew", padx=16, pady=(2, 14))
        body.grid_columnconfigure(0, weight=1)
        return body


# ----------------------------------------------------------------------
# Text helpers
# ----------------------------------------------------------------------
def para(master, text, size=13, color_key="text_dim", **kwargs):
    """A wrapped paragraph label."""
    kwargs.setdefault("justify", "left")
    kwargs.setdefault("anchor", "w")
    return ctk.CTkLabel(master, text=text, font=font(size), text_color=COLORS[color_key],
                        wraplength=340, **kwargs)


def heading(master, text, size=16, text_color=None, **kwargs):
    return ctk.CTkLabel(master, text=text, font=font(size, True),
                        text_color=text_color or COLORS["text"], **kwargs)


# ----------------------------------------------------------------------
# Chips & swatches
# ----------------------------------------------------------------------
def chip(master, text, accent=None, size=12, padx=6, pady=5):
    """A small pill-shaped label."""
    return ctk.CTkLabel(
        master, text=text, font=font(size, True),
        text_color=accent or COLORS["accent_2"],
        fg_color=COLORS["bg_alt"], corner_radius=10,
        padx=padx, pady=pady,
    )


def swatch(master, label, width=34, height=34, dim=False):
    """A single colour swatch tile with its name below it."""
    hex_color = named_color_to_hex(label)
    frame = ctk.CTkFrame(master, fg_color="transparent", width=width + 8)
    tile = ctk.CTkFrame(frame, fg_color=hex_color, width=width, height=height,
                        corner_radius=9, border_width=1, border_color=COLORS["border"])
    tile.grid(row=0, column=0)
    name = ctk.CTkLabel(frame, text=label, font=font(9),
                        text_color=COLORS["text_dim"], width=width + 8)
    name.grid(row=1, column=0, pady=(3, 0))
    if dim:
        # overlay a translucent mask to show "avoid"
        overlay = ctk.CTkFrame(tile, fg_color="#10141C", width=width, height=height,
                               corner_radius=9)
        overlay.place(x=0, y=0)
        ctk.CTkLabel(overlay, text="✕", font=font(13, True), text_color=COLORS["danger"]).place(relx=0.5, rely=0.5, anchor="center")
    return frame


def swatch_row(master, names, dim=False, per_row=5):
    """A wrapping grid of colour swatches."""
    row = ctk.CTkFrame(master, fg_color="transparent")
    row.grid_columnconfigure(0, weight=1)
    for i, name in enumerate(names):
        s = swatch(row, name, dim=dim)
        col = i % per_row
        r = i // per_row
        s.grid(row=r, column=col, padx=3, pady=3)
    return row


# ----------------------------------------------------------------------
# Confidence bar
# ----------------------------------------------------------------------
class ConfidenceBar(ctk.CTkFrame):
    """A label + progress bar showing a confidence value."""

    def __init__(self, master, label, value, accent=COLORS["accent"], **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(1, weight=1)
        pct = max(0.0, min(1.0, value))
        ctk.CTkLabel(self, text=label, font=font(12), text_color=COLORS["text_dim"])\
            .grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(self, text=f"{pct * 100:.0f}%", font=font(12, True),
                     text_color=accent).grid(row=0, column=2, sticky="e", padx=(8, 0))
        bar = ctk.CTkProgressBar(self, progress_color=accent, fg_color=COLORS["bg_alt"],
                                 height=8, corner_radius=4)
        bar.set(pct)
        bar.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(4, 0))


def bullet(master, text, glyph="•", accent=COLORS["accent"]):
    """A single bullet line."""
    row = ctk.CTkFrame(master, fg_color="transparent")
    ctk.CTkLabel(row, text=glyph, font=font(13, True), text_color=accent).grid(row=0, column=0, sticky="nw")
    lbl = ctk.CTkLabel(row, text=text, font=font(12), text_color=COLORS["text"],
                       wraplength=310, justify="left", anchor="w")
    lbl.grid(row=0, column=1, sticky="w", padx=(6, 0))
    return row


def tip_row(master, emoji, text, active=False):
    """Guidance checklist row with active highlighting."""
    row = ctk.CTkFrame(master, fg_color=COLORS["bg_alt"] if active else "transparent",
                       corner_radius=10, border_width=1,
                       border_color=COLORS["accent"] if active else COLORS["border"])
    ctk.CTkLabel(row, text=emoji, font=font(15)).grid(row=0, column=0, padx=10, pady=6)
    ctk.CTkLabel(row, text=text, font=font(12, active),
                 text_color=COLORS["accent_2"] if active else COLORS["text_dim"],
                 anchor="w").grid(row=0, column=1, padx=(0, 10), pady=6, sticky="w")
    return row
