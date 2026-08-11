"""
app.py
------
Main application window for the AI Smart Style Advisor.

Wires together the camera controller (background thread), the face
analyzer, the live webcam preview and the recommendation panel, and
drives the UI refresh loop.
"""

import customtkinter as ctk

from utils.config import (
    APP_NAME, APP_TAGLINE, COLORS, UI_REFRESH_MS,
)
from models.face_analyzer import FaceAnalyzer
from utils.capture import CameraController
from ui.theme import font, setup
from ui.camera_widget import CameraWidget
from ui.recommendation_panel import RecommendationPanel


class StyleAdvisorApp(ctk.CTk):
    """Main window."""

    def __init__(self):
        setup()
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1500x900")
        self.minsize(1200, 720)
        self.configure(fg_color=COLORS["bg"])

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self._build_header()

        # ---- body: camera (left) + panel (right) ----------------------
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)

        self.camera = CameraWidget(body, preview_size=(820, 560))
        self.camera.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.panel = RecommendationPanel(body, width=620)
        self.panel.grid(row=0, column=1, sticky="nsew")

        # ---- engine -----------------------------------------------------
        try:
            self.analyzer = FaceAnalyzer()
        except FileNotFoundError as exc:
            self._fatal_error(str(exc))
            return

        self.camera_controller = CameraController(self.analyzer)
        self.camera_controller.start()

        self.after(UI_REFRESH_MS, self._tick)

    # ------------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=14)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")
        ctk.CTkLabel(title_box, text="✨ " + APP_NAME, font=font(22, True),
                     text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(title_box, text=APP_TAGLINE, font=font(12),
                     text_color=COLORS["text_dim"]).pack(anchor="w")

        badge = ctk.CTkLabel(header, text="AI · OpenCV · MediaPipe",
                             font=font(12, True), text_color=COLORS["accent_2"],
                             fg_color=COLORS["card"], corner_radius=12, padx=14, pady=6)
        badge.pack(side="right", padx=(12, 0))
        ctk.CTkLabel(header, text="v1.0", font=font(11), text_color=COLORS["text_dim"])\
            .pack(side="right")

    # ------------------------------------------------------------------
    def _fatal_error(self, message):
        self.camera.preview.configure(text=message, text_color=COLORS["danger"])

    # ------------------------------------------------------------------
    def _tick(self):
        """UI refresh loop: pull the latest analysis and render it."""
        result = self.camera_controller.latest
        self.camera.update_from_analysis(result, self.camera_controller)
        self.panel.set_analysis(result)

        self.after(UI_REFRESH_MS, self._tick)

    # ------------------------------------------------------------------
    def on_close(self):
        """Clean shutdown of camera thread and MediaPipe resources."""
        try:
            self.camera_controller.stop()
        except Exception:
            pass
        try:
            self.analyzer.close()
        except Exception:
            pass
        self.destroy()


def run():
    """Launch the application."""
    app = StyleAdvisorApp()
    app.mainloop()
