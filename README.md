# AI Smart Style Advisor

A modern, dark-themed desktop application built in Python that uses the
webcam to analyse a face **in real time** and offer *style suggestions*
based only on visual features (approximate face shape and skin tone).

> **Important** — The system never tries to identify a person's
> personality, intelligence, character or emotions from their face.
> Every recommendation is a *suggestion* generated from geometric
> measurements and predefined fashion rules only.

## Features (8 modules)

| Module | What it does |
| --- | --- |
| 1. AI Fashion Advisor | Shirt / T-shirt colours, formal & casual outfit ideas |
| 2. AI Glasses Recommender | Frames (Round, Rectangle, Square, Aviator, Wayfarer…) by face shape |
| 3. AI Hairstyle Advisor | Crew Cut, Fade, Pompadour, Undercut, Side Part and more |
| 4. AI Beard Style Advisor | Clean Shave, Stubble, French Beard, Full Beard, Goatee and more |
| 5. AI Color Palette Advisor | Skin-tone estimate → recommended colours vs colours to avoid |
| 6. AI Selfie Assistant | Move Left/Right/Closer/Back, Look Straight, Smile, Improve Lighting, Perfect Position |
| 7. AI Outfit Matcher | Pants + shoe colours matched to a selected shirt colour |
| 8. AI Occasion Look | College, Interview, Wedding, Party, Casual |

The interface includes a live webcam preview, face-detection box, facial
landmarks, a right-side recommendation panel, confidence indicators and
a dashboard.

## Tech stack

- Python 3.10+
- OpenCV (`opencv-python`)
- MediaPipe Tasks (`mediapipe`) — `FaceLandmarker` (468 landmarks)
- Pillow (image handling / generated assets)
- CustomTkinter (modern dark UI)
- NumPy

## Project structure

```
college project/
├── main.py                     # Entry point
├── requirements.txt
├── assets/
│   ├── generate_assets.py      # Generates icons + item images
│   ├── icons/                  # Category icons (PNG)
│   ├── glasses/                # Glasses-style illustrations
│   ├── hairstyles/             # Hairstyle illustrations
│   └── outfits/                # Occasion-look illustrations
├── models/
│   ├── face_analyzer.py        # MediaPipe FaceLandmarker wrapper
│   └── face_landmarker.task    # Downloaded model (~3.7 MB)
├── ui/
│   ├── app.py                  # Main window + refresh loop
│   ├── camera_widget.py        # Webcam preview + overlay
│   ├── recommendation_panel.py # Right-side panel + all views
│   ├── cards.py                # Reusable UI cards/chips/swatches
│   ├── icons.py                # Icon loader
│   └── theme.py                # Dark theme bootstrap
└── utils/
    ├── capture.py              # Background camera thread
    ├── geometry.py             # Face measurements + shape classifier
    ├── skintone.py             # Skin-tone estimation
    ├── recommendations.py      # All style rules (8 modules)
    ├── selfie_assistant.py     # Camera-position guidance
    ├── colors.py               # Colour-name -> hex lookup
    └── config.py               # Design tokens + paths
```

## Setup & run

```bash
pip install -r requirements.txt

# download the MediaPipe model (already included in this repo)
# https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
#   -> save as models/face_landmarker.task

py assets/generate_assets.py     # optional: regenerate icon images
py main.py                       # desktop app (webcam window)
```

Allow camera access when the OS asks. Position your face in the frame
and the right panel fills with recommendations.

## Web deployment (open on phone / another lab PC)

The same engine can run as a small local web server. The lab PC's webcam
streams the live analysis to **any device on the same Wi-Fi**.

```bash
py web_server.py
```

Then open one of the printed links from a phone / lab PC, e.g.:

```
http://10.50.221.1:8000      # (printed on start — your lab PC's IP)
http://localhost:8000        # on the lab PC itself
```

- Phone and lab PC must be on the **same network** (same Wi-Fi / hotspot).
- The lab PC's webcam feeds the video — visitors watch it on their screen.
- Do **not** run `main.py` at the same time (both would fight over the webcam).
- Windows Firewall may block phone access. As **Administrator** run once:
  ```
  netsh advfirewall firewall add rule name="StyleAdvisor" dir=in action=allow protocol=TCP localport=8000
  ```
- Web UI lives in `ui/web/index.html`; data comes from the `/api/*` JSON endpoints
  (`/api/status`, `/api/recommendations`, `/api/outfit`, `/api/occasion`).

## Deploy to Render (permanent public URL)

The main page (`/`) makes **each visitor use their own webcam** — the
browser captures frames and the server (this app) analyses them. That
means it works perfectly as a real cloud deployment: visitors anywhere,
laptop can even be switched off.

1. Push this repo to GitHub (the model `models/face_landmarker.task` is
   already committed).
2. Sign in at https://render.com using your GitHub account.
3. Dashboard → **New +** → **Blueprint** → select this repo → **Apply**.
   (Or: New + → Web Service → pick repo → build `pip install -r
   requirements.txt` → start `gunicorn web_server:app --bind
   0.0.0.0:$PORT --workers 1 --threads 4 --timeout 180`.)
4. Render builds and gives you a permanent URL like
   `https://ai-style-advisor.onrender.com`.
5. Open that URL on any device → allow camera → done.

Notes:
- Free tier sleeps after ~15 min idle; the first visit after idle takes
  ~1 min to wake up.
- `/lab` (the laptop-camera stream demo) needs a webcam on the server, so
  it only works in local mode — not on Render.
- A visitor's camera requires HTTPS, which Render provides automatically.

## How the analysis works

1. **Facial landmarks** — MediaPipe `FaceLandmarker` returns 468 3D
   landmarks per face.
2. **Face shape** — distances between landmark pairs (forehead temples,
   cheekbones, jaw, chin, face height) feed a small weighted fuzzy
   classifier → Oval / Round / Square / Rectangle / Heart / Diamond,
   with a confidence score.
3. **Skin tone** — several skin patches (forehead, cheeks, jaw) are
   sampled, lighting-normalised, and mapped to Fair / Light / Medium /
   Tan / Deep with a confidence score and warm/cool undertone.
4. **Selfie guidance** — face size/position in the frame, head roll,
   smile score (blendshape) and scene brightness select one guidance
   message.

## Ethics / disclaimer

Face-shape and skin-tone categories are approximate and intended only
for *style ideas*. Style is personal — treat every suggestion as an
inspiration, not a rule, and never as a judgement of character.
