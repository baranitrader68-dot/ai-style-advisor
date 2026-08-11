"""
recommendation_panel.py
-----------------------
Right-side recommendation panel.

Contains:
  * a navigation sidebar (icon + label buttons for every category)
  * a scrollable content area rebuilt per selected category

The panel receives the latest AnalysisResult via set_analysis() and
re-renders "live" categories (dashboard, palette, selfie, glasses, ...)
whenever the analysis signature changes.
"""

import time

import customtkinter as ctk

from utils.config import COLORS, CATEGORIES, CATEGORY_ORDER, FACE_SHAPES
from utils.recommendations import (
    fashion_for, glasses_for, hairstyles_for, beard_for,
    palette_for, outfit_match, occasion_look, OCCASIONS,
)
from utils.selfie_assistant import GUIDANCE_GLYPHS
from ui.theme import font
from ui import cards, icons

DISCLAIMER = ("Style suggestions are based only on visual features "
              "(face shape, skin tone) and predefined fashion rules. "
              "This app never judges personality, intelligence or character.")

SHAPE_DESCRIPTIONS = {
    "Oval": "Balanced proportions — most styles will suit you.",
    "Round": "Soft curves, similar width and length.",
    "Square": "Strong jawline with similar width and length.",
    "Rectangle": "Longer than wide with defined angles.",
    "Heart": "Wide forehead narrowing to a gentle chin.",
    "Diamond": "Prominent cheekbones with a narrower chin.",
}


