#!/usr/bin/env python3
"""
Execute every notebook and report any cell that raises.

    python tools/check_notebooks.py            # all notebooks
    python tools/check_notebooks.py NB-SOLUTIONS.ipynb

NB1/NB2 contain deliberate `___` blanks that are *supposed* to fail, so only
NB0 and NB-SOLUTIONS are executed by default — those are the two that must be
green. Run this before every workshop: a hosted dataset URL going down is the
single most likely thing to break the session, and this catches it in 30s.
"""

import sys
import pathlib

import nbformat
from nbclient import NotebookClient

ROOT = pathlib.Path(__file__).resolve().parent.parent
RUNNABLE = ["NB0-warmup.ipynb", "NB-SOLUTIONS.ipynb"]

# Cells matching these markers need a runtime we don't have locally
# (Colab-only APIs, or heavyweight optional deps).
SKIP_MARKERS = ("torchvision", "google.colab")


def check(name):
    path = ROOT / "notebooks" / name
    nb = nbformat.read(path, as_version=4)

    skipped = 0
    for cell in nb.cells:
        if cell.cell_type == "code" and any(m in cell.source for m in SKIP_MARKERS):
            cell.source = "# [skipped locally: needs Colab / optional deps]"
            skipped += 1

    NotebookClient(
        nb, timeout=600, kernel_name="python3", allow_errors=True,
        resources={"metadata": {"path": str(ROOT)}},
    ).execute()

    fails = [
        (i, cell.source.strip().splitlines()[0][:70], out["ename"], out["evalue"][:160])
        for i, cell in enumerate(nb.cells)
        for out in cell.get("outputs", [])
        if out.get("output_type") == "error"
    ]

    total = sum(1 for c in nb.cells if c.cell_type == "code")
    mark = "PASS" if not fails else "FAIL"
    print(f"[{mark}] {name}: {total - len(fails)}/{total} cells ran "
          f"({skipped} skipped)")
    for i, src, en, ev in fails:
        print(f"       cell {i}: {en}: {ev}\n         {src}")
    return not fails


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")           # never open a window from a check script
    names = sys.argv[1:] or RUNNABLE
    ok = all([check(n) for n in names])
    sys.exit(0 if ok else 1)
