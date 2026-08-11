"""
recommendations.py
------------------
All style-recommendation rules for the 8 advisor modules.

Every recommendation is a *suggestion* based on visual features
(face shape, skin tone) and well-known, predefined fashion rules.
The system never claims to read personality, intelligence, character
or emotions from a face.
"""

from utils.config import SKIN_TONES, FACE_SHAPES

# ======================================================================
# 1. AI FASHION ADVISOR
# ======================================================================
SHIRT_COLORS = {
    "Fair": ["Navy", "Burgundy", "Emerald Green", "Deep Royal Blue", "Soft Pink", "Maroon"],
    "Light": ["Navy", "Olive Green", "Teal", "Charcoal", "Wine Red", "Powder Blue"],
    "Medium": ["Black", "Maroon", "Forest Green", "Royal Blue", "Beige", "Brown"],
    "Tan": ["White", "Crimson", "Mustard Yellow", "Teal", "Olive", "Navy"],
    "Deep": ["White", "Gold", "Royal Blue", "Emerald", "Hot Pink", "Bright Red"],
}

TSHIRT_COLORS = {
    "Fair": ["Sky Blue", "Mint", "Light Grey", "Navy", "Peach"],
    "Light": ["Teal", "Charcoal", "Olive", "Cobalt Blue", "Cream"],
    "Medium": ["Black", "Olive", "Maroon", "Grey", "Denim Blue"],
    "Tan": ["White", "Forest Green", "Mustard", "Black", "Burgundy"],
    "Deep": ["White", "Yellow", "Red", "Turquoise", "Vivid Green"],
}

FORMAL_OUTFITS = {
    "Fair": [
        "Navy two-piece suit + crisp white shirt + black leather oxfords",
        "Charcoal suit + light-blue shirt + burgundy silk tie",
        "Dark grey suit + white shirt + dark brown derby shoes",
    ],
    "Light": [
        "Navy suit + white shirt + black leather shoes",
        "Charcoal suit + pale-blue shirt + patterned tie",
        "Grey suit + light-grey shirt + brown oxfords",
    ],
    "Medium": [
        "Black suit + white shirt + black polished shoes",
        "Navy suit + light-grey shirt + oxblood loafers",
        "Charcoal suit + white shirt + dark derby shoes",
    ],
    "Tan": [
        "Charcoal suit + white shirt + black shoes",
        "Navy blazer + cream shirt + beige trousers + brown shoes",
        "Dark navy suit + white shirt + burgundy tie",
    ],
    "Deep": [
        "Navy suit + white shirt + black leather shoes",
        "Charcoal suit + white shirt + dark tie",
        "Black blazer + white shirt + black trousers",
    ],
}

CASUAL_OUTFITS = {
    "Fair": [
        "Light denim shirt + beige chinos + white sneakers",
        "Grey crew sweatshirt + dark jeans + canvas sneakers",
        "Blue Oxford shirt + olive chinos + loafers",
    ],
    "Light": [
        "Olive bomber jacket + white tee + dark jeans",
        "Navy polo + khaki chinos + white sneakers",
        "Checked flannel + denim jeans + boots",
    ],
    "Medium": [
        "Black tee + grey joggers + clean white sneakers",
        "Denim jacket + plain tee + chinos + trainers",
        "Maroon hoodie + black jeans + sneakers",
    ],
    "Tan": [
        "White tee + olive cargo pants + sneakers",
        "Burgundy polo + beige chinos + suede loafers",
        "Denim shirt + dark denim jeans + boots",
    ],
    "Deep": [
        "White tee + black jeans + bright sneakers",
        "Embroidered shirt + slim denim + loafers",
        "Mustard crew + dark chinos + white sneakers",
    ],
}

