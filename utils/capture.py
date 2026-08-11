"""
capture.py
----------
Background camera controller.

Captures frames from the webcam in a dedicated thread, runs the
FaceAnalyzer on each frame, and stores the newest AnalysisResult so the
UI can read it cheaply on its own timer.

On Windows the DirectShow backend is used because the default backend can
hang forever when the webcam is already in use by another application
(which looks like a frozen preview with "no face").
"""

import threading
import time

import cv2

from utils.config import DEFAULT_CAMERA_INDEX
from utils.render import render_overlay


class CameraController(threading.Thread):
    """Threaded webcam reader + analyzer."""

    def __init__(self, analyzer, camera_index=DEFAULT_CAMERA_INDEX):
        super().__init__(daemon=True)
        self.analyzer = analyzer
        self.camera_index = camera_index
        self._stop_event = threading.Event()
        self.lock = threading.Lock()
        self._latest = None
        self.camera_open = False
        self.fps = 0.0
        self.error = None

    # ------------------------------------------------------------------
    @property
    def latest(self):
        with self.lock:
            return self._latest

    # ------------------------------------------------------------------
    def stop(self):
        """Ask the thread to stop (non-blocking)."""
        self._stop_event.set()

    # ------------------------------------------------------------------
    @staticmethod
    def _open_camera(preferred_index):
        """
        Open a webcam quickly, trying several indices/backends.

        Returns an open VideoCapture or None (in which case the caller
        shows a clear error instead of freezing).
        """
        indices = [preferred_index, 0, 1, 2]
        dshow = getattr(cv2, "CAP_DSHOW", None)
        for idx in dict.fromkeys(indices):
            # DirectShow: opens fast and fails fast on Windows
            if dshow is not None:
                cap = cv2.VideoCapture(idx, dshow)
                if cap.isOpened():
                    # 640x480 is plenty for face analysis and much cheaper for
                    # the CPU than 1280x720.
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    return cap
                cap.release()
        # Last resort: default backend (some platforms ignore the backend flag)
        for idx in dict.fromkeys(indices):
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                return cap
            cap.release()
        return None

    # ------------------------------------------------------------------
    def run(self):
        """Main loop: grab -> analyze -> store."""
        cap = None
        try:
            cap = self._open_camera(self.camera_index)
            if cap is None:
                self.error = ("Webcam could not be opened. It may be in use "
                              "by another app — close it and restart.")
                return
            self.camera_open = True
            self.error = None

            frame_time = time.perf_counter()
            frame_count = 0
            while not self._stop_event.is_set():
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.02)
                    continue

                # Running FPS estimate
                now = time.perf_counter()
                frame_count += 1
                if now - frame_time >= 1.0:
                    self.fps = frame_count / (now - frame_time)
                    frame_time = now
                    frame_count = 0

                result = self.analyzer.analyze(frame)
                result.fps = self.fps
                # Render the annotated preview here (capture thread) so the
                # Tk UI thread only blits the finished image.
                result.overlay_rgb = render_overlay(result)
                with self.lock:
                    self._latest = result
        except Exception as exc:  # pragma: no cover - defensive
            self.error = f"Camera error: {exc}"
        finally:
            self.camera_open = False
            if cap is not None:
                cap.release()
