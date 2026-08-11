"""
face_analyzer.py
----------------
Real-time face analysis engine built on the MediaPipe Tasks FaceLandmarker.

For every camera frame it produces an AnalysisResult containing:
  * 468 normalized facial landmarks
  * a bounding box for the face
  * an approximate face shape + confidence
  * an approximate skin tone + confidence
  * a smile score and scene brightness
  * selfie-assistant guidance

The result is a plain dataclass so the UI layer can render it freely.
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional

import cv2
import numpy as np

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from utils.config import FACE_LANDMARK_MODEL
from utils.geometry import compute_metrics, classify_face_shape
from utils.skintone import estimate_skin_tone
from utils.selfie_assistant import get_guidance, scene_brightness


@dataclass
class AnalysisResult:
    """Everything derived from a single camera frame."""

    frame: np.ndarray = field(default=None)        # original BGR frame
    detected: bool = False
    landmarks: Optional[List] = None               # normalized (x, y, z) list
    box: Optional[tuple] = None                    # pixel (x, y, w, h)
    metrics: Optional[object] = None               # FaceMetrics (geometry)
    shape: Optional[str] = None
    shape_scores: dict = field(default_factory=dict)
    shape_conf: float = 0.0
    skin_tone: Optional[str] = None
    skin_undertone: Optional[str] = None
    skin_conf: float = 0.0
    skin_luma: float = 0.0
    smile: float = 0.0
    brightness: float = 0.0
    guidance: str = "Waiting for face"
    checklist: list = field(default_factory=list)
    fps: float = 0.0
    overlay_rgb: Optional[np.ndarray] = None   # annotated preview (RGB)


class FaceAnalyzer:
    """Wraps the MediaPipe FaceLandmarker in a simple analyze() API."""

    def __init__(self, model_path=None):
        model_path = model_path or FACE_LANDMARK_MODEL
        if not model_path.exists():
            raise FileNotFoundError(
                f"Face Landmarker model not found at {model_path}. "
                "Download it from the MediaPipe model zoo (see README)."
            )
        options = vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.3,
            min_face_presence_confidence=0.3,
            min_tracking_confidence=0.3,
            output_face_blendshapes=True,
        )
        self._landmarker = vision.FaceLandmarker.create_from_options(options)
        self._clock = time.monotonic_ns()

    # ------------------------------------------------------------------
    def analyze(self, frame_bgr: np.ndarray) -> AnalysisResult:
        """Analyse a BGR frame and return an AnalysisResult."""
        result = AnalysisResult(frame=frame_bgr)
        h, w = frame_bgr.shape[:2]
        result.brightness = scene_brightness(frame_bgr)

        # Frame is captured in BGR; MediaPipe expects RGB.
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        try:
            timestamp = time.monotonic_ns() // 1_000_000
            mp_result = self._landmarker.detect_for_video(mp_image, timestamp)
        except Exception:
            mp_result = None

        if mp_result and mp_result.face_landmarks:
            try:
                lm = mp_result.face_landmarks[0]
                landmarks = [(p.x, p.y, p.z) for p in lm]
                result.detected = True
                result.landmarks = landmarks

                # ---- pixel bounding box -----------------------------------
                xs = [p.x for p in lm]
                ys = [p.y for p in lm]
                x0, x1 = int(min(xs) * w), int(max(xs) * w)
                y0, y1 = int(min(ys) * h), int(max(ys) * h)
                pad_x = int((x1 - x0) * 0.05)
                pad_y = int((y1 - y0) * 0.05)
                result.box = (max(0, x0 - pad_x), max(0, y0 - pad_y),
                              min(w - x0 + pad_x, x1 - x0 + 2 * pad_x),
                              min(h - y0 + pad_y, y1 - y0 + 2 * pad_y))

                # ---- smile score from blendshapes --------------------------
                result.smile = self._smile_score(mp_result)

                # ---- geometry / face shape ---------------------------------
                result.metrics = compute_metrics(landmarks, result.smile)
                shape, conf, scores = classify_face_shape(result.metrics)
                result.shape = shape
                result.shape_scores = scores
                result.shape_conf = conf

                # ---- skin tone ----------------------------------------------
                tone, conf2, luma, undertone = estimate_skin_tone(
                    frame_bgr, landmarks, result.box)
                result.skin_tone = tone
                result.skin_conf = conf2
                result.skin_luma = luma
                result.skin_undertone = undertone

                # ---- selfie guidance ----------------------------------------
                msg, checklist = get_guidance(result)
                result.guidance = msg
                result.checklist = checklist
            except Exception:
                # Never let a single bad frame kill the camera thread.
                # Keep whatever partial data was extracted.
                result.detected = True
                if not result.guidance:
                    result.guidance = "Face detected — analysing…"
        else:
            result.guidance = "Please position your face in the frame"

        return result

    # ------------------------------------------------------------------
    @staticmethod
    def _smile_score(mp_result):
        """Read the 'smile' blendshape (0..1) if available."""
        try:
            blendshapes = mp_result.face_blendshapes
            if blendshapes:
                for category in blendshapes[0]:
                    if category.category_name == "smile":
                        return float(category.score)
        except Exception:
            pass
        return 0.0

    # ------------------------------------------------------------------
    def close(self):
        """Release MediaPipe resources."""
        try:
            self._landmarker.close()
        except Exception:
            pass
