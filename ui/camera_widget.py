"""
camera_widget.py
----------------
Live webcam preview.

The annotated preview image is rendered in the capture thread (see
utils/render.py) and stored on the AnalysisResult as overlay_rgb. This
widget only converts it to a CTkImage and blits it — keeping the Tk UI
thread light and responsive.
"""

import numpy as np
import customtkinter as ctk
from PIL import Image

from utils.config import COLORS
from utils.render import render_overlay
from ui.theme import font


class CameraWidget(ctk.CTkFrame):
    """Webcam preview with a status strip beneath it."""

    def __init__(self, master, preview_size=(820, 540)):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=16,
                         border_width=1, border_color=COLORS["border"])
        self.preview_size = preview_size
        self._ctk_image = None
        self._disp_size = None
        self._last_shown_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Preview surface
        self.preview = ctk.CTkLabel(self, text="Starting camera…",
                                    font=font(16), text_color=COLORS["text_dim"],
                                    fg_color=COLORS["bg_alt"], corner_radius=12,
                                    width=preview_size[0], height=preview_size[1])
        self.preview.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="nsew")

        # Status strip: FPS | camera | guidance
        strip = ctk.CTkFrame(self, fg_color="transparent")
        strip.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
        strip.grid_columnconfigure(3, weight=1)

        self.fps_label = ctk.CTkLabel(strip, text="FPS —", font=font(12),
                                      text_color=COLORS["text_dim"])
        self.fps_label.grid(row=0, column=0, padx=(0, 16))

        self.camera_label = ctk.CTkLabel(strip, text="Camera: ● starting",
                                         font=font(12, True), text_color=COLORS["warn"])
        self.camera_label.grid(row=0, column=1, padx=(0, 16))

        self.detection_label = ctk.CTkLabel(strip, text="Face: not detected",
                                            font=font(12), text_color=COLORS["text_dim"])
        self.detection_label.grid(row=0, column=2)

        self.guidance_label = ctk.CTkLabel(strip, text="", font=font(12, True),
                                           text_color=COLORS["accent_2"])
        self.guidance_label.grid(row=0, column=3, sticky="e")

    # ------------------------------------------------------------------
    def update_from_analysis(self, result, controller=None):
        """Blit the latest pre-rendered preview + update the status strip."""
        error = controller.error if controller is not None else None

        # Skip the expensive blit if this exact frame was already shown
        # (the UI timer can outpace the capture thread).
        if result is not None and id(result) == self._last_shown_id:
            self._update_strip(result, controller)
            return

        # Preview image (already annotated by the capture thread)
        if result is not None and result.overlay_rgb is not None:
            self._set_preview(result.overlay_rgb)
        elif result is not None:
            # Face detected but no overlay rendered yet (rare)
            self._set_preview(render_overlay(result, max_height=480,
                                             message=error))
        elif self._ctk_image is None:
            # No frame yet / camera failed — show a status placeholder once
            self._set_preview(render_overlay(None, max_height=480,
                                             message=error or None))

        if result is not None:
            self._last_shown_id = id(result)
        self._update_strip(result, controller)

    # ------------------------------------------------------------------
    def _update_strip(self, result, controller=None):
        """Refresh the cheap status labels (FPS / camera / face / guidance)."""
        error = controller.error if controller is not None else None
        fps = result.fps if result is not None else 0.0
        self.fps_label.configure(text=f"FPS {fps:4.1f}")
        if controller is not None:
            if error:
                self.camera_label.configure(text="Camera: ✕ error",
                                            text_color=COLORS["danger"])
            elif controller.camera_open:
                self.camera_label.configure(text="Camera: ● live",
                                            text_color=COLORS["success"])
            else:
                self.camera_label.configure(text="Camera: ● starting",
                                            text_color=COLORS["warn"])

        detected = result.detected if result is not None else False
        self.detection_label.configure(
            text=("Face: detected" if detected else "Face: not detected"),
            text_color=COLORS["success"] if detected else COLORS["text_dim"])
        guidance = result.guidance if result is not None else "Starting camera…"
        self.guidance_label.configure(text=guidance)

    # ------------------------------------------------------------------
    def _set_preview(self, rgb_array):
        """Convert an RGB numpy array to a CTkImage and display it.

        The image is fitted into the preview box preserving its aspect
        ratio. The CTkImage is only rebuilt when that fitted size changes,
        otherwise it is reconfigured in place (fast path).
        """
        pil = Image.fromarray(rgb_array.astype(np.uint8))
        disp = _fit_size(pil.size, self.preview_size)
        if self._ctk_image is None or disp != self._disp_size:
            self._ctk_image = ctk.CTkImage(light_image=pil, dark_image=pil, size=disp)
            self._disp_size = disp
            self.preview.configure(image=self._ctk_image, text="")
        else:
            self._ctk_image.configure(light_image=pil, dark_image=pil)


def _fit_size(source, box):
    """Return (w, h) fitting `source` inside `box` while keeping aspect."""
    sw, sh = source
    bw, bh = box
    scale = min(bw / sw, bh / sh)
    return (max(1, int(sw * scale)), max(1, int(sh * scale)))
