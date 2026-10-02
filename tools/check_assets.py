#!/usr/bin/env python3
"""
Check every rendered asset against the spec in docs/WORKSHOP-PLAN.md.

    make -C assets check      (or: python tools/check_assets.py)

Caps enforced: clips <= 30 s and <= 4 MB, 1280x720; the whole rendered/
directory well under the repo budget. Exits non-zero on a violation so it
can gate a release. A deck that stalls mid-session because one clip is 40 MB
is a failure mode worth catching in CI rather than in a lecture hall.
"""

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RENDERED = ROOT / "assets" / "rendered"

MAX_CLIP_MB = 4.0
MAX_CLIP_SEC = 30.0     # self-contained micro-lessons need reading time
EXPECT_SIZE = (1280, 720)
MAX_TOTAL_MB = 60.0

EXPECTED = [
    "asset_01_variable_boxes.svg", "asset_02_list_vs_dict.svg",
    "asset_03_for_loop.mp4", "asset_04_list_vs_array.svg",
    "asset_05_broadcasting.mp4", "asset_06_dataframe_anatomy.svg",
    "asset_07_wrangling_pipeline.svg", "asset_08_split_apply_combine.mp4",
    "asset_09_good_chart.svg", "asset_11_supervised_unsupervised.svg",
    "asset_12_train_test_split.svg", "asset_12b_train_test_split.mp4",
    "asset_13_overfitting.mp4", "asset_14_decision_boundary.mp4",
    "asset_15_confusion_matrix.svg", "asset_16_knn.mp4",
    "asset_17_effect_of_k.mp4", "asset_18_scaling.svg",
    "asset_19_pipeline.svg", "asset_24_rules_vs_learning.svg", "asset_25_confusion_matrix_3x3.svg", "asset_20_imputation.mp4",
    "asset_21_knn_distance.mp4", "asset_22_logistic_curve.mp4",
    "asset_23_confusion_matrix.mp4",
]


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=width,height", "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    stream = d["streams"][0]
    return float(d["format"]["duration"]), stream["width"], stream["height"]


def main():
    if not RENDERED.exists():
        sys.exit("assets/rendered/ does not exist — run `make -C assets` first")

    problems, total = [], 0.0
    print(f"{'asset':<38} {'size':>9}  detail")
    print("-" * 74)

    for name in EXPECTED:
        p = RENDERED / name
        if not p.exists():
            problems.append(f"MISSING  {name}")
            print(f"{name:<38} {'—':>9}  MISSING")
            continue

        mb = p.stat().st_size / 1e6
        total += mb
        detail = ""

        if p.suffix == ".mp4":
            dur, w, h = probe(p)
            detail = f"{dur:5.1f}s  {w}x{h}"
            if mb > MAX_CLIP_MB:
                problems.append(f"{name}: {mb:.1f} MB > {MAX_CLIP_MB} MB")
            if dur > MAX_CLIP_SEC:
                problems.append(f"{name}: {dur:.1f}s > {MAX_CLIP_SEC}s")
            if (w, h) != EXPECT_SIZE:
                problems.append(f"{name}: {w}x{h}, expected 1280x720")

        print(f"{name:<38} {mb:8.2f}M  {detail}")

    print("-" * 74)
    print(f"{'total':<38} {total:8.2f}M")
    if total > MAX_TOTAL_MB:
        problems.append(f"rendered/ total {total:.1f} MB > {MAX_TOTAL_MB} MB")

    extra = sorted(f.name for f in RENDERED.iterdir()
                   if f.is_file() and f.name not in EXPECTED
                   and not f.name.startswith("."))
    n_png = len(list((RENDERED / "png").glob("*.png"))) if (RENDERED / "png").exists() else 0
    print(f"{'png/ (for notebook embedding)':<38} {n_png:>8} files")
    if extra:
        print("\nnot in the spec (harmless, but unreferenced):",
              ", ".join(extra))

    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("\nAll assets within spec.")


if __name__ == "__main__":
    main()
