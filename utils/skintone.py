"""
skintone.py
-----------
Estimate an approximate skin-tone category from a webcam frame.

The estimator samples a few patches of skin (forehead, cheeks, jaw) using
the face landmarks, normalizes for lighting, and maps the average luma
onto a Fitzpatrick-like scale: Fair / Light / Medium / Tan / Deep.

This is a rough estimate intended ONLY for suggesting clothing colours —
it is not a medical or scientific skin-type measurement.
"""

import numpy as np
import cv2

# Landmark indices used as skin sampling centres.
# Jaw / chin points are excluded because facial hair often covers them.
SAMPLE_INDICES = [
    9,      # nose bridge / forehead centre
    50,     # left cheek (under eye)
    280,    # right cheek (under eye)
    206,    # left lower cheek
    426,    # right lower cheek
]

# Luma thresholds (ITU-R BT.601) separating the five categories.
_LUMA_BOUNDS = [(205, "Fair"), (165, "Light"), (125, "Medium"), (88, "Tan"), (0, "Deep")]


def _patch_centroid(landmarks, index, w, h, face_box):
    """Pixel centre of a landmark, only if it lies inside the face box."""
    x, y = landmarks[index][0] * w, landmarks[index][1] * h
    fx, fy, fw, fh = face_box
    if not (fx <= x <= fx + fw and fy <= y <= fy + fh):
        return None
    return int(x), int(y)


def estimate_skin_tone(frame, landmarks, face_box):
    """
    Estimate skin tone from a BGR frame.

    Returns (tone, confidence, luma, undertone) where tone is one of the
    SKIN_TONES categories and undertone is "Warm" or "Cool".
    """
    h, w = frame.shape[:2]
    samples = []

    for idx in SAMPLE_INDICES:
        centre = _patch_centroid(landmarks, idx, w, h, face_box)
        if centre is None:
            continue
        cx, cy = centre
        half = 6
        x0, x1 = max(0, cx - half), min(w, cx + half)
        y0, y1 = max(0, cy - half), min(h, cy + half)
        patch = frame[y0:y1, x0:x1]
        if patch.size == 0:
            continue
        # Skin-colour sanity check: skin is redder than green by a small
        # margin; hair / beards / clothes usually do not satisfy this.
        b, g, r = patch.reshape(-1, 3).mean(axis=0)
        if 2 < (int(r) - int(g)) < 120 and int(r) > 25:
            samples.append((int(r), int(g), int(b)))

    if not samples:
        return None, 0.0, 0.0, "Warm"

    arr = np.array(samples, dtype=np.float64)
    r, g, b = arr.mean(axis=0)

    # Luma (ITU-R BT.601)
    luma = 0.299 * r + 0.587 * g + 0.114 * b

    # Gentle lighting correction: if the whole scene is very dark, raise
    # the floor slightly so the estimate is not dominated by shadows.
    scene_luma = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean()
    if scene_luma < 70:
        luma = min(255.0, luma + (70 - scene_luma) * 0.25)

    # Find category and confidence from distance to category boundaries.
    tone, conf = _classify_luma(luma)
    undertone = _undertone(r, g, b)
    return tone, conf, float(luma), undertone


def _classify_luma(luma):
    """Map luma to a tone category with a confidence value."""
    for upper, label in _LUMA_BOUNDS:
        if luma >= upper:
            break
    # distance to the nearest boundary -> confidence
    boundaries = [b for b, _ in _LUMA_BOUNDS]
    nearest = min(abs(luma - b) for b in boundaries)
    # 60 units of separation maps to confidence 1.0
    confidence = max(0.15, min(0.98, nearest / 60.0))
    return label, confidence


def _undertone(r, g, b):
    """Heuristic warm/cool undertone from the R/G/B balance."""
    # Warm skin reflects more yellow/red (G > B); cool skin leans blue.
    warmth = (r - b) - (g - b) * 0.5
    return "Warm" if warmth >= 0 else "Cool"
