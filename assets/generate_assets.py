"""
generate_assets.py
------------------
Generates all PNG assets used by the application:
  * assets/icons/       — 9 flat category icons (96x96)
  * assets/glasses/     — 5 glasses style images (160x160)
  * assets/hairstyles/  — 5 hairstyle images (160x160)
  * assets/outfits/     — 5 occasion outfit images (160x160)

Run once:  py assets/generate_assets.py
Only the standard library + Pillow are required.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent
ICON_DIR = BASE / "icons"
GLASSES_DIR = BASE / "glasses"
HAIR_DIR = BASE / "hairstyles"
OUTFIT_DIR = BASE / "outfits"

for d in (ICON_DIR, GLASSES_DIR, HAIR_DIR, OUTFIT_DIR):
    d.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def canvas(size, bg=None):
    img = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def rounded_tile(draw, size, color, radius=22):
    draw.rounded_rectangle([4, 4, size - 4, size - 4], radius=radius, fill=color)


def star_points(cx, cy, outer, inner, n=5, rot=math.pi / 2):
    pts = []
    for i in range(n * 2):
        r = outer if i % 2 == 0 else inner
        a = rot + i * math.pi / n
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ----------------------------------------------------------------------
# Category icons
# ----------------------------------------------------------------------
def icon_dashboard(color):
    img, d = canvas(96)
    rounded_tile(d, 96, color)
    for gx, gy in ((30, 30), (66, 30), (30, 66), (66, 66)):
        d.rounded_rectangle([gx, gy, gx + 24, gy + 24], radius=7, fill="#10141C")
    return img


def icon_shirt(color):
    img, d = canvas(96)
    rounded_tile(d, 96, color)
    body = [(48, 28), (28, 36), (28, 48), (34, 52), (34, 66), (48, 70), (62, 66),
            (62, 52), (68, 48), (68, 36)]
    d.polygon(body, fill="#10141C")
    d.line([(28, 36), (40, 44), (48, 40)], fill="#10141C", width=4)
    d.line([(68, 36), (56, 44), (48, 40)], fill="#10141C", width=4)
    return img


def icon_glasses(color):
    img, d = canvas(96)
    rounded_tile(d, 96, color)
    d.ellipse([22, 40, 46, 62], outline="#10141C", width=4)
    d.ellipse([50, 40, 74, 62], outline="#10141C", width=4)
    d.line([(46, 51), (50, 51)], fill="#10141C", width=4)
    d.line([(22, 46), (14, 42)], fill="#10141C", width=4)
    d.line([(74, 46), (82, 42)], fill="#10141C", width=4)
    return img


def icon_scissors(color):
    img, d = canvas(96)
    rounded_tile(d, 96, color)
    d.ellipse([30, 26, 44, 40], outline="#10141C", width=5)
    d.ellipse([52, 26, 66, 40], outline="#10141C", width=5)
    d.line([(43, 39), (30, 62)], fill="#10141C", width=4)
    d.line([(53, 39), (66, 62)], fill="#10141C", width=4)
    d.ellipse([26, 56, 40, 70], outline="#10141C", width=4)
    d.ellipse([56, 56, 70, 70], outline="#10141C", width=4)
    return img


def icon_beard(color):
    img, d = canvas(96)
    rounded_tile(d, 96, color)
    # head
    d.ellipse([30, 22, 66, 60], outline="#10141C", width=4)
    # beard
    d.polygon([(32, 52), (64, 52), (58, 74), (48, 80), (38, 74)], fill="#10141C")
    return img


def icon_palette(color):
    img, d = canvas(96)
    rounded_tile(d, 96, color)
    d.ellipse([26, 26, 70, 70], outline="#10141C", width=5)
    for x, y, r in ((34, 38, 6), (48, 30, 6), (62, 40, 6), (50, 58, 6)):
        d.ellipse([x - r, y - r, x + r, y + r], fill="#10141C")
    return img


def icon_camera(color):
    img, d = canvas(96)
    rounded_tile(d, 96, color)
    d.rounded_rectangle([16, 32, 80, 66], radius=6, outline="#10141C", width=4)
    d.ellipse([38, 41, 58, 59], outline="#10141C", width=4)
    d.line([(66, 32), (60, 40)], fill="#10141C", width=4)
    d.ellipse([70, 36, 76, 42], fill="#10141C")
    return img


def icon_outfit(color):
    img, d = canvas(96)
    rounded_tile(d, 96, color)
    # shirt
    d.polygon([(48, 22), (30, 30), (30, 42), (36, 46), (36, 60), (48, 64), (60, 60),
               (60, 46), (66, 42), (66, 30)], fill="#10141C")
    # pants
    d.polygon([(36, 68), (60, 68), (58, 88), (52, 86), (48, 88), (42, 86)], fill="#10141C")
    return img


def icon_star(color):
    img, d = canvas(96)
    rounded_tile(d, 96, color)
    d.polygon(star_points(48, 50, 26, 11, 5), fill="#10141C")
    return img


# ----------------------------------------------------------------------
# Glasses images
# ----------------------------------------------------------------------
SKIN = (255, 224, 196, 255)
FRAME = (221, 231, 255, 255)


def _face_base(img, d):
    d.ellipse([34, 16, 126, 144], fill=SKIN)                 # head
    d.ellipse([58, 60, 70, 72], fill=(40, 40, 50, 255))      # eye
    d.ellipse([90, 60, 102, 72], fill=(40, 40, 50, 255))     # eye
    d.arc([58, 96, 102, 116], 20, 160, fill=(40, 40, 50, 255), width=4)  # smile
    return img


def glasses_round():
    img, d = canvas(160)
    _face_base(img, d)
    d.ellipse([44, 62, 76, 94], outline=FRAME, width=6)
    d.ellipse([84, 62, 116, 94], outline=FRAME, width=6)
    d.line([(76, 78), (84, 78)], fill=FRAME, width=6)
    return img


def glasses_rectangle():
    img, d = canvas(160)
    _face_base(img, d)
    d.rounded_rectangle([40, 64, 78, 94], radius=6, outline=FRAME, width=6)
    d.rounded_rectangle([82, 64, 120, 94], radius=6, outline=FRAME, width=6)
    d.line([(78, 79), (82, 79)], fill=FRAME, width=6)
    return img


def glasses_square():
    img, d = canvas(160)
    _face_base(img, d)
    d.rectangle([42, 62, 76, 96], outline=FRAME, width=6)
    d.rectangle([84, 62, 118, 96], outline=FRAME, width=6)
    d.line([(76, 79), (84, 79)], fill=FRAME, width=6)
    return img


def glasses_aviator():
    img, d = canvas(160)
    _face_base(img, d)
    for cx in (58, 102):
        d.line([(cx - 16, 62), (cx + 16, 62)], fill=FRAME, width=6)   # top bar
        d.arc([cx - 17, 62, cx + 17, 94], 10, 170, fill=FRAME, width=6)
        d.line([(cx - 17, 70), (cx - 13, 88)], fill=FRAME, width=6)
    d.line([(74, 62), (86, 62)], fill=FRAME, width=6)
    return img


def glasses_wayfarer():
    img, d = canvas(160)
    _face_base(img, d)
    d.polygon([(36, 64), (80, 60), (80, 94), (44, 98)], outline=FRAME, fill=(221, 231, 255, 40))
    d.polygon([(124, 64), (80, 60), (80, 94), (116, 98)], outline=FRAME, fill=(221, 231, 255, 40))
    d.line([(80, 60), (80, 98)], fill=FRAME, width=6)
    return img


# ----------------------------------------------------------------------
# Hairstyle images
# ----------------------------------------------------------------------
def hair_face():
    img, d = canvas(160)
    d.ellipse([34, 20, 126, 144], fill=SKIN)
    d.ellipse([58, 62, 70, 74], fill=(40, 40, 50, 255))
    d.ellipse([90, 62, 102, 74], fill=(40, 40, 50, 255))
    d.arc([58, 98, 102, 118], 20, 160, fill=(40, 40, 50, 255), width=4)
    return img, d


HAIR = (43, 43, 54, 255)
HAIR2 = (70, 70, 88, 255)


def hairstyle_crew():
    img, d = hair_face()
    d.rounded_rectangle([34, 22, 126, 46], radius=26, fill=HAIR)
    d.arc([30, 14, 130, 52], 200, 340, fill=HAIR, width=12)
    return img


def hairstyle_fade():
    img, d = hair_face()
    d.rounded_rectangle([34, 22, 126, 44], radius=26, fill=HAIR)
    d.rectangle([34, 44, 126, 60], fill=HAIR2)
    d.polygon([(34, 60), (126, 60), (126, 66), (34, 66)], fill=(90, 90, 112, 255))
    return img


def hairstyle_pompadour():
    img, d = hair_face()
    d.pieslice([22, 6, 138, 66], 200, 340, fill=HAIR)
    d.rounded_rectangle([34, 24, 126, 48], radius=24, fill=HAIR)
    d.arc([30, 4, 130, 50], 210, 330, fill=HAIR, width=14)
    return img


def hairstyle_undercut():
    img, d = hair_face()
    d.pieslice([26, 10, 134, 66], 200, 340, fill=HAIR)
    d.rounded_rectangle([34, 26, 126, 50], radius=20, fill=HAIR)
    d.polygon([(34, 50), (126, 50), (126, 58), (34, 58)], fill=(90, 90, 112, 255))
    return img


def hairstyle_side_part():
    img, d = hair_face()
    d.rounded_rectangle([34, 22, 126, 44], radius=24, fill=HAIR)
    d.line([(80, 22), (92, 44)], fill=SKIN, width=6)
    d.rounded_rectangle([34, 22, 84, 40], radius=20, fill=HAIR2)
    return img


# ----------------------------------------------------------------------
# Outfit images (occasion looks)
# ----------------------------------------------------------------------
def _person(d, shirt_color, is_formal=False, is_wedding=False):
    # head
    d.ellipse([64, 14, 96, 46], fill=SKIN)
    # torso (shirt)
    d.polygon([(48, 54), (112, 54), (118, 96), (42, 96)], fill=shirt_color)
    d.line([(80, 54), (80, 96)], fill=(255, 255, 255, 60), width=2)
    if is_formal:
        d.line([(80, 54), (80, 96)], fill=(255, 255, 255, 90), width=2)
        d.polygon([(70, 54), (80, 66), (90, 54)], fill=(255, 255, 255, 200))
    if is_wedding:
        d.polygon([(48, 54), (112, 54), (118, 90), (42, 90)], fill=shirt_color)
        d.polygon([(62, 54), (80, 70), (98, 54)], fill=(255, 255, 255, 230))
    # pants
    d.polygon([(52, 96), (76, 96), (74, 146), (58, 142), (56, 146)], fill=(28, 32, 42, 255))
    d.polygon([(84, 96), (108, 96), (104, 142), (102, 146), (86, 142)], fill=(28, 32, 42, 255))
    return d


def outfit_college():
    img, d = canvas(160)
    _person(d, (140, 150, 160, 255))
    return img


def outfit_interview():
    img, d = canvas(160)
    _person(d, (40, 52, 92, 255), is_formal=True)
    return img


def outfit_wedding():
    img, d = canvas(160)
    _person(d, (120, 90, 60, 255), is_wedding=True)
    return img


def outfit_party():
    img, d = canvas(160)
    _person(d, (26, 26, 32, 255))
    return img


def outfit_casual():
    img, d = canvas(160)
    _person(d, (42, 140, 138, 255))
    return img


# ----------------------------------------------------------------------
# Write everything
# ----------------------------------------------------------------------
def main():
    icons = {
        "icon_dashboard": icon_dashboard("#6C7CFF"),
        "icon_fashion": icon_shirt("#F06292"),
        "icon_glasses": icon_glasses("#4FC3F7"),
        "icon_hairstyle": icon_scissors("#BA68C8"),
        "icon_beard": icon_beard("#8D6E63"),
        "icon_palette": icon_palette("#FFB454"),
        "icon_selfie": icon_camera("#00D4AA"),
        "icon_outfit": icon_outfit("#FF8A65"),
        "icon_occasion": icon_star("#FFD54F"),
    }
    for name, img in icons.items():
        img.save(ICON_DIR / f"{name}.png")
        print("icon   ->", name)

    glasses = {
        "round": glasses_round,
        "rectangle": glasses_rectangle,
        "square": glasses_square,
        "aviator": glasses_aviator,
        "wayfarer": glasses_wayfarer,
    }
    for name, fn in glasses.items():
        fn().save(GLASSES_DIR / f"{name}.png")
        print("glasses ->", name)

    hairstyles = {
        "crew cut": hairstyle_crew,
        "fade": hairstyle_fade,
        "pompadour": hairstyle_pompadour,
        "undercut": hairstyle_undercut,
        "side part": hairstyle_side_part,
    }
    for name, fn in hairstyles.items():
        fn().save(HAIR_DIR / f"{name.replace(' ', '_')}.png")
        print("hair ->", name)

    outfits = {
        "college": outfit_college,
        "interview": outfit_interview,
        "wedding": outfit_wedding,
        "party": outfit_party,
        "casual": outfit_casual,
    }
    for name, fn in outfits.items():
        fn().save(OUTFIT_DIR / f"{name}.png")
        print("outfit ->", name)

    print("\nAll assets generated successfully.")


if __name__ == "__main__":
    main()
