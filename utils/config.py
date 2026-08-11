"""
config.py
---------
Central configuration for the AI Smart Style Advisor application.

Holds design tokens (colors, fonts), category metadata used by the
dashboard and recommendation panel, and the file-system layout of the
project (assets, icons, models, ...).
"""

from pathlib import Path

# ----------------------------------------------------------------------
# Application identity
# ----------------------------------------------------------------------
APP_NAME = "AI Smart Style Advisor"
APP_TAGLINE = "Style suggestions based on visual features only"

# ----------------------------------------------------------------------
# Project layout (relative to this file)
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
HAIRSTYLES_DIR = ASSETS_DIR / "hairstyles"
GLASSES_DIR = ASSETS_DIR / "glasses"
OUTFITS_DIR = ASSETS_DIR / "outfits"

# MediaPipe Face Landmarker model (downloaded separately, see README)
FACE_LANDMARK_MODEL = MODELS_DIR / "face_landmarker.task"

# ----------------------------------------------------------------------
# Design tokens — modern dark theme
# ----------------------------------------------------------------------
COLORS = {
    "bg": "#0B0E14",          # window background
    "bg_alt": "#0F141D",      # subtle alternate background
    "panel": "#151A23",       # panels / sidebars
    "card": "#1B2230",        # card surfaces
    "card_hover": "#232D40",  # card hover state
    "border": "#2A3346",      # borders / dividers
    "text": "#EAF0F6",        # primary text
    "text_dim": "#93A3B8",    # secondary text
    "accent": "#6C7CFF",      # primary accent (indigo)
    "accent_2": "#00D4AA",    # secondary accent (teal)
    "warn": "#FFB454",        # warnings / guidance
    "danger": "#FF6B6B",      # errors / alerts
    "info": "#4FC3F7",        # information
    "success": "#4CD98F",     # success / "perfect" states
}

FONT_FAMILY = "Segoe UI"
FONT_BOLD = "Segoe UI Semibold"

# ----------------------------------------------------------------------
# Recommendation categories
#
# key      -> (title, subtitle, emoji, accent_color, image_name)
# image_name is the icon file name inside assets/icons/ (with .png).
# ----------------------------------------------------------------------
CATEGORIES = {
    "dashboard": ("Dashboard", "Live overview of your analysis", "📊", COLORS["accent"], "icon_dashboard"),
    "fashion":   ("AI Fashion Advisor", "Shirt & outfit colour ideas", "👕", "#F06292", "icon_fashion"),
    "glasses":   ("AI Glasses Recommender", "Frames for your face shape", "🕶️", "#4FC3F7", "icon_glasses"),
    "hairstyle": ("AI Hairstyle Advisor", "Cuts that suit your face", "💇", "#BA68C8", "icon_hairstyle"),
    "beard":     ("AI Beard Style Advisor", "Facial hair ideas", "🧔", "#8D6E63", "icon_beard"),
    "palette":   ("AI Color Palette Advisor", "Colours for your skin tone", "🎨", "#FFB454", "icon_palette"),
    "selfie":    ("AI Selfie Assistant", "Get the perfect camera position", "📸", "#00D4AA", "icon_selfie"),
    "outfit":    ("AI Outfit Matcher", "Pair pants & shoes with a shirt", "🧥", "#FF8A65", "icon_outfit"),
    "occasion":  ("AI Occasion Look", "Looks for every event", "✨", "#FFD54F", "icon_occasion"),
}

# Ordered navigation list (dashboard first)
CATEGORY_ORDER = [
    "dashboard", "fashion", "glasses", "hairstyle",
    "beard", "palette", "selfie", "outfit", "occasion",
]

# Face shapes the system can approximate
FACE_SHAPES = ["Oval", "Round", "Square", "Rectangle", "Heart", "Diamond"]

# Skin tone categories
SKIN_TONES = ["Fair", "Light", "Medium", "Tan", "Deep"]

# ----------------------------------------------------------------------
# Camera / analysis defaults
# ----------------------------------------------------------------------
DEFAULT_CAMERA_INDEX = 0
UI_REFRESH_MS = 50                 # ~20 FPS UI refresh (light on the Tk thread)
LIVE_REFRESH_MS = 1000             # refresh of "live" recommendation cards
