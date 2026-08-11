"""
colors.py
---------
Lookup table mapping colour names used in recommendations to hex values,
so the UI can render attractive colour swatches for every suggestion.
"""

COLOR_HEX = {
    # Neautrals
    "Black": "#16181D",
    "White": "#F7F7F7",
    "Grey": "#9AA3AF",
    "Grey chinos": "#A6ADB8",
    "Dark Grey": "#4A4F57",
    "Light Grey": "#D3D7DC",
    "Charcoal": "#36404C",
    "Beige": "#E3D4B8",
    "Cream": "#F5EBDD",
    "Brown": "#6E4A2F",
    "Tan": "#C19A6B",
    "Ashy Grey": "#8A8F98",
    "Dusty Grey": "#7E8894",
    "Muted Earth Tones": "#7A6A55",
    # Blues
    "Navy": "#1F2E56",
    "Royal Blue": "#2456C4",
    "Cobalt Blue": "#2B4FDB",
    "Sky Blue": "#7BC7F2",
    "Light Blue": "#9CC9F5",
    "Powder Blue": "#B8D4EE",
    "Denim Blue": "#5A7FB4",
    "Deep Royal Blue": "#1D3F8F",
    "Teal": "#1C8A87",
    "Turquoise": "#2EC4B6",
    # Greens
    "Emerald": "#0E9B63",
    "Emerald Green": "#0E9B63",
    "Olive": "#7A8036",
    "Olive Green": "#7A8036",
    "Forest Green": "#23543B",
    "Mint": "#A8E6CF",
    "Lime Green": "#9BD12A",
    "Toxic Green": "#66FF00",
    "Vivid Green": "#21D07A",
    # Reds / pinks
    "Red": "#D62839",
    "Bright Red": "#E63946",
    "Crimson": "#B0122B",
    "Maroon": "#6E1B2C",
    "Burgundy": "#7B1E3A",
    "Wine Red": "#722F45",
    "Hot Pink": "#FF3D81",
    "Soft Pink": "#F5A9BC",
    "Pastel Pink": "#F6C6D8",
    "Peach": "#FFCBA4",
    # Yellows / oranges
    "Yellow": "#FFD23F",
    "Mustard": "#D9A521",
    "Mustard Yellow": "#D9A521",
    "Gold": "#D4AF37",
    "Neon Yellow": "#E6FF00",
    "Bright Orange": "#FF8C42",
    "Muddy Orange": "#B8772E",
    # Misc
    "Beige": "#E3D4B8",
    "Faded Grey": "#B8BFC9",
    "Faded Denim": "#7E9CBC",
    "Washed-out Beige": "#DDD3BC",
    "Very Pale Pastels": "#EADDF0",
    "Dark Brown on Black": "#3B2E24",
    "Navy on Black": "#1F2E56",
    "Dull Khaki": "#A69B7B",
    "Muddy Brown": "#6E5840",
}

_DEFAULT_HEX = "#8A93A5"


def named_color_to_hex(name):
    """Return a hex string for a colour name (fallback: neutral grey)."""
    return COLOR_HEX.get(name, _DEFAULT_HEX)


def hex_to_rgb(hx):
    """Convert '#RRGGBB' to an (r, g, b) tuple."""
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))