class RecommendationPanel(ctk.CTkFrame):
    def __init__(self, master, width=620):
        super().__init__(master, fg_color=COLORS["panel"], corner_radius=16,
                         width=width, border_width=1, border_color=COLORS["border"])
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._latest = None
        self._signature = None
        self._last_rebuild = 0.0
        self._rebuild_pending = False
        self._current = "dashboard"
        self._buttons = {}
        self._occasion_selected = "Casual"
        self._shirt_selected = "Navy"

        # ---- header --------------------------------------------------
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(14, 8))
        ctk.CTkLabel(header, text="Style Studio", font=font(18, True),
                     text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Recommendations · powered by vision",
                     font=font(12), text_color=COLORS["text_dim"]).pack(anchor="w")

        # ---- navigation sidebar ---------------------------------------
        self.nav = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_alt"],
                                          corner_radius=12, width=210)
        self.nav.grid(row=1, column=0, sticky="nsw", padx=(16, 8), pady=(0, 16))
        for key in CATEGORY_ORDER:
            self._buttons[key] = self._make_nav_button(key)
            self._buttons[key].pack(fill="x", padx=8, pady=3)

        # ---- content area ----------------------------------------------
        self.content = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                              corner_radius=12)
        self.content.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=(0, 16))

        self.switch("dashboard")

    # ------------------------------------------------------------------
    def _make_nav_button(self, key):
        title, _, emoji, accent, image_name = CATEGORIES[key]
        icon = icons.load_icon(image_name, 20)
        button = ctk.CTkButton(
            self.nav, text=f"{emoji}  {title}", font=font(13, True),
            fg_color="transparent", hover_color=COLORS["card_hover"],
            text_color=COLORS["text_dim"], anchor="w",
            corner_radius=10, height=38, image=icon, compound="left",
            command=lambda k=key: self.switch(k),
        )
        return button

    # ------------------------------------------------------------------
    def switch(self, key):
        """Switch to a category and rebuild its content."""
        self._current = key
        for k, b in self._buttons.items():
            _, _, _, accent, _ = CATEGORIES[k]
            selected = (k == key)
            b.configure(
                fg_color=COLORS["card"] if selected else "transparent",
                text_color=accent if selected else COLORS["text_dim"],
                hover_color=COLORS["card_hover"],
            )
        self._rebuild()

    # ------------------------------------------------------------------
    def set_analysis(self, result):
        """
        Store the latest analysis. Live categories are rebuilt only when
        the analysis meaningfully changes, and at most every ~700 ms, so
        a busy camera can never starve the UI thread.
        """
        self._latest = result
        sig = self._analysis_signature(result)
        if sig != self._signature:
            self._signature = sig
            if self._current in ("dashboard", "palette", "selfie", "glasses",
                                 "fashion", "hairstyle", "beard"):
                self._schedule_rebuild()

    @staticmethod
    def _analysis_signature(result):
        """Coarse signature used to decide whether the panel must rebuild."""
        if result is None or not result.detected:
            return ("none",)
        return (
            result.detected,
            result.shape,
            round(result.shape_conf, 1),
            result.skin_tone,
            round(result.skin_conf, 1),
            result.guidance,
        )

    def _schedule_rebuild(self):
        """Rebuild immediately if >700 ms since last rebuild, else soon."""
        now = time.monotonic()
        if now - self._last_rebuild >= 0.7:
            self._last_rebuild = now
            self._rebuild()
        elif not self._rebuild_pending:
            self._rebuild_pending = True
            self.after(700, self._flush_rebuild)

    def _flush_rebuild(self):
        self._rebuild_pending = False
        now = time.monotonic()
        if now - self._last_rebuild >= 0.7:
            self._last_rebuild = now
            self._rebuild()

    # ------------------------------------------------------------------
    def _clear(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _rebuild(self):
        self._clear()
        builder = getattr(self, f"_build_{self._current}")
        builder()
        self._footer()

    # ==================================================================
    # Shared helpers
    # ==================================================================
    def _header(self, emoji, title, subtitle, accent):
        head = ctk.CTkFrame(self.content, fg_color=COLORS["card"], corner_radius=14,
                            border_width=1, border_color=COLORS["border"])
        head.pack(fill="x", padx=4, pady=(0, 12))
        head.grid_columnconfigure(1, weight=1)
        emoji_lbl = ctk.CTkLabel(head, text=emoji, font=font(30),
                                 fg_color=accent, text_color="#10141C",
                                 corner_radius=12, width=52, height=52)
        emoji_lbl.grid(row=0, column=0, rowspan=2, padx=14, pady=12)
        ctk.CTkLabel(head, text=title, font=font(19, True),
                     text_color=COLORS["text"]).grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(head, text=subtitle, font=font(12),
                     text_color=COLORS["text_dim"]).grid(row=1, column=1, sticky="nw")

    def _footer(self):
        foot = ctk.CTkFrame(self.content, fg_color="transparent")
        foot.pack(fill="x", padx=4, pady=(12, 0))
        ctk.CTkLabel(foot, text="ℹ️  " + DISCLAIMER, font=font(11),
                     text_color=COLORS["text_dim"], justify="left", wraplength=360).pack(anchor="w")

    def _no_face(self, message="Position your face in the camera frame to get personalised suggestions."):
        card = cards.Card(self.content, title="Waiting for face", icon="🧑", accent=COLORS["warn"])
        card.pack(fill="x", padx=4, pady=6)
        cards.para(card.body(), message).pack(fill="x")

    def _confidence_card(self):
        if self._latest and self._latest.detected:
            r = self._latest
            card = cards.Card(self.content, title="Analysis confidence", icon="🎯",
                              accent=COLORS["accent"])
            body = card.body()
            cards.ConfidenceBar(body, "Face shape detection", r.shape_conf,
                                accent=COLORS["accent"]).pack(fill="x", pady=4)
            cards.ConfidenceBar(body, "Skin-tone estimation", r.skin_conf,
                                accent=COLORS["accent_2"]).pack(fill="x", pady=4)
            card.pack(fill="x", padx=4, pady=6)

    # ==================================================================
    # Dashboard
    # ==================================================================
    def _build_dashboard(self):
        self._header("📊", "Dashboard", "Live overview of your style analysis", COLORS["accent"])
        r = self._latest

        if r is None or not r.detected:
            self._no_face()
            self._confidence_card()
            return

        # Face shape card
        card = cards.Card(self.content, title=f"Detected face shape · {r.shape}", icon="🧑",
                          accent=COLORS["accent"])
        body = card.body()
        cards.para(body, SHAPE_DESCRIPTIONS.get(r.shape, "")).pack(fill="x", pady=(0, 8))
        cards.ConfidenceBar(body, "Shape confidence", r.shape_conf).pack(fill="x")
        card.pack(fill="x", padx=4, pady=6)

        # Skin tone card
        card = cards.Card(self.content, title=f"Approximate skin tone · {r.skin_tone}",
                          icon="🎨", accent=COLORS["accent_2"])
        body = card.body()
        cards.para(body, f"Undertone: {r.skin_undertone} · "
                         "Used only for colour suggestions.").pack(fill="x", pady=(0, 8))
        cards.ConfidenceBar(body, "Skin-tone confidence", r.skin_conf,
                            accent=COLORS["accent_2"]).pack(fill="x")
        card.pack(fill="x", padx=4, pady=6)

        # Shape distribution (mini scores)
        if r.shape_scores:
            card = cards.Card(self.content, title="Shape similarity scores", icon="📈",
                              accent=COLORS["info"])
            body = card.body()
            for shape in FACE_SHAPES:
                cards.ConfidenceBar(body, shape, r.shape_scores.get(shape, 0.0),
                                    accent=COLORS["info"]).pack(fill="x", pady=3)
            card.pack(fill="x", padx=4, pady=6)

        self._guidance_card()

    # ==================================================================
    # Fashion advisor
    # ==================================================================
    def _build_fashion(self):
        self._header("👕", "AI Fashion Advisor", "Colour & outfit ideas for your skin tone",
                     "#F06292")
        r = self._latest
        tone = (r.skin_tone if r and r.skin_tone else "Medium")
        data = fashion_for(tone, r.shape if r else None)

        card = cards.Card(self.content, title="Shirt colours", icon="👔", accent="#F06292")
        cards.swatch_row(card.body(), data["shirt"]).pack(fill="x", padx=4, pady=6)
        card.pack(fill="x", padx=4, pady=6)

        card = cards.Card(self.content, title="T-shirt colours", icon="👕", accent="#EC407A")
        cards.swatch_row(card.body(), data["tshirt"]).pack(fill="x", padx=4, pady=6)
        card.pack(fill="x", padx=4, pady=6)

        card = cards.Card(self.content, title="Formal outfits", icon="🕴️", accent="#7E57C2")
        body = card.body()
        for item in data["formal"]:
            cards.bullet(body, item).pack(fill="x", pady=3)
        card.pack(fill="x", padx=4, pady=6)

        card = cards.Card(self.content, title="Casual outfits", icon="🧢", accent="#26A69A")
        body = card.body()
        for item in data["casual"]:
            cards.bullet(body, item).pack(fill="x", pady=3)
        card.pack(fill="x", padx=4, pady=6)

        self._confidence_card()

    # ==================================================================
    # Glasses recommender
    # ==================================================================
    def _build_glasses(self):
        self._header("🕶️", "AI Glasses Recommender", "Frames matched to your face shape", "#4FC3F7")
        r = self._latest
        if r is None or not r.detected:
            self._no_face()
            return

        card = cards.Card(self.content, title=f"Your face shape · {r.shape}", icon="🧑",
                          accent="#4FC3F7")
        body = card.body()
        cards.para(body, SHAPE_DESCRIPTIONS.get(r.shape, "")).pack(fill="x", pady=(0, 8))
        cards.ConfidenceBar(body, "Shape confidence", r.shape_conf, accent="#4FC3F7").pack(fill="x")
        card.pack(fill="x", padx=4, pady=6)

        for style, reason in glasses_for(r.shape):
            item = ctk.CTkFrame(self.content, fg_color=COLORS["card"], corner_radius=14,
                                border_width=1, border_color=COLORS["border"])
            item.pack(fill="x", padx=4, pady=6)
            item.grid_columnconfigure(1, weight=1)
            img = icons.item_image("glasses", style, 88)
            if img:
                ctk.CTkLabel(item, text="", image=img, width=88, height=88)\
                    .grid(row=0, column=0, rowspan=2, padx=10, pady=10)
            else:
                ctk.CTkLabel(item, text="🕶️", font=font(34)).grid(row=0, column=0, padx=10, pady=10)
            ctk.CTkLabel(item, text=style, font=font(15, True), text_color="#4FC3F7")\
                .grid(row=0, column=1, sticky="sw", pady=(12, 0))
            ctk.CTkLabel(item, text=reason, font=font(12), text_color=COLORS["text_dim"],
                         wraplength=300, justify="left", anchor="w")\
                .grid(row=1, column=1, sticky="nw", pady=(0, 12))

    # ==================================================================
    # Hairstyle advisor
    # ==================================================================
    def _build_hairstyle(self):
        self._header("💇", "AI Hairstyle Advisor", "Cuts that complement your face shape", "#BA68C8")
        r = self._latest
        if r is None or not r.detected:
            self._no_face()
            return

        card = cards.Card(self.content, title=f"Your face shape · {r.shape}", icon="🧑",
                          accent="#BA68C8")
        body = card.body()
        cards.para(body, SHAPE_DESCRIPTIONS.get(r.shape, "")).pack(fill="x", pady=(0, 8))
        cards.ConfidenceBar(body, "Shape confidence", r.shape_conf, accent="#BA68C8").pack(fill="x")
        card.pack(fill="x", padx=4, pady=6)

        for style, reason in hairstyles_for(r.shape):
            item = ctk.CTkFrame(self.content, fg_color=COLORS["card"], corner_radius=14,
                                border_width=1, border_color=COLORS["border"])
            item.pack(fill="x", padx=4, pady=6)
            item.grid_columnconfigure(1, weight=1)
            img = icons.item_image("hairstyles", style, 88)
            if img:
                ctk.CTkLabel(item, text="", image=img, width=88, height=88)\
                    .grid(row=0, column=0, rowspan=2, padx=10, pady=10)
            else:
                ctk.CTkLabel(item, text="💇", font=font(34)).grid(row=0, column=0, padx=10, pady=10)
            ctk.CTkLabel(item, text=style, font=font(15, True), text_color="#BA68C8")\
                .grid(row=0, column=1, sticky="sw", pady=(12, 0))
            ctk.CTkLabel(item, text=reason, font=font(12), text_color=COLORS["text_dim"],
                         wraplength=300, justify="left", anchor="w")\
                .grid(row=1, column=1, sticky="nw", pady=(0, 12))

    # ==================================================================
    # Beard style advisor
    # ==================================================================
    def _build_beard(self):
        self._header("🧔", "AI Beard Style Advisor", "Facial hair ideas for your face shape", "#8D6E63")
        r = self._latest
        if r is None or not r.detected:
            self._no_face()
            return

        card = cards.Card(self.content, title=f"Your face shape · {r.shape}", icon="🧑",
                          accent="#8D6E63")
        body = card.body()
        cards.para(body, SHAPE_DESCRIPTIONS.get(r.shape, "")).pack(fill="x", pady=(0, 8))
        cards.ConfidenceBar(body, "Shape confidence", r.shape_conf, accent="#8D6E63").pack(fill="x")
        card.pack(fill="x", padx=4, pady=6)

        card = cards.Card(self.content, title="Recommended beard styles", icon="🧔",
                          accent="#8D6E63")
        body = card.body()
        for style, reason in beard_for(r.shape):
            cards.bullet(body, f"{style} — {reason}", glyph="🧔",
                         accent="#8D6E63").pack(fill="x", pady=3)
        card.pack(fill="x", padx=4, pady=6)

    # ==================================================================
    # Color palette advisor
    # ==================================================================
    def _build_palette(self):
        self._header("🎨", "AI Color Palette Advisor", "Colours that work with your skin tone", "#FFB454")
        r = self._latest
        tone = (r.skin_tone if r and r.skin_tone else "Medium")
        pal = palette_for(tone)

        card = cards.Card(self.content, title=f"Skin tone · {tone}", icon="🧑",
                          accent="#FFB454")
        body = card.body()
        cards.para(body, f"Undertone: {r.skin_undertone if r else '—'}").pack(fill="x", pady=(0, 6))
        cards.ConfidenceBar(body, "Skin-tone confidence",
                            (r.skin_conf if r else 0.0), accent="#FFB454").pack(fill="x")
        card.pack(fill="x", padx=4, pady=6)

        card = cards.Card(self.content, title="Recommended colours", icon="✅", accent="#4CD98F")
        cards.swatch_row(card.body(), pal["recommended"]).pack(fill="x", padx=4, pady=6)
        card.pack(fill="x", padx=4, pady=6)

        card = cards.Card(self.content, title="Colours to avoid", icon="⛔", accent="#FF6B6B")
        cards.swatch_row(card.body(), pal["avoid"], dim=True).pack(fill="x", padx=4, pady=6)
        card.pack(fill="x", padx=4, pady=6)

        card = cards.Card(self.content, title="Stylist note", icon="💡", accent="#FFB454")
        body = card.body()
        cards.para(body, pal["note"]).pack(fill="x")
        card.pack(fill="x", padx=4, pady=6)

    # ==================================================================
    # Selfie assistant
    # ==================================================================
    def _build_selfie(self):
        self._header("📸", "AI Selfie Assistant", "Guide to the perfect selfie position", "#00D4AA")
        r = self._latest

        state = (r.guidance if r else "Waiting for face")
        glyph = GUIDANCE_GLYPHS.get(state, "🙂")
        perfect = state == "Perfect Position"
        color = COLORS["success"] if perfect else COLORS["warn"]

        card = ctk.CTkFrame(self.content, fg_color=COLORS["card"], corner_radius=16,
                            border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", padx=4, pady=6)
        ctk.CTkLabel(card, text=glyph, font=font(44)).pack(pady=(18, 4))
        ctk.CTkLabel(card, text=state, font=font(22, True), text_color=color).pack()
        cards.para(card, "Follow the steps below one at a time.", ).pack(pady=(6, 18))

        checklist = cards.Card(self.content, title="Live guidance checklist", icon="☑️",
                               accent="#00D4AA")
        body = checklist.body()
        active_labels = [label for label, active in (r.checklist if r else []) if active]
        for label, is_active in (r.checklist if r else []):
            cards.tip_row(body, GUIDANCE_GLYPHS.get(label, "•"), label,
                          active=is_active).pack(fill="x", pady=3)
        if not active_labels:
            cards.para(body, "Waiting for the camera to find a face…").pack(fill="x")
        checklist.pack(fill="x", padx=4, pady=6)

    # ==================================================================
    # Outfit matcher
    # ==================================================================
    def _build_outfit(self):
        self._header("🧥", "AI Outfit Matcher", "Pick a shirt colour for matching pants & shoes", "#FF8A65")
        from utils.recommendations import SHIRT_COLOR_CHOICES

        control = cards.Card(self.content, title="Choose your shirt colour", icon="👕",
                             accent="#FF8A65")
        body = control.body()
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        self._shirt_menu = ctk.CTkOptionMenu(
            row, values=SHIRT_COLOR_CHOICES, command=self._on_shirt_changed,
            font=font(13, True), fg_color=COLORS["bg_alt"], button_color=COLORS["border"],
            button_hover_color=COLORS["card_hover"], dropdown_fg_color=COLORS["card"],
            text_color=COLORS["text"])
        self._shirt_menu.set(self._shirt_selected)
        self._shirt_menu.grid(row=0, column=0, sticky="ew")
        row.grid_columnconfigure(0, weight=1)
        control.pack(fill="x", padx=4, pady=6)

        self._outfit_results()

    def _on_shirt_changed(self, value):
        self._shirt_selected = value
        self._outfit_results()

    def _outfit_results(self):
        # remove previously created result cards (keep the control card)
        for child in self.content.winfo_children():
            if getattr(child, "_is_outfit_result", False):
                child.destroy()

        match = outfit_match(self._shirt_selected)

        card = cards.Card(self.content, title="Matching pants", icon="👖", accent="#8D9EFF")
        body = card.body()
        for p in match["pants"]:
            cards.bullet(body, p, glyph="👖", accent="#8D9EFF").pack(fill="x", pady=2)
        card.pack(fill="x", padx=4, pady=6)
        card._is_outfit_result = True

        card = cards.Card(self.content, title="Matching shoes", icon="👟", accent="#FF8A65")
        body = card.body()
        for s in match["shoes"]:
            cards.bullet(body, s, glyph="👟", accent="#FF8A65").pack(fill="x", pady=2)
        card.pack(fill="x", padx=4, pady=6)
        card._is_outfit_result = True

        card = cards.Card(self.content, title="Finishing accents", icon="⌚", accent="#FFD54F")
        body = card.body()
        cards.bullet(body, match["accent"], glyph="✨", accent="#FFD54F").pack(fill="x", pady=2)
        card.pack(fill="x", padx=4, pady=6)
        card._is_outfit_result = True

    # ==================================================================
    # Occasion look suggestion
    # ==================================================================
    def _build_occasion(self):
        self._header("✨", "AI Occasion Look", "Complete looks for any event", "#FFD54F")

        chips = cards.Card(self.content, title="Choose an occasion", icon="🗓️", accent="#FFD54F")
        body = chips.body()
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        for i, name in enumerate(OCCASIONS):
            btn = ctk.CTkButton(
                row, text=f"{OCCASIONS[name]['icon']} {name}", font=font(12, True),
                fg_color=COLORS["card_hover"] if name == self._occasion_selected else COLORS["bg_alt"],
                hover_color=COLORS["card_hover"], corner_radius=10, height=34,
                command=lambda n=name: self._select_occasion(n))
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3, sticky="ew")
            row.grid_columnconfigure((0, 1, 2), weight=1)
        chips.pack(fill="x", padx=4, pady=6)

        self._occasion_detail()

    def _select_occasion(self, name):
        self._occasion_selected = name
        self._rebuild()

    def _occasion_detail(self):
        look = occasion_look(self._occasion_selected)

        card = cards.Card(self.content, title=f"{look['icon']} {self._occasion_selected} look",
                          icon=look["icon"], accent="#FFD54F")
        body = card.body()
        cards.para(body, look["look"], color_key="text").pack(fill="x", pady=(0, 8))
        for tip in look["tips"]:
            cards.bullet(body, tip, glyph="💡", accent="#FFD54F").pack(fill="x", pady=2)
        card.pack(fill="x", padx=4, pady=6)

        # incorporate current analysis, when available
        r = self._latest
        if r and r.detected:
            card = cards.Card(self.content, title="Personalised touch", icon="✨",
                              accent=COLORS["accent"])
            body = card.body()
            cards.para(body, f"For your {r.shape} face and {r.skin_tone} skin tone, "
                             "prefer colours from the recommended palette when "
                             "picking this look.").pack(fill="x")
            card.pack(fill="x", padx=4, pady=6)

    # ==================================================================
    # Shared: guidance card (used by dashboard)
    # ==================================================================
    def _guidance_card(self):
        r = self._latest
        state = r.guidance if r else "Waiting for face"
        glyph = GUIDANCE_GLYPHS.get(state, "🙂")
        perfect = state == "Perfect Position"
        card = cards.Card(self.content, title="Selfie assistant", icon="📸", accent="#00D4AA")
        body = card.body()
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkLabel(row, text=glyph, font=font(24)).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(row, text=state, font=font(15, True),
                     text_color=COLORS["success"] if perfect else COLORS["warn"]).pack(side="left")
        card.pack(fill="x", padx=4, pady=6)
