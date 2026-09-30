# Tech stack — 2-hour version

| Need | Tool |
|---|---|
| Slides | **Quarto → reveal.js** (`format: revealjs`), one `slides/index.qmd` |
| Student code | **Google Colab** — every line students type runs there |
| Animations | **Manim CE** → 11 MP4 clips, played once per visit by `slides/video-once.html` |
| Diagrams | **TikZ** → SVG (slides) and PNG (embedded in the notebooks) |
| Interactive | `assets/interactive/correlation-playground.html` (plain JS, no deps) |
| Exercise timers | `quarto-countdown` extension, committed under `slides/_extensions/` |
| Equations | KaTeX, self-hosted in `slides/katex/` (no CDN on lecture-hall wifi) |
| Hosting | **GitHub Pages**, deployed by `.github/workflows/publish.yml` |

## Clips

The clips are the four-hour set, unchanged: 1280×720, ≤15 s, ≤4 MB,
~4.5 MB for all eleven. They are committed pre-rendered in `assets/rendered/`,
so neither CI nor a presenter needs Manim. `tools/check_assets.py` enforces the
size and duration budget. Rebuild one with:

```bash
python tools/build_assets.py --scene OverfitUnderfit
```

Each clip plays **once** when its slide arrives and stops on its last frame —
a looping clip behind a speaker fights for the room's attention. Click it or
press ↻ replay to run it again.

## What the four-hour version has that this one does not

**quarto-live / Pyodide cells** in the slides. They fetch ~10 MB of
WebAssembly and invite the room to play for minutes. In two hours every
keystroke happens in Colab, so the deck stays a plain static reveal.js site.
Because nothing executes at render time, CI needs only Quarto.

## Pipeline

```
assets/manim/scenes.py ──manim──▶ assets/rendered/*.mp4 ─────────────────────┐
assets/tikz/*.tex ──lualatex──▶ assets/rendered/*.svg ───────────────────────┤
                            └─▶ assets/rendered/png/*.png ──▶ notebooks/*.ipynb │
slides/index.qmd ──────────────────────────────────────────▶ quarto render ──▶ _site/ ──▶ GitHub Pages
```

## CI (`publish.yml`)

| Job | Fails when |
|---|---|
| `verify-notebooks` | a committed notebook differs from its generator, or a solution cell raises |
| `build-deploy` | the deck will not render, or a clip/diagram is missing or over budget |
| `deploy` | — runs on push to `main` only, after both jobs pass |
