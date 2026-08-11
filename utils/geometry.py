"""
geometry.py
-----------
Face-shape approximation from MediaPipe facial landmarks.

This module converts the 468 normalized face landmarks into a set of
simple facial measurements (forehead width, cheekbone width, jaw width,
face length, chin width) and then classifies the shape into one of
six broad categories: Oval, Round, Square, Rectangle, Heart, Diamond.

IMPORTANT: This is a geometric *approximation* used only to power style
recommendations. It never attempts to infer personality, intelligence,
character or emotions.
"""

import math

# ----------------------------------------------------------------------
# FaceMesh landmark indices used for the measurements
# (https://github.com/tensorflow/graphics/blob/master/tensorflow_graphics/
#  nn/geometry/landmark_encoders/face/README.md)
# ----------------------------------------------------------------------
FOREHEAD_TOP = 10          # centre of the forehead (top)
CHIN = 152                 # tip of the chin
LEFT_FOREHEAD = 63         # left temple / forehead
RIGHT_FOREHEAD = 293       # right temple / forehead
LEFT_CHEEK = 234           # left cheekbone (widest point)
RIGHT_CHEEK = 454          # right cheekbone (widest point)
LEFT_JAW = 172             # left jaw (near the mouth line)
RIGHT_JAW = 397            # right jaw (near the mouth line)
LEFT_JAW_BOTTOM = 132      # left lower jaw line
RIGHT_JAW_BOTTOM = 361     # right lower jaw line
NOSE_TIP = 1               # tip of the nose
LEFT_EYE = 33              # left outer eye corner
RIGHT_EYE = 263            # right outer eye corner
LEFT_EYE_INNER = 133       # left inner eye corner
RIGHT_EYE_INNER = 362      # right inner eye corner
LIPS_LEFT = 61             # left corner of the lips
LIPS_RIGHT = 291           # right corner of the lips
MOUTH_TOP = 13             # centre of upper lip
MOUTH_BOTTOM = 14          # centre of lower lip


def distance(p1, p2):
    """Euclidean distance between two (x, y) points."""
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return math.hypot(dx, dy)


class FaceMetrics:
    """Bunch of normalized face measurements derived from landmarks."""

    def __init__(self, forehead, cheekbone, jaw, chin_width, height,
                 nose_offset, eye_tilt, smile_score):
        self.forehead = forehead          # forehead width / face height
        self.cheekbone = cheekbone        # cheekbone width / face height
        self.jaw = jaw                    # jaw width / face height
        self.chin_width = chin_width      # lower jaw / cheekbone width
        self.height = height              # face height / cheekbone width
        # ratios used by the classifier
        self.jaw_to_cheek = jaw / cheekbone if cheekbone else 0.0
        self.fore_to_cheek = forehead / cheekbone if cheekbone else 0.0
        self.nose_offset = nose_offset    # -1 .. 1 (horizontal face turn)
        self.eye_tilt = eye_tilt          # degrees (head roll)
        self.smile_score = smile_score    # 0 .. 1


def compute_metrics(landmarks, smile_score=0.0):
    """
    Compute FaceMetrics from a list of normalized (x, y, z) landmarks.

    Parameters
    ----------
    landmarks : list of (x, y, z) tuples (normalized 0..1)
    smile_score : float 0..1 (from MediaPipe blendshapes, if available)
    """
    if not landmarks:
        return None

    def p(idx):
        return (landmarks[idx][0], landmarks[idx][1])

    # Absolute face height
    height_px = distance(p(FOREHEAD_TOP), p(CHIN))
    if height_px <= 1e-6:
        return None

    forehead = distance(p(LEFT_FOREHEAD), p(RIGHT_FOREHEAD)) / height_px
    cheekbone = distance(p(LEFT_CHEEK), p(RIGHT_CHEEK)) / height_px
    jaw = distance(p(LEFT_JAW), p(RIGHT_JAW)) / height_px
    chin_width = distance(p(LEFT_JAW_BOTTOM), p(RIGHT_JAW_BOTTOM)) / \
        distance(p(LEFT_CHEEK), p(RIGHT_CHEEK))

    # Head-pose hints (used by the selfie assistant)
    face_center_x = (p(LEFT_CHEEK)[0] + p(RIGHT_CHEEK)[0]) / 2.0
    nose_offset = p(NOSE_TIP)[0] - face_center_x

    eye_y_l = (landmarks[LEFT_EYE][1] + landmarks[LEFT_EYE_INNER][1]) / 2.0
    eye_y_r = (landmarks[RIGHT_EYE][1] + landmarks[RIGHT_EYE_INNER][1]) / 2.0
    eye_dx = p(LEFT_EYE)[0] - p(RIGHT_EYE)[0]
    eye_dy = p(LEFT_EYE)[1] - p(RIGHT_EYE)[1]
    eye_tilt = math.degrees(math.atan2(eye_dy, eye_dx)) if eye_dx else 0.0
    _ = (eye_y_l, eye_y_r)  # reserved for future use

    return FaceMetrics(
        forehead=forehead,
        cheekbone=cheekbone,
        jaw=jaw,
        chin_width=chin_width,
        height=1.0 / cheekbone if cheekbone else 0.0,
        nose_offset=nose_offset,
        eye_tilt=eye_tilt,
        smile_score=smile_score,
    )


