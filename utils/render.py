"""
render.py
---------
Builds the annotated preview image (face box, landmarks, tags, guidance
banner) as a plain RGB numpy array.

This runs inside the camera-capture thread so the Tk UI thread only has
to blit the finished image — keeping the interface responsive.
"""

import numpy as np
import cv2

from utils.config import COLORS

# Landmark drawing step: draw every Nth point (cheap, still looks full)
LANDMARK_STEP = 4
LANDMARK_RADIUS = 1


def _bgr(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return (b, g, r)


def _put_text_bg(img, text, origin, fg, bg, size=15, thick=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = size / 30.0
    (tw, th), baseline = cv2.getTextSize(text, font, scale, thick)
    x, y = origin
    cv2.rectangle(img, (x - 4, y - th - 4), (x + tw + 4, y + baseline + 4), bg, -1)
    cv2.putText(img, text, (x, y), font, scale, fg, thick, cv2.LINE_AA)


def render_overlay(result, max_height=480, message=None):
    """
    Render an annotated RGB image for display.

    Returns a numpy uint8 RGB array (H <= max_height). If there is no
    frame yet (or a camera error), a dark placeholder with a message is
    returned instead.
    """
    frame = result.frame if result is not None else None
    if frame is None:
        w = int(max_height * 4 / 3)
        img = np.full((max_height, w, 3), 14, dtype=np.uint8)
        _put_text_bg(img, message or "Starting camera…",
                     (w // 2 - 130, max_height // 2), _bgr(COLORS["text"]),
                     (20, 26, 36), size=16, thick=1)
        return img

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]
    scale = max_height / h
    nw, nh = int(w * scale), max_height
    img = cv2.resize(img, (nw, nh))

    if message:
        # Camera-error banner drawn on top of the last frame / black box
        _put_text_bg(img, message, (20, max(16, nh // 2 - 10)),
                     _bgr(COLORS["text"]), (60, 22, 28), size=15, thick=1)
        return img

    if result.detected and result.landmarks is not None:
        # ---- face box ----------------------------------------------------
        x, y, bw, bh = result.box
        p1 = (int(x * scale), int(y * scale))
        p2 = (int((x + bw) * scale), int((y + bh) * scale))
        cv2.rectangle(img, p1, p2, _bgr(COLORS["accent_2"]), 2)

        # ---- landmarks (subsampled for speed) ---------------------------
        pts = [(int(lx * nw), int(ly * nh)) for lx, ly, _ in result.landmarks]
        for i in range(0, len(pts), LANDMARK_STEP):
            px, py = pts[i]
            cv2.circle(img, (px, py), LANDMARK_RADIUS, _bgr(COLORS["accent"]), -1,
                       lineType=cv2.LINE_AA)

        # ---- info tag ------------------------------------------------------
        tag = f"{result.shape or '?'}  |  {result.skin_tone or '?'}"
        _put_text_bg(img, tag, (p1[0], max(6, p1[1] - 26)),
                     _bgr(COLORS["text"]), _bgr(COLORS["card"]))
    else:
        _put_text_bg(img, "Position your face in the frame",
                     (16, 16), _bgr(COLORS["text"]), (15, 20, 29))

    # ---- guidance banner ---------------------------------------------------
    banner_bg = (_bgr(COLORS["success"]) if result.guidance == "Perfect Position"
                 else _bgr(COLORS["warn"]))
    _put_text_bg(img, result.guidance or "Waiting for face", (16, 16),
                 (10, 14, 20), banner_bg, size=16, thick=2)

    return img