# ======================================================================
# 2. AI GLASSES RECOMMENDER
# ======================================================================
GLASSES = {
    "Oval": [
        ("Wayfarer", "Balanced oval faces carry classic wayfarers effortlessly."),
        ("Rectangle", "Adds a little structure without fighting the natural balance."),
        ("Aviator", "A timeless choice that follows the soft lines of the face."),
    ],
    "Round": [
        ("Rectangle", "Sharp, angular frames add definition to a soft face."),
        ("Square", "Strong corners help balance the curved face outline."),
        ("Geometric", "Angled shapes lengthen the appearance of a round face."),
    ],
    "Square": [
        ("Round", "Soft, circular frames soften a strong angular jawline."),
        ("Aviator", "Teardrop lenses relax the hard edges of the face."),
        ("Oval", "Gentle curves balance the width of a square jaw."),
    ],
    "Rectangle": [
        ("Round", "Rounded frames shorten a long face visually."),
        ("Oval", "Curved outlines break up the vertical length."),
        ("Oversized", "Larger lenses fill out the middle of a long face."),
    ],
    "Heart": [
        ("Aviator", "Frames with wider bottoms balance a narrow chin."),
        ("Wayfarer", "Classic shape directs attention away from the forehead."),
        ("Rimless", "Light, low frames avoid adding width up top."),
    ],
    "Diamond": [
        ("Oval", "Soft outlines soften prominent cheekbones."),
        ("Cat-eye", "Lifts and balances the cheekbone line."),
        ("Rimless", "Keeps focus on the cheekbones without adding bulk."),
    ],
}

# ======================================================================
# 3. AI HAIRSTYLE ADVISOR
# ======================================================================
HAIRSTYLES = {
    "Oval": [
        ("Pompadour", "The oval face is the most versatile — go bold."),
        ("Side Part", "A classic, clean look that always works."),
        ("Crew Cut", "Low-maintenance and neat."),
        ("Undercut", "Modern contrast with plenty of edge."),
    ],
    "Round": [
        ("Fade", "Tapered sides slim the face and add definition."),
        ("Pompadour", "Height on top lengthens a round face."),
        ("Undercut", "Sharp sides + volume on top balance the curves."),
        ("Quiff", "Adds vertical lift and angles."),
    ],
    "Square": [
        ("Crew Cut", "Short and clean, highlights a strong jaw."),
        ("Side Part", "Softens the square outline with structure."),
        ("Textured Crop", "Keeps the focus above the jawline."),
        ("Buzz Cut", "Bold, confident and very low maintenance."),
    ],
    "Rectangle": [
        ("Side Part", "Horizontal structure breaks up the length."),
        ("Textured Fringe", "Covers the forehead and shortens the face."),
        ("Comb Over", "Adds width on the sides."),
        ("Fringe", "Reduces visible forehead height."),
    ],
    "Heart": [
        ("Side Swept", "Softens the wide forehead."),
        ("Textured Fringe", "Balances a narrow chin."),
        ("Pompadour", "Works when the sides are kept tighter."),
        ("Slick Back", "Minimal sides, focus on the top."),
    ],
    "Diamond": [
        ("Side Part", "Softens the cheekbone emphasis."),
        ("Fringe", "Covers part of the forehead for balance."),
        ("Quiff", "Adds balance between forehead and jaw."),
        ("Medium Crop", "Keeps the width in the middle of the face."),
    ],
}

# ======================================================================
# 4. AI BEARD STYLE ADVISOR
# ======================================================================
BEARD_STYLES = {
    "Oval": [
        ("Clean Shave", "Perfectly complements an oval face."),
        ("Stubble", "Adds a subtle masculine texture."),
        ("Full Beard", "A fuller look that still suits the oval balance."),
    ],
    "Round": [
        ("Goatee", "Adds length to the lower face."),
        ("French Beard", "Draws the eye downward, slimming the face."),
        ("Short Boxed", "Keeps the sides tight and adds a defined chin."),
    ],
    "Square": [
        ("Stubble", "Softens the strong jawline slightly."),
        ("Full Beard", "Rounds out a prominent jaw for balance."),
        ("Short Boxed", "A clean, structured look for a square face."),
    ],
    "Rectangle": [
        ("Short Stubble", "Adds width without lengthening the face."),
        ("Full Beard", "Grows fuller on the sides to widen the face."),
        ("Chin Strap", "Defines the jaw while keeping length down."),
    ],
    "Heart": [
        ("Stubble", "Adds mass to the narrow chin area."),
        ("Goatee", "Strengthens a pointed chin."),
        ("Van Dyke", "Balances the wide forehead."),
    ],
    "Diamond": [
        ("Goatee", "Broadens a narrow chin."),
        ("French Beard", "Adds volume around the jawline."),
        ("Full Beard", "Fills out the lower face for balance."),
    ],
}

