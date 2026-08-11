"""
selfie_assistant.py
-------------------
Camera-position guidance ("AI Selfie Assistant").

Based purely on the geometry of the detected face inside the camera
frame (position, size, rotation), the lighting of the scene, and the
MediaPipe smile score, the module suggests one simple corrective action.

Messages produced:
    Move Left / Move Right / Move Closer / Move Back
    Look Straight / Smile / Improve Lighting / Perfect Position
"""

import cv2
import numpy as np

# Tuning thresholds (relative values)
MIN_FACE_RATIO = 0.18      # below this the face is too far / small
MAX_FACE_RATIO = 0.48      # above this the face is too close / large
POSITION_TOL = 0.10        # allowed horizontal offset from frame centre
TURN_TOL = 0.10            # allowed nose offset inside the face box
TILT_TOL = 12.0            # allowed head roll in degrees
SMILE_TARGET = 0.35        # minimum smile score considered a "smile"
BRIGHTNESS_MIN = 70        # too dark below this scene luma
BRIGHTNESS_MAX = 225       # too bright above this scene luma

# Dead-zones (reserved for future smoothing) — see comments above
RATIO_DEAD_ZONE = 0.03

# All guidance checks, in priority order
GUIDANCE_ORDER = [
    "Improve Lighting",
    "Move Closer",
    "Move Back",
    "Move Right",
    "Move Left",
    "Look Straight",
    "Smile",
]


def scene_brightness(frame):
    """Average scene luma (0..255)."""
    return float(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).mean())


def _signpost(active):
    """Return a checklist of every guidance state with its active flag."""
    return [(label, label == active) for label in GUIDANCE_ORDER + ["Perfect Position"]]


def get_guidance(result):
    """
    Compute the selfie-assistant message from an AnalysisResult.

    Returns (message, active_checklist).
    """
    if not result.detected:
        return "Please position your face in the frame", _signpost(None)

    frame_w = result.frame.shape[1]
    face_w = result.box[2] if result.box else 0
    face_ratio = face_w / frame_w if frame_w else 0.0

    # Horizontal position of the face inside the whole frame
    face_cx = (result.box[0] + result.box[2] / 2.0) / frame_w if frame_w else 0.5
    frame_centre = 0.5

    # Turn / tilt of the head (from geometry metrics)
    metrics = result.metrics
    nose_offset = metrics.nose_offset if metrics else 0.0
    tilt = abs(metrics.eye_tilt) if metrics else 0.0

    brightness = result.brightness
    smile = result.smile

    active = None

    # 1. Lighting -------------------------------------------------------
    if brightness < BRIGHTNESS_MIN:
        active = "Improve Lighting"
    elif brightness > BRIGHTNESS_MAX:
        active = "Improve Lighting"
    # 2. Distance --------------------------------------------------------
    elif face_ratio < MIN_FACE_RATIO:
        active = "Move Closer"
    elif face_ratio > MAX_FACE_RATIO:
        active = "Move Back"
    # 3. Horizontal position ---------------------------------------------
    elif face_cx > frame_centre + POSITION_TOL:
        active = "Move Left"          # face is to the right -> move left
    elif face_cx < frame_centre - POSITION_TOL:
        active = "Move Right"         # face is to the left -> move right
    # 4. Head straight ---------------------------------------------------
    elif abs(nose_offset) > TURN_TOL or abs(tilt) > TILT_TOL:
        active = "Look Straight"
    # 5. Smile -----------------------------------------------------------
    elif smile < SMILE_TARGET:
        active = "Smile"
    else:
        active = "Perfect Position"

    return active, _signpost(active)


# Display glyphs for each guidance state (used by the UI)
GUIDANCE_GLYPHS = {
    "Improve Lighting": "🔆",
    "Move Closer": "🙂",
    "Move Back": "↩️",
    "Move Right": "➡️",
    "Move Left": "⬅️",
    "Look Straight": "🧭",
    "Smile": "😁",
    "Perfect Position": "✅",
}
