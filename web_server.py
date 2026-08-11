"""
web_server.py
-------------
Web deployment of the AI Smart Style Advisor.

Two pages:

1)  /   — "camera on YOUR device"
        Every device opens the link and uses ITS OWN webcam. The browser
        captures frames, sends them to this server for analysis, and shows
        the results (face shape, skin tone, recommendations) — powered by
        the same Python engine as the desktop app.

2)  /lab — "lab PC camera"
        The old demo: the lab PC's webcam streams to viewers. The webcam is
        opened LAZILY (only while somebody watches) and auto-stops ~60 s
        after the last viewer leaves, so the laptop camera is not left on.

The laptop camera therefore only turns on when /lab is actively watched.

Run:
    py web_server.py

Expose it to the internet (for phone access anywhere) with:
    cloudflared tunnel --url http://localhost:8000
"""

import os
import socket
import threading
import time
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, Response, jsonify, request, send_file

from models.face_analyzer import FaceAnalyzer
from utils.capture import CameraController
from utils.render import render_overlay
from utils.colors import COLOR_HEX
from utils.recommendations import (
    fashion_for, glasses_for, hairstyles_for, beard_for,
    palette_for, outfit_match, occasion_look, OCCASIONS, SHIRT_COLOR_CHOICES,
)
from utils.selfie_assistant import GUIDANCE_GLYPHS

PORT = int(os.environ.get("PORT", 8000))   # Render injects PORT; default 8000 locally
BASE_DIR = Path(__file__).resolve().parent
WEB_UI = BASE_DIR / "ui" / "web" / "index_camera.html"   # device's own camera
WEB_LAB = BASE_DIR / "ui" / "web" / "index.html"          # lab PC camera demo

LAB_CAM_IDLE_TIMEOUT = 60   # seconds after the last viewer before stopping

app = Flask(__name__)

# ----------------------------------------------------------------------
# Shared analyzer (single MediaPipe instance, guarded by a lock because
# the Tasks API is not thread-safe).
# ----------------------------------------------------------------------
_analyzer = FaceAnalyzer()
_analyze_lock = threading.Lock()


def _run_analysis(frame_bgr):
    """Analyse a frame under the shared lock."""
    with _analyze_lock:
        return _analyzer.analyze(frame_bgr)


def _result_payload(result):
    """Build the full JSON payload for one analysed frame."""
    shape = result.shape if result.detected else None
    tone = result.skin_tone if result.detected else None
    payload = {
        "detected": result.detected,
        "landmarks": [[round(p[0], 4), round(p[1], 4)]
                      for p in (result.landmarks or [])],
        "box": None,
        "shape": shape,
        "shape_conf": round(result.shape_conf, 2) if result.detected else 0.0,
        "skin_tone": tone,
        "skin_undertone": result.skin_undertone if result.detected else None,
        "skin_conf": round(result.skin_conf, 2) if result.detected else 0.0,
        "smile": round(result.smile, 2),
        "guidance": result.guidance,
        "checklist": [{"label": l, "active": a} for l, a in result.checklist],
        "recommendations": _recommendations_payload(shape, tone),
    }
    if result.detected and result.box:
        x, y, w, h = result.box
        payload["box"] = [round(x / result.frame.shape[1], 4),
                          round(y / result.frame.shape[0], 4),
                          round(w / result.frame.shape[1], 4),
                          round(h / result.frame.shape[0], 4)]
    return payload


def _recommendations_payload(shape, tone):
    return {
        "shape": shape,
        "tone": tone,
        "fashion": fashion_for(tone, shape),
        "glasses": [{"style": s, "reason": r} for s, r in glasses_for(shape)],
        "hairstyles": [{"style": s, "reason": r} for s, r in hairstyles_for(shape)],
        "beard": [{"style": s, "reason": r} for s, r in beard_for(shape)],
        "palette": palette_for(tone),
        "occasions": {k: {"icon": v["icon"], "look": v["look"], "tips": v["tips"]}
                      for k, v in OCCASIONS.items()},
        "shirt_colors": SHIRT_COLOR_CHOICES,
        "guidance_glyphs": GUIDANCE_GLYPHS,
    }


# ======================================================================
# Lazy lab-PC camera (opened only while /lab is watched)
# ======================================================================
class LabStream:
    """The lab-PC webcam stream — started lazily and auto-stopped."""

    def __init__(self):
        self.lock = threading.Lock()
        self._latest = None
        self._jpeg = None
        self.error = None
        self.running = False
        self._stop = threading.Event()
        self.thread = None
        self.last_access = 0.0

    # ------------------------------------------------------------------
    def ensure_running(self):
        with self.lock:
            self.last_access = time.time()
            if self.running:
                return
            self._stop = threading.Event()
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        with self.lock:
            self._stop.set()

    @property
    def jpeg(self):
        with self.lock:
            return self._jpeg

    # ------------------------------------------------------------------
    def _run(self):
        cap = None
        try:
            cap = CameraController._open_camera(0)
            if cap is None:
                with self.lock:
                    self.error = "Webcam could not be opened."
                return
            with self.lock:
                self.running = True
                self.error = None

            while not self._stop.is_set():
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.02)
                    continue
                result = _run_analysis(frame)
                overlay = render_overlay(result)
                ok_enc, buf = cv2.imencode(
                    ".jpg", cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR),
                    [cv2.IMWRITE_JPEG_QUALITY, 80])
                with self.lock:
                    self._latest = result
                    self._jpeg = buf.tobytes() if ok_enc else None
                    self.last_access = time.time()
        except Exception as exc:
            with self.lock:
                self.error = f"Camera error: {exc}"
        finally:
            if cap is not None:
                cap.release()
            with self.lock:
                self.running = False


