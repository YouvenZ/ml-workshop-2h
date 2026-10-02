# Python & Machine Learning Workshop — 2 hours

A 2-hour, zero-prerequisite workshop taking CS/STEM university students from
no Python to a trained, evaluated classifier. Browser only — students install
nothing.

By **Dr. Rachid Zeghlache**, Assistant Professor of Artificial Intelligence,
American University in Dubai.

This is the **fast cut of the four-hour workshop**: the same four steps in the
same order (Python → explore → first model → compare & challenge), all 11
animated clips and live Python in the slides, with 114 slides condensed to 56 and the long explanations moved
into the notebooks. See [what changed](docs/WORKSHOP-PLAN.md#what-changed-from-the-four-hour-version).

**[▶ View the slides](https://YouvenZ.github.io/ml-workshop-2h/slides/)**

## Notebooks

| Notebook | Covers | |
|---|---|---|
| NB0 — Warm-up | 20-min pre-work, sent T−3 days — **expected** in the 2h format | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YouvenZ/ml-workshop-2h/blob/main/notebooks/NB0-warmup.ipynb) |
| NB1 — Python & Data | 0:00 – 0:55 | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YouvenZ/ml-workshop-2h/blob/main/notebooks/NB1-python-data.ipynb) |
| NB2 — Machine Learning | 1:00 – 2:00 | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YouvenZ/ml-workshop-2h/blob/main/notebooks/NB2-machine-learning.ipynb) |
| NB-SOLUTIONS | Released at the end | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YouvenZ/ml-workshop-2h/blob/main/notebooks/NB-SOLUTIONS.ipynb) |

> **NB2 loads its own clean data in cell 1.** A student whose NB1 is broken at
> 0:55 still starts the ML hour on time with everyone else.

## For instructors

- **[Workshop plan](docs/WORKSHOP-PLAN.md)** — minute-by-minute, cut list, what changed from 4h.
- **[Pre-flight checklist](docs/PREFLIGHT.md)** — T−3 days, T−1 day, T−0.
- **[Install guide](docs/INSTALL.md)** — build toolchain for Linux, macOS and Windows.

## Repository layout

```
├── index.qmd               landing page for the published site
├── _quarto.yml             project config (root, so ../assets/ resolves)
├── slides/index.qmd        the deck — 56 slides, 12 clips, 3 live Python cells
├── slides/katex/           self-hosted KaTeX, so equations never need a CDN
├── notebooks/*.ipynb       BUILD OUTPUT — edit tools/build_notebooks.py
├── assets/
│   ├── tikz/*.tex          11 static diagrams (SVG for slides, PNG for notebooks)
│   ├── manim/scenes.py     11 animated clips, one file
│   ├── interactive/        the correlation playground (slide 26, and the break)
│   └── rendered/           committed build output the slides point at
├── data/                   backup CSVs, in case a hosted URL is down
└── tools/                  build + verification scripts
```

## Building it

| | Linux / macOS | Windows |
|---|---|---|
| Install once | `bash tools/setup.sh` | `.\tools\setup.ps1` |
| Build everything | `bash tools/build.sh` | `.\tools\build.ps1` |
| Build and preview | `bash tools/build.sh --serve` | `.\tools\build.ps1 -Serve` |

While editing slides, `quarto preview slides/index.qmd` hot-reloads the deck.

> **The notebooks are generated.** Edit `tools/build_notebooks.py`, never the
> `.ipynb` files. CI fails the build if a committed notebook does not match
> its generator.

## Deploying (GitHub Pages)

`.github/workflows/publish.yml` verifies the notebooks, renders the site with
Quarto and deploys `_site/` to GitHub Pages on every push to `main`.

One-time setup:

1. Create an empty **public** repo on GitHub named `ml-workshop-2h`, then:
   ```bash
   git remote add origin git@github.com:YouvenZ/ml-workshop-2h.git
   git push -u origin main
   ```
2. On GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. The site appears at `https://YouvenZ.github.io/ml-workshop-2h/`.

**Forking it to another account?** Replace `YouvenZ` in `tools/build_notebooks.py`
(`GH_USER`, then re-run it), `README.md`, `index.qmd` and `_quarto.yml` (`site-url`).

## License

Content (plan, slides, diagrams): **CC BY 4.0**
Code (notebooks, Manim scripts, tools): **MIT**