# ----------------------------------------------------------------------
# Fuzzy classifier
# ----------------------------------------------------------------------
def _gaussian(value, center, sigma):
    """Bell-shaped membership function used by the fuzzy classifier."""
    return math.exp(-((value - center) ** 2) / (2 * sigma ** 2))


def classify_face_shape(metrics):
    """
    Classify the face shape and return (shape, confidence, scores).

    The classifier is a small weighted fuzzy-logic engine. Each prototype
    shape gets a score between 0 and 1; the best match wins and the
    confidence reflects how strongly it beats the runner-up.
    """
    if metrics is None:
        return "Unknown", 0.0, {}

    m = metrics
    scores = {}

    # ---- Oval ---------------------------------------------------------
    scores["Oval"] = (
        0.30 * _gaussian(m.height, 1.35, 0.12) +
        0.25 * _gaussian(m.jaw_to_cheek, 0.88, 0.09) +
        0.20 * _gaussian(m.fore_to_cheek, 0.92, 0.09) +
        0.25 * _gaussian(m.chin_width, 0.86, 0.08)
    )

    # ---- Round ---------------------------------------------------------
    scores["Round"] = (
        0.30 * _gaussian(m.height, 1.12, 0.09) +
        0.25 * _gaussian(m.jaw_to_cheek, 0.95, 0.05) +
        0.25 * _gaussian(m.fore_to_cheek, 0.96, 0.05) +
        0.20 * _gaussian(m.chin_width, 0.92, 0.06)
    )

    # ---- Square --------------------------------------------------------
    scores["Square"] = (
        0.25 * _gaussian(m.height, 1.18, 0.08) +
        0.30 * _gaussian(m.jaw_to_cheek, 0.97, 0.04) +
        0.25 * _gaussian(m.fore_to_cheek, 1.00, 0.05) +
        0.20 * _gaussian(m.chin_width, 0.95, 0.05)
    )

    # ---- Rectangle (long / oblong) ------------------------------------
    scores["Rectangle"] = (
        0.35 * _gaussian(m.height, 1.55, 0.12) +
        0.25 * _gaussian(m.jaw_to_cheek, 0.90, 0.08) +
        0.20 * _gaussian(m.fore_to_cheek, 0.94, 0.08) +
        0.20 * _gaussian(m.chin_width, 0.90, 0.08)
    )

    # ---- Heart ----------------------------------------------------------
    scores["Heart"] = (
        0.35 * _gaussian(m.fore_to_cheek, 1.05, 0.05) +
        0.30 * _gaussian(m.jaw_to_cheek, 0.72, 0.07) +
        0.20 * _gaussian(m.chin_width, 0.62, 0.07) +
        0.15 * _gaussian(m.height, 1.25, 0.10)
    )

    # ---- Diamond ---------------------------------------------------------
    scores["Diamond"] = (
        0.35 * _gaussian(m.fore_to_cheek, 0.85, 0.05) +
        0.30 * _gaussian(m.jaw_to_cheek, 0.82, 0.06) +
        0.20 * _gaussian(m.chin_width, 0.72, 0.07) +
        0.15 * _gaussian(m.height, 1.35, 0.10)
    )

    total = sum(scores.values()) or 1.0
    shape = max(scores, key=scores.get)
    confidence = scores[shape] / total
    confidence = max(0.0, min(1.0, confidence))
    return shape, confidence, scores
