#!/usr/bin/env python3
"""
Check every rendered asset against the spec in docs/WORKSHOP-PLAN.md.

    make -C assets check      (or: python tools/check_assets.py)

Checks that every diagram the deck references exists, and that rendered/
stays small. Exits non-zero on a violation so it can gate a release: a deck
with a missing figure is worth catching in CI rather than in a lecture hall.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RENDERED = ROOT / "assets" / "rendered"

MAX_TOTAL_MB = 10.0

# Every diagram the deck points at. No clips in the two-hour version.
EXPECTED = [
    "asset_01_variable_boxes.svg", "asset_04_list_vs_array.svg",
    "asset_06_dataframe_anatomy.svg", "asset_09_good_chart.svg",
    "asset_11_supervised_unsupervised.svg", "asset_12_train_test_split.svg",
    "asset_15_confusion_matrix.svg", "asset_18_scaling.svg",
    "asset_19_pipeline.svg",
]


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