lab_stream = LabStream()


def _lab_watchdog():
    """Auto-stop the lab camera after the last viewer leaves."""
    while True:
        time.sleep(5)
        if lab_stream.running and time.time() - lab_stream.last_access > LAB_CAM_IDLE_TIMEOUT:
            lab_stream.stop()
        if (not lab_stream.running) and time.time() - lab_stream.last_access > LAB_CAM_IDLE_TIMEOUT:
            lab_stream.last_access = time.time()


threading.Thread(target=_lab_watchdog, daemon=True).start()


# ======================================================================
# Routes
# ======================================================================
@app.route("/")
def index():
    """The device's-own-camera page."""
    page = WEB_UI if WEB_UI.exists() else WEB_LAB
    if page.exists():
        return send_file(page)
    return "<h1>AI Smart Style Advisor</h1><p>web UI missing.</p>", 404


@app.route("/lab")
def lab_page():
    """The lab-PC camera demo page."""
    if WEB_LAB.exists():
        return send_file(WEB_LAB)
    return "lab page missing.", 404


@app.route("/video_feed")
def video_feed():
    """MJPEG stream of the lab-PC webcam (lazy start)."""
    lab_stream.ensure_running()

    def generate():
        while True:
            lab_stream.last_access = time.time()
            jpeg = lab_stream.jpeg
            if jpeg is not None:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")
            time.sleep(0.05)

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """Analyse an image uploaded from a visitor's own webcam."""
    file = request.files.get("image")
    if file is None:
        return jsonify({"error": "no image uploaded"}), 400
    data = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify({"error": "could not decode image"}), 400
    result = _run_analysis(frame)
    return jsonify(_result_payload(result))


@app.route("/api/status")
def api_status():
    """Lab-stream status (used by the /lab page)."""
    r = lab_stream._latest
    if r is None:
        return jsonify({"detected": False, "guidance": "Waiting for camera…",
                        "camera_error": lab_stream.error, "fps": 0.0})
    return jsonify({
        "detected": r.detected,
        "shape": r.shape,
        "shape_conf": round(r.shape_conf, 2),
        "shape_scores": {k: round(v, 3) for k, v in (r.shape_scores or {}).items()},
        "skin_tone": r.skin_tone,
        "skin_undertone": r.skin_undertone,
        "skin_conf": round(r.skin_conf, 2),
        "smile": round(r.smile, 2),
        "guidance": r.guidance,
        "checklist": [{"label": l, "active": a} for l, a in r.checklist],
        "camera_error": lab_stream.error,
        "fps": 0.0,
    })


@app.route("/api/recommendations")
def api_recommendations():
    """Recommendations for the current lab-stream face (used by /lab)."""
    r = lab_stream._latest
    shape = r.shape if (r and r.detected) else None
    tone = r.skin_tone if (r and r.detected) else None
    return jsonify(_recommendations_payload(shape, tone))


@app.route("/api/outfit")
def api_outfit():
    shirt = request.args.get("shirt", "Navy")
    return jsonify({"shirt": shirt, **outfit_match(shirt)})


@app.route("/api/occasion")
def api_occasion():
    name = request.args.get("name", "Casual")
    return jsonify({"name": name, **occasion_look(name)})


@app.route("/api/colors")
def api_colors():
    return jsonify(COLOR_HEX)


# ======================================================================
# Helpers
# ======================================================================
def local_ips():
    ips = set()
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except Exception:
        pass
    if not ips or ("127.0.0.1" in ips and len(ips) == 1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ips.add(s.getsockname()[0])
            s.close()
        except Exception:
            pass
    return sorted(ips)


def print_links():
    print("=" * 62)
    print("  AI SMART STYLE ADVISOR — WEB SERVER")
    print("=" * 62)
    print("  /     -> every device uses ITS OWN camera (phone / laptop)")
    print("  /lab  -> the lab PC's camera streams to viewers (auto-stops)")
    print()
    print("  LAN links (same Wi-Fi):")
    for ip in local_ips():
        print(f"      http://{ip}:{PORT}")
    print()
    print("  Public link (anywhere): run a tunnel, e.g.")
    print("      cloudflared tunnel --url http://localhost:8000")
    print("  NOTE: browser cameras need HTTPS — use the public tunnel link")
    print("        or open http://localhost:8000 on the PC itself.")
    print("=" * 62)


def main():
    print_links()
    app.run(host="0.0.0.0", port=PORT, threaded=True, debug=False)


if __name__ == "__main__":
    main()
