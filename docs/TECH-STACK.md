# Tech stack — 2-hour version

| Need | Tool |
|---|---|
| Slides | **Quarto → reveal.js** (`format: live-revealjs`), one `slides/index.qmd` |
| Live code | **quarto-live / Pyodide** — 3 runnable cells in the slides |
| Student code | **Google Colab** — every line students type runs there |
| Animations | **Manim CE** → 11 MP4 clips, played once per visit by `slides/video-once.html` |
| Diagrams | **TikZ** → SVG (slides) and PNG (embedded in the notebooks) |
| Interactive | `assets/interactive/correlation-playground.html` (plain JS, no deps) |
| Exercise timers | `quarto-countdown` extension, committed under `slides/_extensions/` |
| Equations | KaTeX, self-hosted in `slides/katex/` (no CDN on lecture-hall wifi) |
| Hosting | **GitHub Pages**, deployed by `.github/workflows/publish.yml` |

## Clips

Eleven self-contained micro-lessons, rewritten for the two-hour deck:
1280×720 @30fps, ≤30 s, ≤4 MB (~12 MB for all eleven). Every scene subclasses
`Lesson` in `assets/manim/scenes.py`, which gives them one grammar — a
question as the title, `say()` captions held long enough to read, and a
`takeaway()` box as the final frame. All on-screen numbers are computed from
`data/` at render time, not typed in. On the slide, the clip fills the whole
slide (`{.clip-slide}` hides the slide heading — the clip carries its own). They are committed pre-rendered in `assets/rendered/`,
so neither CI nor a presenter needs Manim. `tools/check_assets.py` enforces the
size and duration budget. Rebuild one with:

```bash
python tools/build_assets.py --scene OverfitUnderfit
```

Each clip plays **once** when its slide arrives and stops on its last frame —
a looping clip behind a speaker fights for the room's attention. Click it or
press ↻ replay to run it again.

## Live Python in the slides

Three `{pyodide}` cells (quarto-live, committed under `slides/_extensions/`)
run real Python in the browser — no server:

| Slide | Cell | Packages |
|---|---|---|
| 7 | change a value, read the error | none |
| 14 | vectorise and mask a NumPy array | numpy (preloaded) |
| 48 | **pick your own K** — KNN on the real penguins | pandas + scikit-learn (fetched on first import) |

The penguins CSV is copied into the in-browser filesystem at start-up
(`pyodide: resources:` in the deck header), so the cell reads
`data/penguins.csv` without a network call from Python.

> The first load downloads Python (~10 MB) and took ~2 minutes in testing;
> scikit-learn adds ~1 minute on first import. Warm both before the room fills
> — see PREFLIGHT.md. Nothing load-bearing lives in an in-slide cell.

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
