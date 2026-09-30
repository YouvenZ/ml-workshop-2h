#!/usr/bin/env bash
# One-command setup for the authoring machine.
#
#   bash tools/setup.sh
#
# Installs, if missing: Quarto (user-local), the conda build environment,
# the Inter typeface, and the two Quarto extensions. Everything lands under
# $HOME — no sudo, nothing touched outside your user account.
#
# Students need NONE of this. This is only for building the material.
#
# Windows: use tools\setup.ps1 instead. See docs/INSTALL.md.
# LaTeX is NOT installed here — it is only needed to rebuild the diagrams,
# whose rendered SVG/PNG are committed.
set -euo pipefail

QUARTO_VERSION="1.10.18"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

# ---------------------------------------------------------------- Quarto --
if command -v quarto >/dev/null 2>&1; then
  say "Quarto already installed: $(quarto --version)"
else
  say "Installing Quarto ${QUARTO_VERSION} into ~/.local"
  mkdir -p "$HOME/.local/opt" "$HOME/.local/bin"
  tmp="$(mktemp -d)"
  curl -fsSL -o "$tmp/quarto.tar.gz" \
    "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"
  tar -xzf "$tmp/quarto.tar.gz" -C "$HOME/.local/opt/"
  ln -sf "$HOME/.local/opt/quarto-${QUARTO_VERSION}/bin/quarto" "$HOME/.local/bin/quarto"
  rm -rf "$tmp"
  export PATH="$HOME/.local/bin:$PATH"
  echo "Add this to your shell profile if it is not already there:"
  echo '    export PATH="$HOME/.local/bin:$PATH"'
fi

# ------------------------------------------------------------------ conda --
if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found. Install Miniforge, then re-run this script:"
  echo "  https://github.com/conda-forge/miniforge"
  exit 1
fi
# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"

if conda env list | grep -qE '^mlws2h\s'; then
  say "conda env 'mlws2h' already exists — updating"
  conda env update -n mlws2h -f "$REPO/environment.yml" --prune
else
  say "Creating conda env 'mlws2h' (this takes a few minutes)"
  conda env create -f "$REPO/environment.yml"
fi

# ------------------------------------------------------------------- Inter --
# The slides, the TikZ diagrams and the Manim clips all specify Inter. If it
# is missing everything still builds, but the three stop matching each other.
if fc-list : family 2>/dev/null | grep -qi '^Inter$'; then
  say "Inter already installed"
else
  say "Installing the Inter typeface into ~/.local/share/fonts"
  tmp="$(mktemp -d)"
  curl -fsSL -o "$tmp/inter.zip" \
    "https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip"
  unzip -oq "$tmp/inter.zip" -d "$tmp/inter"
  mkdir -p "$HOME/.local/share/fonts/Inter"
  # static upright weights: Pango picks weights far more reliably from these
  # than from the variable font
  find "$tmp/inter/extras/otf" -name 'Inter-*.otf' ! -name '*Italic*' \
       -exec cp {} "$HOME/.local/share/fonts/Inter/" \;
  cp "$tmp/inter/extras/otf/Inter-Italic.otf" "$HOME/.local/share/fonts/Inter/" 2>/dev/null || true
  fc-cache -f "$HOME/.local/share/fonts" >/dev/null
  rm -rf "$tmp"
fi

# ------------------------------------------------------- Quarto extensions --
# Committed to git, so this is only needed on a fresh clone that dropped them.
if [ ! -d "$REPO/slides/_extensions/r-wasm/live" ]; then
  say "Installing quarto-live"
  (cd "$REPO/slides" && quarto add r-wasm/quarto-live --no-prompt)
fi
if [ ! -d "$REPO/slides/_extensions/gadenbuie/countdown" ]; then
  say "Installing quarto-countdown"
  # NB: the extension lives in the repo's quarto/ subdirectory, not at its root
  (cd "$REPO/slides" && quarto add gadenbuie/countdown/quarto --no-prompt)
fi

# ------------------------------------------------------------------- LaTeX --
if ! command -v lualatex >/dev/null 2>&1; then
  cat <<'MSG'

WARNING: lualatex not found — the 11 TikZ diagrams cannot be rebuilt.
Install TeX Live (scheme-medium or larger) if you need to change them.
The already-rendered SVGs in assets/rendered/ are committed, so the slides
still build without it.
MSG
fi

say "Done."
cat <<'MSG'
Next:
    conda activate mlws2h
    bash tools/build.sh            # the whole pipeline
    bash tools/build.sh --serve    # ...and serve it on :8777

Individual steps, if you prefer:
    python tools/build_assets.py   # the 22 visual assets (make -C assets also works)
    python tools/build_notebooks.py
    python tools/check_notebooks.py
    quarto preview slides/index.qmd
MSG
