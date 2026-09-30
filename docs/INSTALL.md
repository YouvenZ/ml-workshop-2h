# Installing the build toolchain

**Students need none of this.** They open a Colab link and install nothing.
This page is for the machine that *builds* the workshop — the slides, the
11 diagrams and the notebooks. (The two-hour version has no animated clips,
so there is no Manim or ffmpeg to install.)

---

## The short version

| | Linux / macOS | Windows |
|---|---|---|
| **Install once** | `bash tools/setup.sh` | `.\tools\setup.ps1` |
| **Build everything** | `bash tools/build.sh` | `.\tools\build.ps1` |
| **Build and preview** | `bash tools/build.sh --serve` | `.\tools\build.ps1 -Serve` |

Both setup scripts need **conda** already present, and neither installs
LaTeX. Details below.

---

## What the pipeline actually needs

| Component | Used for | Comes from |
|---|---|---|
| **conda** (Miniforge) | the `mlws2h` environment | you install it first |
| **Python 3.12** | everything | the conda env |
| **poppler** (`pdftocairo`, `pdftoppm`) | PDF → SVG and PNG | the conda env |
| **Quarto** | the slide deck and site | setup script |
| **Inter** typeface | slides and diagrams matching | setup script |
| **LaTeX** with `lualatex` | rebuilding the 11 TikZ diagrams | **you install it** |
| numpy · pandas · seaborn · scikit-learn | notebooks | the conda env |
| nbformat · nbclient · ipykernel | notebook generation and checks | the conda env |

> **LaTeX is optional.** The rendered `.svg` and `.png` diagrams are committed
> to the repo. You only need LaTeX if you want to *change* a diagram. Without
> it, `build_assets.py` skips diagrams with a clear message and everything
> else still builds.

---

## Linux / macOS

### 1. conda

Miniforge, if you do not already have conda:

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

### 2. LaTeX — only if you will edit diagrams

```bash
# Debian / Ubuntu
sudo apt install texlive-latex-extra texlive-luatex texlive-fonts-recommended

# Fedora
sudo dnf install texlive-scheme-medium texlive-luatex

# macOS
brew install --cask mactex-no-gui
```

### 3. Everything else

```bash
bash tools/setup.sh
```

That installs Quarto into `~/.local`, creates the `mlws2h` conda environment,
installs the Inter typeface into `~/.local/share/fonts`, and adds the
countdown Quarto extension if it is missing. Nothing goes outside your home directory and nothing
needs `sudo`.

Add this to your shell profile if it is not there already:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 4. Build

```bash
conda activate mlws2h
bash tools/build.sh
```

---

## Windows

PowerShell 5.1 (built in) or PowerShell 7 both work. Run everything from the
repository root.

### 1. conda

Install **Miniforge** from
<https://github.com/conda-forge/miniforge#miniforge3>, then once:

```powershell
conda init powershell
```

and **reopen PowerShell**. Without this, `conda activate` does not work in a
PowerShell session and the build script will tell you so.

### 2. LaTeX — only if you will edit diagrams

Install **MiKTeX** from <https://miktex.org/download>. Accept the default
"install missing packages on the fly" setting — the diagrams pull in TikZ
libraries and `fontspec`, and MiKTeX will fetch them the first time.

### 3. Everything else

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\setup.ps1
```

That installs Quarto (the portable `.zip`, into `%LOCALAPPDATA%\Programs\Quarto`,
added to your **user** PATH — no admin rights), creates the `mlws2h` environment
from `environment-windows.yml`, installs the Inter typeface for your user,
and adds the countdown Quarto extension if it is missing.

### 4. Build

```powershell
conda activate mlws2h
.\tools\build.ps1
```

### If PowerShell refuses to run the scripts

The default execution policy blocks local scripts. Either run them one-off:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\build.ps1
```

or allow signed and local scripts for your user, once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## What the build does

`build.sh` and `build.ps1` run the same five steps, in the same order:

| Step | Command underneath | Fails the build when |
|---|---|---|
| 1. Assets | `tools/build_assets.py` | a diagram will not render |
| 2. Asset check | `tools/check_assets.py` | a diagram the deck uses is missing |
| 3. Notebooks | `tools/build_notebooks.py` | generation errors |
| 4. Notebook run | `tools/check_notebooks.py` | **a hosted dataset URL is down** |
| 5. Site | `quarto render` | the deck will not build |

Step 4 is the one to run the day before a workshop. It executes NB0 and every
solution cell against the live Penguins and Titanic URLs, so a dataset that
moved is caught at your desk rather than at 0:03 in front of a room.

### Useful flags

| | Linux / macOS | Windows |
|---|---|---|
| Skip the assets | `--skip-assets` | `-SkipAssets` |
| Rebuild every asset | `--force` | `-Force` |
| Skip the notebook run and checks | `--quick` | `-Quick` |
| Serve when done | `--serve` | `-Serve` |

`--skip-assets` is what you want while editing slides; the assets only
change when you edit `assets/tikz/*.tex`.

### Building assets directly

```bash
python tools/build_assets.py --list            # what is out of date
python tools/build_assets.py --clean           # drop intermediates
```

`make -C assets` still works on Linux and macOS — the Makefile is a thin
wrapper around the same Python script, so the two cannot drift apart. There
is no `make` on the Windows path; use the script or `build.ps1`.

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `'lualatex' not found` | No LaTeX. Diagrams cannot be rebuilt; everything else still works. Install TeX Live or MiKTeX only if you need to edit one. |
| `'pdftocairo' not found` | poppler missing from the env: `conda install -c conda-forge poppler` |
| `conda env 'mlws2h' not found` | Run the setup script for your platform. |
| `conda activate` does nothing (Windows) | `conda init powershell`, then reopen PowerShell. |
| Quarto renders but equations show as `\[ ... \]` | KaTeX is vendored in `slides/katex/`. Check that directory survived the clone. |
| Fonts look wrong in the diagrams | Inter is missing. Re-run the setup script. Everything still builds; it just stops matching the slides. |
