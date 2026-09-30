#!/usr/bin/env bash
# Run the whole workshop pipeline. Linux and macOS.
#
#   bash tools/build.sh                 assets -> notebooks -> site
#   bash tools/build.sh --serve         ...then serve it on :8777
#   bash tools/build.sh --skip-assets   site only (assets already built)
#   bash tools/build.sh --force         rebuild every asset from scratch
#   bash tools/build.sh --quick         skip Manim (slowest step) and checks
#
# Windows: use tools\build.ps1 instead — same steps, same order.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

ENV_NAME="mlws2h"
PORT=8777
SERVE=0; SKIP_ASSETS=0; FORCE=""; QUICK=0

for arg in "$@"; do
  case "$arg" in
    --serve)       SERVE=1 ;;
    --skip-assets) SKIP_ASSETS=1 ;;
    --force)       FORCE="--force" ;;
    --quick)       QUICK=1 ;;
    -h|--help)     sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown option: $arg (try --help)"; exit 2 ;;
  esac
done

step()  { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
ok()    { printf '    \033[32m%s\033[0m\n' "$*"; }
die()   { printf '\n\033[31mFAILED: %s\033[0m\n' "$*" >&2; exit 1; }

# ---------------------------------------------------------------- env ----
if [ -z "${CONDA_PREFIX:-}" ] || [ "$(basename "${CONDA_PREFIX:-}")" != "$ENV_NAME" ]; then
  if command -v conda >/dev/null 2>&1; then
    # shellcheck disable=SC1091
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$ENV_NAME" 2>/dev/null \
      || die "conda env '$ENV_NAME' not found. Run: bash tools/setup.sh"
  else
    die "conda not found. See docs/INSTALL.md"
  fi
fi
ok "environment: $ENV_NAME ($(python --version 2>&1))"

command -v quarto >/dev/null 2>&1 || die "quarto not on PATH. Run: bash tools/setup.sh"

# ------------------------------------------------------------- assets ----
if [ "$SKIP_ASSETS" -eq 0 ]; then
  step "Building visual assets"
  if [ "$QUICK" -eq 1 ]; then
    python tools/build_assets.py --tikz $FORCE || die "diagram build"
    ok "diagrams only (--quick skipped the clips)"
  else
    python tools/build_assets.py $FORCE || die "asset build"
  fi

  if [ "$QUICK" -eq 0 ]; then
    step "Checking asset sizes and durations"
    python tools/check_assets.py || die "an asset is outside the spec"
  fi
else
  ok "skipping assets"
fi

# ---------------------------------------------------------- notebooks ----
step "Generating notebooks"
python tools/build_notebooks.py || die "notebook generation"

if [ "$QUICK" -eq 0 ]; then
  step "Executing notebooks (catches a dead dataset URL)"
  python tools/check_notebooks.py || die "a notebook cell raised"
fi

# --------------------------------------------------------------- site ----
step "Rendering the site"
quarto render || die "quarto render"
ok "site written to _site/"

# -------------------------------------------------------------- serve ----
if [ "$SERVE" -eq 1 ]; then
  step "Serving on http://127.0.0.1:$PORT"
  echo "    slides:  http://127.0.0.1:$PORT/slides/index.html"
  echo "    Ctrl-C to stop"
  exec python -m http.server "$PORT" --bind 127.0.0.1 -d _site
fi

printf '\n\033[1mDone.\033[0m  Preview with:\n'
printf '    bash tools/build.sh --skip-assets --serve\n'
printf '    quarto preview slides/index.qmd     # hot reload while editing\n'