# ======================================================================
# 5. AI COLOR PALETTE ADVISOR
# ======================================================================
PALETTE = {
    "Fair": {
        "recommended": ["Navy", "Emerald", "Burgundy", "Pastel Pink", "Light Blue", "Charcoal"],
        "avoid": ["Neon Yellow", "Washed-out Beige", "Lime Green", "Muddy Orange"],
        "note": "Rich, deep tones add contrast and warmth to fair skin.",
    },
    "Light": {
        "recommended": ["Navy", "Olive", "Teal", "Wine Red", "Powder Blue", "Charcoal"],
        "avoid": ["Bright Orange", "Hot Pink", "Very Pale Pastels", "Mustard"],
        "note": "Mid-depth jewel tones flatter light complexions best.",
    },
    "Medium": {
        "recommended": ["Black", "Maroon", "Forest Green", "Royal Blue", "Beige", "Brown"],
        "avoid": ["Neon Colours", "Muddy Brown", "Faded Grey", "Toxic Green"],
        "note": "Warm earth tones and deep colours create a rich contrast.",
    },
    "Tan": {
        "recommended": ["White", "Crimson", "Teal", "Mustard", "Olive", "Navy"],
        "avoid": ["Very Pale Pastels", "Ashy Grey", "Dull Khaki", "Faded Denim"],
        "note": "High-contrast and warm colours make tan skin glow.",
    },
    "Deep": {
        "recommended": ["White", "Gold", "Royal Blue", "Emerald", "Bright Red", "Hot Pink"],
        "avoid": ["Dark Brown on Black", "Muted Earth Tones", "Dusty Grey", "Navy on Black"],
        "note": "Bold, vivid and luminous colours pop beautifully on deep skin.",
    },
}

# ======================================================================
# 7. AI OUTFIT MATCHER
#    (pants + shoes suggestions for a selected shirt colour)
# ======================================================================
SHIRT_COLOR_CHOICES = [
    "Black", "White", "Navy", "Grey", "Beige", "Olive",
    "Maroon", "Burgundy", "Royal Blue", "Emerald", "Mustard",
]

OUTFIT_MATCHER = {
    "Black": {
        "pants": ["Grey chinos", "Dark denim jeans", "Black trousers"],
        "shoes": ["White sneakers", "Black leather shoes"],
        "accent": "Silver or gunmetal accessories",
    },
    "White": {
        "pants": ["Navy chinos", "Beige trousers", "Dark denim"],
        "shoes": ["Brown loafers", "White sneakers", "Tan brogues"],
        "accent": "Brown leather belt + watch",
    },
    "Navy": {
        "pants": ["Beige chinos", "Grey trousers", "Light denim"],
        "shoes": ["Brown leather shoes", "White sneakers"],
        "accent": "Brown or tan leather accessories",
    },
    "Grey": {
        "pants": ["Black trousers", "Navy chinos", "Dark denim"],
        "shoes": ["Black leather shoes", "White sneakers"],
        "accent": "Silver watch + dark belt",
    },
    "Beige": {
        "pants": ["Navy chinos", "White trousers", "Dark denim"],
        "shoes": ["Brown loafers", "White sneakers"],
        "accent": "Brown leather belt",
    },
    "Olive": {
        "pants": ["Black trousers", "Beige chinos", "Dark denim"],
        "shoes": ["Tan boots", "White sneakers"],
        "accent": "Canvas strap watch",
    },
    "Maroon": {
        "pants": ["Black chinos", "Grey trousers", "Dark denim"],
        "shoes": ["Black shoes", "White sneakers"],
        "accent": "Black belt + silver watch",
    },
    "Burgundy": {
        "pants": ["Black trousers", "Grey chinos", "Navy denim"],
        "shoes": ["Black leather shoes", "Brown boots"],
        "accent": "Oxblood or brown leather belt",
    },
    "Royal Blue": {
        "pants": ["White chinos", "Grey trousers", "Dark denim"],
        "shoes": ["White sneakers", "Brown loafers"],
        "accent": "Silver watch + light belt",
    },
    "Emerald": {
        "pants": ["Black trousers", "Beige chinos", "Navy denim"],
        "shoes": ["Brown leather shoes", "White sneakers"],
        "accent": "Gold or brass details",
    },
    "Mustard": {
        "pants": ["Black chinos", "Navy trousers", "Dark denim"],
        "shoes": ["White sneakers", "Tan boots"],
        "accent": "Minimal neutral accessories",
    },
}

