#!/usr/bin/env python3
"""
Build every visual asset — cross-platform.

    python tools/build_assets.py              # everything that is out of date
    python tools/build_assets.py --tikz       # the 11 diagrams only
    python tools/build_assets.py --manim      # the 10 clips only
    python tools/build_assets.py --force      # rebuild even if up to date
    python tools/build_assets.py --list       # show what would be built

This is the single implementation of the asset build. `assets/Makefile` is a
thin wrapper around it so `make -C assets` still works on Linux and macOS.

Why Python and not the Makefile: the Makefile's manim target used a POSIX
shell loop with bash parameter expansion, plus `find` and `cp`. GNU Make on
Windows runs recipes through cmd.exe, where none of that exists. Rather than
keep two divergent build definitions, the logic lives here and both the
Makefile and the PowerShell script call it.

Outputs, all into assets/rendered/:
    <asset>.svg        diagrams, for the slides (glyphs as paths, no fonts)
    png/<asset>.png    diagrams, for the notebooks (base64-embedded there)
    <asset>.mp4        clips, 1280x720 @30fps
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
MANIM_FILE = ROOT / "assets" / "manim" / "scenes.py"
RENDERED = ROOT / "assets" / "rendered"
PNG_DIR = RENDERED / "png"
MEDIA = ROOT / "assets" / "media"

# scene name -> output asset name
CLIPS = {
    "ForLoopWalkthrough": "asset_03_for_loop",
    "Broadcasting": "asset_05_broadcasting",
    "SplitApplyCombine": "asset_08_split_apply_combine",
    "TrainTestSplit": "asset_12b_train_test_split",
    "OverfitUnderfit": "asset_13_overfitting",
    "DecisionBoundary": "asset_14_decision_boundary",
    "KNNMechanism": "asset_16_knn",
    "EffectOfK": "asset_17_effect_of_k",
    "Imputation": "asset_20_imputation",
    "KNNDistance": "asset_21_knn_distance",
    "LogisticCurve": "asset_22_logistic_curve",
}

# -qm is exactly 1280x720 @30fps, which is what the asset spec asks for.
# -qh would be 1080p60: three times the file size, no visible gain on a
# projector, and it blows past the 4 MB per-clip budget.
MANIM_QUALITY = "-qm"


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


# --------------------------------------------------------------------------
# clips
# --------------------------------------------------------------------------
def build_manim(force=False, dry=False, only=None):
    manim = need("manim",
                 "conda install -c conda-forge manim (Linux/macOS) or "
                 "pip install manim (Windows). See docs/INSTALL.md.")
    need("ffmpeg", "conda install -c conda-forge ffmpeg")

    RENDERED.mkdir(parents=True, exist_ok=True)
    built = 0
    for scene, asset in CLIPS.items():
        if only and scene not in only and asset not in only:
            continue
        out = RENDERED / f"{asset}.mp4"
        if not force and not stale(out, MANIM_FILE):
            continue
        print(f"  manim  {scene} -> {asset}.mp4")
        built += 1
        if dry:
            continue
        run([manim, MANIM_QUALITY, "--disable_caching", "--format=mp4",
             "--media_dir", str(MEDIA), "-o", asset, str(MANIM_FILE), scene])
        produced = sorted(MEDIA.rglob(f"{asset}.mp4"),
                          key=lambda p: p.stat().st_mtime)
        if not produced:
            raise RuntimeError(f"manim reported success but {asset}.mp4 "
                               f"was not found under {MEDIA}")
        shutil.copy2(produced[-1], out)
    return built


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tikz", action="store_true", help="diagrams only")
    ap.add_argument("--manim", action="store_true", help="clips only")
    ap.add_argument("--scene", action="append", default=None,
                    help="build one clip by scene or asset name (repeatable)")
    ap.add_argument("--force", action="store_true", help="ignore timestamps")
    ap.add_argument("--list", action="store_true",
                    help="show what is out of date, build nothing")
    ap.add_argument("--clean", action="store_true",
                    help="remove build intermediates (not rendered/)")
    args = ap.parse_args()

    if args.clean:
        shutil.rmtree(MEDIA, ignore_errors=True)
        for ext in ("*.aux", "*.log", "*.pdf", "*.out"):
            for f in TIKZ.glob(ext):
                f.unlink()
        print("cleaned build intermediates")
        return 0

    do_tikz = args.tikz or not (args.tikz or args.manim or args.scene)
    do_manim = args.manim or args.scene or not (args.tikz or args.manim)

    t0 = time.time()
    total = 0
    try:
        if do_tikz:
            print("diagrams:")
            n = build_tikz(args.force, args.list)
            total += n
            print(f"  {n} rebuilt" if not args.list else f"  {n} out of date")
        if do_manim:
            print("clips:")
            n = build_manim(args.force, args.list, args.scene)
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
