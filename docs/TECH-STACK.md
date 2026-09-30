# Tech stack — 2-hour version

| Need | Tool |
|---|---|
| Slides | **Quarto → reveal.js** (`format: revealjs`), one `slides/index.qmd` |
| Student code | **Google Colab** — every line students type runs there |
| Diagrams | **TikZ** → SVG (slides) and PNG (embedded in the notebooks) |
| Exercise timers | `quarto-countdown` extension, committed under `slides/_extensions/` |
| Equations | KaTeX, self-hosted in `slides/katex/` (no CDN on lecture-hall wifi) |
| Hosting | **GitHub Pages**, deployed by `.github/workflows/publish.yml` |

## What the four-hour version has that this one does not

- **Manim clips** (11 MP4s). Each one was worth its 10–15 seconds when the
  hour had room to talk over it. At two hours, a static diagram or a
  three-row table carries the same idea in the time it takes to say it.
- **quarto-live / Pyodide cells** in the slides. They fetch ~10 MB of
  WebAssembly and invite the room to play. The fast version keeps every
  keystroke in Colab, so the deck is a plain static reveal.js site that
  loads instantly.

Because nothing executes at render time, CI needs only Quarto: no Jupyter,
no LaTeX, no Manim. The diagrams are committed pre-rendered in
`assets/rendered/`; rebuild them with `python tools/build_assets.py` only if
you edit a `.tex` file.

## Pipeline

```
assets/tikz/*.tex ──lualatex/pdftocairo──▶ assets/rendered/*.svg ─┐
                                    └────▶ assets/rendered/png/*.png ──▶ tools/build_notebooks.py ──▶ notebooks/*.ipynb
slides/index.qmd ─────────────────────────────────────────────────┴──▶ quarto render ──▶ _site/ ──▶ GitHub Pages
```

## CI (`publish.yml`)

| Job | Fails when |
|---|---|
| `verify-notebooks` | a committed notebook differs from its generator, or a solution cell raises (e.g. a dataset URL moved) |
| `build-deploy` | the deck will not render, or a diagram it uses is missing |
| `deploy` | — runs on push to `main` only, after both jobs pass |
