#!/usr/bin/env python3
"""
Build every visual asset — cross-platform.

    python tools/build_assets.py              # everything that is out of date
    python tools/build_assets.py --tikz       # same thing (kept for muscle memory)
    python tools/build_assets.py --force      # rebuild even if up to date
    python tools/build_assets.py --list       # show what would be built

This is the single implementation of the asset build. `assets/Makefile` is a
thin wrapper around it so `make -C assets` still works on Linux and macOS.

Why Python and not only the Makefile: GNU Make on Windows runs recipes through
cmd.exe, so the logic lives here and both the Makefile and build.ps1 call it.

Outputs, all into assets/rendered/:
    <asset>.svg        diagrams, for the slides (glyphs as paths, no fonts)
    png/<asset>.png    diagrams, for the notebooks (base64-embedded there)

The two-hour version has no animated clips: the four-hour version's Manim
scenes were cut together with the explanation time they needed.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIKZ = ROOT / "assets" / "tikz"
RENDERED = ROOT / "assets" / "rendered"
PNG_DIR = RENDERED / "png"

class Missing(Exception):
    pass


def need(tool, hint):
    """Resolve an executable, or explain how to get it."""
    path = shutil.which(tool)
    if not path:
        raise Missing(f"'{tool}' not found on PATH.\n    {hint}")
    return path


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-15:])
        raise RuntimeError(f"command failed: {' '.join(str(c) for c in cmd)}\n{tail}")
    return r


def stale(target, source):
    return not target.exists() or target.stat().st_mtime < source.stat().st_mtime


# --------------------------------------------------------------------------
# diagrams
# --------------------------------------------------------------------------
def build_tikz(force=False, dry=False):
    lualatex = need("lualatex",
                    "Install TeX Live (Linux/macOS) or MiKTeX (Windows). "
                    "See docs/INSTALL.md.")
    # pdftocairo, not dvisvgm: dvisvgm's PDF path needs Ghostscript < 10.01
    # or mutool, and current distros ship neither.
    pdftocairo = need("pdftocairo",
                      "poppler-utils. `conda install -c conda-forge poppler` "
                      "works on every platform.")
    pdftoppm = need("pdftoppm", "Ships with poppler, same as pdftocairo.")

    preamble = TIKZ / "_preamble.tex"
    sources = sorted(p for p in TIKZ.glob("*.tex") if p.name != "_preamble.tex")
    if not sources:
        print("  no .tex files found"); return 0

    built = 0
    RENDERED.mkdir(parents=True, exist_ok=True)
    PNG_DIR.mkdir(parents=True, exist_ok=True)

    for tex in sources:
        name = tex.stem
        svg, png = RENDERED / f"{name}.svg", PNG_DIR / f"{name}.png"
        if not force and not stale(svg, tex) and not stale(svg, preamble) \
                and png.exists():
            continue
        print(f"  tikz   {name}")
        built += 1
        if dry:
            continue
        # One lualatex run feeds both outputs.
        run([lualatex, "-interaction=nonstopmode", "-halt-on-error", tex.name],
            cwd=TIKZ)
        pdf = TIKZ / f"{name}.pdf"
        run([pdftocairo, "-svg", str(pdf), str(svg)])
        run([pdftoppm, "-png", "-r", "130", "-singlefile",
             str(pdf), str(PNG_DIR / name)])
        for ext in (".aux", ".log", ".pdf", ".out"):
            (TIKZ / f"{name}{ext}").unlink(missing_ok=True)
    return built


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tikz", action="store_true", help="diagrams only")
    ap.add_argument("--force", action="store_true", help="ignore timestamps")
    ap.add_argument("--list", action="store_true",
                    help="show what is out of date, build nothing")
    ap.add_argument("--clean", action="store_true",
                    help="remove build intermediates (not rendered/)")
    args = ap.parse_args()

    if args.clean:
        for ext in ("*.aux", "*.log", "*.pdf", "*.out"):
            for f in TIKZ.glob(ext):
                f.unlink()
        print("cleaned build intermediates")
        return 0

    t0 = time.time()
    total = 0
    try:
        print("diagrams:")
        n = build_tikz(args.force, args.list)
        total += n
        print(f"  {n} rebuilt" if not args.list else f"  {n} out of date")
    except Missing as e:
        print(f"\nMISSING PREREQUISITE\n    {e}", file=sys.stderr)
        return 2
    except RuntimeError as e:
        print(f"\nBUILD FAILED\n{e}", file=sys.stderr)
        return 1

    if not args.list:
        print(f"\n{total} asset(s) rebuilt in {time.time() - t0:.0f}s"
              if total else "\neverything already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