# ======================================================================
# 8. AI OCCASION LOOK SUGGESTION
# ======================================================================
OCCASIONS = {
    "College": {
        "icon": "🎒",
        "look": ("Casual layered look — crew-neck tee under a hoodie or "
                 "overshirt, slim jeans or joggers, and clean white sneakers. "
                 "Backpack + watch completes it."),
        "tips": ["Opt for comfort + clean fit", "Keep colours casual & muted"],
    },
    "Interview": {
        "icon": "💼",
        "look": ("Formal and polished — a navy or charcoal suit, crisp white "
                 "or light-blue shirt, a subtle silk tie, and polished black "
                 "oxfords. Minimal accessories."),
        "tips": ["Stick to classic neutral colours", "Ensure clothes are ironed"],
    },
    "Wedding": {
        "icon": "💍",
        "look": ("Semi-formal / festive — a well-fitted blazer over a dress "
                 "shirt with tailored trousers, or a classic sherwani/bandhgala "
                 "for a traditional feel. Add elegant velvet loafers."),
        "tips": ["Slight sheen or pastel tones work well", "Coordinate with the dress code"],
    },
    "Party": {
        "icon": "🎉",
        "look": ("Smart-casual with edge — a black or burgundy shirt, slim-fit "
                 "dark jeans, and statement sneakers or boots. Rolled sleeves "
                 "add a relaxed vibe."),
        "tips": ["Textures like velvet or satin pop", "Keep jewellery minimal"],
    },
    "Casual": {
        "icon": "😎",
        "look": ("Relaxed and comfortable — a crisp polo or plain tee with "
                 "chinos or light denim, finished with clean sneakers or "
                 "canvas shoes."),
        "tips": ["Light colours for daytime", "Layering adds effortlessness"],
    },
}

# ======================================================================
# Convenience helpers
# ======================================================================

def pick(values, key, fallback_index=0):
    """Pick a value from a per-tone/per-shape dict, with a safe fallback."""
    if not values:
        return []
    if key in values:
        return values[key]
    # fall back to the first available entry
    first = next(iter(values.values()))
    return first


def fashion_for(tone, shape):
    """Bundle shirt, t-shirt, formal and casual suggestions for a tone+shape."""
    return {
        "shirt": pick(SHIRT_COLORS, tone),
        "tshirt": pick(TSHIRT_COLORS, tone),
        "formal": pick(FORMAL_OUTFITS, tone),
        "casual": pick(CASUAL_OUTFITS, tone),
    }


def glasses_for(shape):
    """Return list of (style, reason) for a face shape."""
    return GLASSES.get(shape, GLASSES["Oval"])


def hairstyles_for(shape):
    """Return list of (style, reason) for a face shape."""
    return HAIRSTYLES.get(shape, HAIRSTYLES["Oval"])


def beard_for(shape):
    """Return list of (style, reason) for a face shape."""
    return BEARD_STYLES.get(shape, BEARD_STYLES["Oval"])


def palette_for(tone):
    """Return recommended / avoid / note for a skin tone."""
    return PALETTE.get(tone, PALETTE["Medium"])


def outfit_match(shirt_color):
    """Return pants/shoes/accent for a selected shirt colour."""
    return OUTFIT_MATCHER.get(shirt_color, OUTFIT_MATCHER["Navy"])


def occasion_look(name):
    """Return the look dict for an occasion name."""
    return OCCASIONS.get(name, OCCASIONS["Casual"])
