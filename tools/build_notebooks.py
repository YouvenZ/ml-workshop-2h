#!/usr/bin/env python3
"""
Generate the four workshop notebooks from a single source of truth.

    python tools/build_notebooks.py

Rebuilds notebooks/NB0, NB1, NB2 and NB-SOLUTIONS. Edit this file, never the
.ipynb files — they are build output. Keeping the content here means the
solutions notebook can never drift out of sync with the exercises, because
both are generated from the same EXERCISES table below.
"""

import json
import pathlib

# --- Edit these two lines after you create the GitHub repo -----------------
GH_USER = "YouvenZ"
GH_REPO = "ml-workshop-2h"
# ---------------------------------------------------------------------------

PENGUINS_URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
TITANIC_URL = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
COMP_URL = f"https://raw.githubusercontent.com/{GH_USER}/{GH_REPO}/main/codabench/bundle/input_data"

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "notebooks"


# --------------------------------------------------------------------------
# Visuals
# --------------------------------------------------------------------------
# Diagrams are embedded as base64 data URIs rather than linked.
#
# A linked image needs the repo to be public and the URL to be right, and it
# silently 404s in a student's Colab a year later. Embedding makes each
# notebook self-contained: it renders offline, in any Colab, from any copy,
# forever. The cost is ~60 KB per diagram, which is nothing.
#
# PNG, not SVG: Colab will not render an SVG from a data URI.
PNG_DIR = ROOT / "assets" / "rendered" / "png"

_MISSING_IMG = []


def img(name, width=760, alt=""):
    """Embed assets/rendered/png/<name>.png as a centred data-URI image."""
    import base64

    path = PNG_DIR / f"{name}.png"
    if not path.exists():
        # Don't fail the build — a missing diagram should degrade to a note,
        # so `make -C assets` can be run after the notebooks if need be.
        _MISSING_IMG.append(name)
        return f"<p align=\"center\"><i>[diagram {name} not built yet]</i></p>"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return (f'<p align="center">\n'
            f'<img src="data:image/png;base64,{b64}" '
            f'width="{width}" alt="{alt or name}">\n'
            f'</p>')


_CALLOUT = {
    # kind: (accent, background, label)
    "key":  ("#2A9D8F", "#ECF7F5", "THE POINT"),
    "warn": ("#E07A2C", "#FDF2E9", "WATCH OUT"),
    "info": ("#2E5CA8", "#EDF2FA", "WHY"),
    "try":  ("#1B2A4A", "#F1F2F5", "TRY IT"),
}


def callout(kind, body, label=None):
    """A coloured HTML box. Colab renders inline-styled HTML in markdown
    cells; a <style> block would be stripped, so every rule is inline."""
    accent, bg, default_label = _CALLOUT[kind]
    return (
        f'<div style="border-left:5px solid {accent};background:{bg};'
        f'padding:10px 16px;margin:14px 0;border-radius:4px;">\n'
        f'<div style="color:{accent};font-weight:700;font-size:12px;'
        f'letter-spacing:.09em;margin-bottom:4px;">'
        f'{label or default_label}</div>\n'
        f'{body}\n</div>'
    )


def libwhy(lib, name, bullets):
    """A library's logo and why it matters, shown where the library first appears.

    The logo is linked from the repo (Colab will not render an SVG data URI);
    if it ever 404s the box still reads fine without it.
    """
    logo = (f"https://raw.githubusercontent.com/{GH_USER}/{GH_REPO}/main/"
            f"assets/logos/{lib}.svg")
    items = "".join(f"<li>{b}</li>" for b in bullets)
    return (
        '<div style="display:flex;gap:18px;align-items:center;border:1px solid #D9DCE1;'
        'border-radius:10px;padding:12px 16px;margin:12px 0;">\n'
        f'<img src="{logo}" alt="{name} logo" style="height:64px;max-width:190px;object-fit:contain;">\n'
        '<div><div style="color:#E07A2C;font-weight:700;font-size:12px;letter-spacing:.09em;">'
        f'WHY {name.upper()} MATTERS HERE</div>\n'
        f'<ul style="margin:6px 0 0 0;padding-left:18px;">{items}</ul></div>\n</div>'
    )


# --------------------------------------------------------------------------
# notebook primitives
# --------------------------------------------------------------------------
def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": _lines(text)}


def code(text, collapsed=False):
    cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": _lines(text),
    }
    if collapsed:
        # Colab renders this as a click-to-expand cell — our cheapest
        # differentiation lever: students who need the hint open it,
        # students who don't never see it.
        cell["metadata"]["cellView"] = "form"
    return cell


def _lines(text):
    text = text.strip("\n")
    out = text.splitlines(keepends=True)
    return out


def live(topic, hints=""):
    """An empty cell the instructor fills on screen.

    Not truly empty: a one-line landmark so a student who looks up from
    their keyboard can still tell which cell we are in.
    """
    body = f"# --- live-code: {topic} ---\n"
    if hints:
        body += f"# {hints}\n"
    return code(body + "\n")


def badge(nb):
    url = f"https://colab.research.google.com/github/{GH_USER}/{GH_REPO}/blob/main/notebooks/{nb}"
    return f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]({url})"


def write(name, cells):
    nb = {
        "cells": cells,
        "metadata": {
            "colab": {"provenance": [], "toc_visible": True},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 0,
    }
    path = OUT / name
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
    n_code = sum(1 for c in cells if c["cell_type"] == "code")
    print(f"  {name:<28} {len(cells):>3} cells ({n_code} code)")


# ==========================================================================
# NB0 — Warm-up. Optional, sent before the workshop.
# Read-and-run only. No blanks, no exercises, nothing that can fail.
# ==========================================================================
def build_nb0():
    c = []
    c.append(md(f"""
# Warm-up — before the workshop

{badge('NB0-warmup.ipynb')}

**Optional, but it makes Part 1 much easier: everything you do here is
time saved on the day.**

You do not need to install anything. You do not need to understand everything
here. You need to arrive on the day having *run a cell* at least once.

Three things to do:

1. Click **Copy to Drive** at the top of this page. (Without it your changes
   are not saved — you are looking at a read-only copy.)
2. Run every cell, top to bottom.
3. Answer the one question at the bottom.
"""))

    c.append(md("""
## 1. Running a cell

A notebook is a stack of cells. Grey cells are **code**, white cells are
**text**. You run a code cell by clicking it and pressing **Shift + Enter**.

Try it on the cell below. It should print a line underneath itself.
"""))
    c.append(code("""
print("If you can see this, you are ready for the workshop.")
"""))

    c.append(md("""
Notice the `[ ]` to the left of the cell turned into a number, like `[1]`.
That number is the order cells were run in — it will matter later.

> **The one thing to remember:** if a notebook starts behaving strangely,
> use the menu **Runtime → Restart and run all**. That fixes most problems
> and you will not break anything by doing it.
"""))

    c.append(md("""
## 2. Variables

A variable is a **name attached to a value**. The `=` sign does not mean
"equals" the way it does in maths — it means *"put this value in this box"*.
"""))
    c.append(code("""
species = "Adelie"
body_mass_g = 3750

print(species)
print(body_mass_g)
"""))
    c.append(md(img("asset_01_variable_boxes", 680,
                    "assignment as labelled boxes holding values")))

    c.append(md("""
You can put the name in a sentence with an **f-string** — a piece of text with
an `f` in front, where anything in `{curly braces}` gets replaced by its value.
"""))
    c.append(code("""
print(f"This penguin is an {species} and weighs {body_mass_g} grams.")
"""))

    c.append(md("""
## 3. A list of values

Most real data is many values, not one. A **list** holds them in order,
inside square brackets.
"""))
    c.append(code("""
masses = [3750, 3800, 3250, 3450]

print(masses)
print("how many:", len(masses))
print("the first one:", masses[0])
"""))

    c.append(md("""
> Python counts from **0**, not 1. `masses[0]` is the first value.
> This trips up everybody once, and then never again.
"""))

    c.append(md("""
## 4. Self-check

Run the cell below. **Before you look at the answer**, decide what you think
it will print.
"""))
    c.append(code("""
flippers = [181, 186, 195, 193]

print(flippers[1])
"""))

    c.append(md("""
<details>
<summary><b>Click here for the answer</b></summary>

It prints `186`.

`flippers[0]` is 181, so `flippers[1]` is the **second** value, 186.

If you guessed 181, you were counting from 1 — that is the single most common
first mistake in Python, and you have now made it before the workshop instead
of during it. That is exactly what this notebook was for.
</details>

---

## That's it

You are done. See you at the workshop.

If a cell threw a red error you could not get past, that is useful information —
tell us at the start of the session rather than fighting it alone.
"""))
    return c


# ==========================================================================
# Shared helpers so NB1/NB2 and NB-SOLUTIONS are generated from ONE source.
# `sol=True` fills in every live-code cell and every ___ blank.
# ==========================================================================
def L(sol, topic, hints, answer):
    """A live-code cell: empty for students, filled in the solutions."""
    if sol:
        return code(f"# {topic}\n{answer.strip()}\n")
    return live(topic, hints)


def EX(sol, blanked, answer):
    """An exercise cell: blanks for students, filled in the solutions."""
    return code(answer if sol else blanked)


# ==========================================================================
# NB1 — Python & Data.  Parts 1-2.
# ==========================================================================
def build_nb1(sol=False):
    c = []
    name = "NB-SOLUTIONS" if sol else "NB1"
    c.append(md(f"""
# {name} — Python for Data Work
## Parts 1 and 2

{badge('NB1-python-data.ipynb')}

**Click *Copy to Drive* before you start**, or nothing you type will be saved.

| | |
|---|---|
| **Grey cells** | code — run with `Shift + Enter` |
| **`___`** | a blank for you to fill in |
| **Stuck?** | flat hand. **Done?** thumbs up. |
| **Broken?** | Runtime → Restart and run all |
"""))

    # --- the first win, inside 90 seconds ---------------------------------
    c.append(md("""
---
## Cell 1 — run this now

Do not read it yet. Click it, press **Shift + Enter**, and check you get a
table of penguins. We will explain every piece of this line in the next half hour.
"""))
    c.append(code(f"""
import pandas as pd

URL = "{PENGUINS_URL}"
df = pd.read_csv(URL)

print(f"Loaded {{len(df)}} penguins.")
df.head()
"""))
    c.append(md("""
If you see a table: you are set up. That is the whole setup.

If you see a red error: raise a hand. Do not debug it alone — it is almost
certainly the network, not you.
"""))

    # ================== PART 1 ============================================
    c.append(md("""
---
---
# Part 1 — Python for data work

Everything below is typed live on screen. Type along in the empty cells —
you will remember far more than by reading finished code.
"""))

    c.append(md("""
## Variables and types

A variable is a **labelled box holding a value**. `=` means *"put this in
that box"*, not "is equal to".
"""))
    c.append(L(sol, "variables and types", "species, body_mass_g, is_adult", """
species     = 'Adelie'      # str  — text
body_mass_g = 3750          # int  — whole number
bill_mm     = 39.1          # float — decimal
is_adult    = True          # bool — True / False

print(type(species), type(body_mass_g), type(bill_mm), type(is_adult))
print(f"A {species} weighing {body_mass_g} g")
"""))
    c.append(md(img("asset_01_variable_boxes", 700,
                    "assignment as labelled boxes") + "\n\n" +
                callout("warn",
                        "<code>=</code> puts a value in a box. "
                        "<code>==</code> asks whether two things are equal. "
                        "Mixing them up is the single most common first error "
                        "in Python.")))

    c.append(md("""
## Lists — ordered, indexed, sliceable

One value is rarely enough. A list holds many, **in order**, and remembers
that order.
"""))
    c.append(L(sol, "lists", "masses = [...]  then index, slice, len, append", """
masses = [3750, 3800, 3250, 3450]

masses[0]      # first  — Python counts from 0
masses[-1]     # last
masses[:2]     # first two — a slice
len(masses)    # how many

masses.append(4100)
print(masses)
"""))

    c.append(md("""
## Dicts — lookup by name, not by position

A list answers *"what is at position 2?"*. A dict answers *"what is the
mass?"*. One row of a table is naturally a dict.
"""))
    c.append(L(sol, "dicts", "penguin = {'species': ..., 'mass': ..., 'island': ...}", """
penguin = {'species': 'Adelie', 'mass': 3750, 'island': 'Torgersen'}

penguin['mass']
penguin.keys()
penguin['mass'] = 3800      # values can be changed
print(penguin)
"""))
    c.append(md(img("asset_02_list_vs_dict", 820,
                    "list found by position, dict found by name") + "\n\n" +
                callout("key",
                        "A list answers <i>“what is at position 2?”</i>. "
                        "A dict answers <i>“what is the mass?”</i>. "
                        "One row of the table you loaded is naturally a dict.")))

    c.append(md("""
## Loops and conditionals

A **loop** does the same thing to every item. A **conditional** chooses
between two paths.

> The indentation is not decoration — it is what tells Python which lines are
> *inside* the loop. And `==` asks a question; `=` gives an answer.
"""))
    c.append(L(sol, "loops and conditionals", "for m in masses: if m > 3700 ... else ...", """
for m in masses:
    if m > 3700:
        print(m, 'heavy')
    else:
        print(m, 'light')
"""))

    c.append(md("""
## Functions — name a piece of work so you can reuse it
"""))
    c.append(L(sol, "functions", "def size_label(mass_g): return ...", """
def size_label(mass_g):
    return 'large' if mass_g > 3700 else 'small'

print(size_label(3750))
print(size_label(3250))

# a function is most useful applied to many values at once:
for m in masses:
    print(m, size_label(m))
"""))

    # --- NumPy ------------------------------------------------------------
    c.append(md("""
---
## NumPy — the same operations, on the whole column at once

A Python list of numbers is a list of *objects scattered in memory*. A NumPy
array is **one contiguous block of numbers**. That difference is why it is
fast, and why every data library in Python is built on it.
"""))
    c.append(md(libwhy("numpy", "NumPy", [
        "Looping over a million list items in Python is slow; one NumPy operation hits every element at once, in compiled code.",
        "Every number in machine learning (features, weights, predictions) is stored in a NumPy array.",
        "pandas, Matplotlib and scikit-learn are all built on top of it.",
    ])))
    c.append(L(sol, "numpy arrays", "np.array, .shape, .dtype", """
import numpy as np

a = np.array([3750, 3800, 3250, 3450])
print(a)
print(a.shape, a.dtype)
"""))
    c.append(md(img("asset_04_list_vs_array", 840,
                    "a list of pointers vs one contiguous block")))

    c.append(md("""
### Vectorised: no loop needed

This is the idea that makes the rest of the workshop possible. One operation
applies to **every element**, with no `for` in sight.
"""))
    c.append(L(sol, "vectorised operations", "a * 2, a.mean(), a.std(), a.max()", """
a * 2            # every element doubled — no loop
a + 100

a.mean(), a.std(), a.max(), a.min()
"""))

    c.append(md("""
### Boolean masking — the bridge to Pandas

`a > 3700` does not give you `True` or `False`. It gives you **one answer per
element**. Feed that back in as an index and you keep only the `True` ones.

Remember this — Pandas filtering is exactly the same idea on a whole table.
"""))
    c.append(L(sol, "boolean masking", "a > 3700 is a mask; a[mask] filters", """
mask = a > 3700
print(mask)          # one True/False per element

print(a[mask])       # keep only where True
print(a[a > 3700])   # normally written in one line
print((a > 3700).sum())   # True counts as 1 — so this counts them
"""))

    c.append(md("""
### The speed demo

One million numbers. Same sum, two ways. Watch the units — one says
milliseconds, the other says microseconds.
"""))
    c.append(code("""
big = np.random.rand(1_000_000)
"""))
    c.append(code("""
%timeit sum(big)          # Python loop
"""))
    c.append(code("""
%timeit big.sum()         # NumPy
"""))
    c.append(md("""
> That gap is typically **50–250×** depending on the machine. It is the
> entire answer to
> *"why not just use a list?"*.
"""))

    # --- Pandas -----------------------------------------------------------
    c.append(md("""
---
## Pandas — NumPy with names on the rows and columns

A **DataFrame** is a table. Each column is a **Series** — a NumPy array that
knows its own name and dtype.
"""))
    c.append(md(libwhy("pandas", "pandas", [
        "Real data is a table with named columns, mixed types and missing cells; a bare array cannot hold that.",
        "It reads a CSV or Excel file in one line, and filters, groups, counts and fills gaps in one line each.",
        "Under every column is a NumPy array, so the speed and the boolean masks come with it.",
    ])))
    c.append(L(sol, "first look at a dataframe", "head, shape, columns, info", """
df.head()          # first five rows
df.shape           # (rows, columns)
df.columns         # column names
df.info()          # dtypes AND missing values, in one view
"""))
    c.append(md(img("asset_06_dataframe_anatomy", 860,
                    "index, columns, one row, one cell") + "\n\n" +
                callout("info",
                        "Every question you ask of this table is some "
                        "combination of picking <b>columns</b> and filtering "
                        "<b>rows</b>. That is most of pandas.")))

    c.append(md("""
### Selecting columns

**One bracket gives a Series. Two brackets give a DataFrame.** That
distinction will cause you an error in Part 3, so meet it now.
"""))
    c.append(L(sol, "selecting columns", "df['col'] vs df[['col1','col2']]", """
df['body_mass_g']                  # one column  -> Series
df[['species', 'body_mass_g']]     # a list of columns -> DataFrame

type(df['body_mass_g']), type(df[['body_mass_g']])
"""))

    c.append(md("""
### Filtering rows

Exactly the boolean mask you just met, applied to a table.

> With more than one condition, wrap **each** in parentheses and join with
> `&` (and) or `|` (or). Not `and` / `or` — those fail on whole columns.
"""))
    c.append(L(sol, "filtering rows", "df[df[...] > ...], then two conditions with &", """
df[df['body_mass_g'] > 4500]

df[(df['species'] == 'Gentoo') & (df['body_mass_g'] > 5000)]

# how many rows came back?
df[df['body_mass_g'] > 4500].shape[0]
"""))

    # --- Exercise 1 -------------------------------------------------------
    c.append(md("""
---
# Exercise 1

Three short tasks. Fill in every `___`. Work with the person next to you.

Thumbs up when you are done, flat hand if you are stuck.
"""))

    c.append(md("**Task 1.** Write a function that labels a flipper `'long'` above 210 mm, else `'short'`."))
    c.append(EX(sol, """
def flipper_label(mm):
    if mm > ___:
        return ___
    else:
        return ___


# check yourself — this should print:  long   short
print(flipper_label(215))
print(flipper_label(190))
""", """
def flipper_label(mm):
    if mm > 210:
        return 'long'
    else:
        return 'short'


# check yourself — this should print:  long   short
print(flipper_label(215))
print(flipper_label(190))

# the same thing written the short way:
def flipper_label_short(mm):
    return 'long' if mm > 210 else 'short'
"""))

    c.append(md("**Task 2.** How many penguins are heavier than the average penguin?"))
    c.append(EX(sol, """
masses = df['body_mass_g'].dropna().to_numpy()

average = masses.___()            # the mean of the array
above   = masses[masses > ___]    # keep only those above it

print(f"{len(above)} of {len(masses)} penguins are above the mean mass")
""", """
masses = df['body_mass_g'].dropna().to_numpy()

average = masses.mean()               # the mean of the array
above   = masses[masses > average]    # keep only those above it

print(f"{len(above)} of {len(masses)} penguins are above the mean mass")

# note it is NOT half — the distribution is not symmetric, because
# Gentoos are much heavier than the other two species.
"""))

    c.append(md("**Task 3.** How many Chinstrap penguins are in the dataset?"))
    c.append(EX(sol, """
chinstraps = df[df['___'] == 'Chinstrap']

print(chinstraps.shape[0], "Chinstrap penguins")
""", """
chinstraps = df[df['species'] == 'Chinstrap']

print(chinstraps.shape[0], "Chinstrap penguins")   # 68

# value_counts() answers this for every species at once — Part 2:
df['species'].value_counts()
"""))

    c.append(md("""
### Checkpoint

> Given `df`, what does this return — a penguin, a number, or a table?
>
> ```python
> df[df['body_mass_g'] > 4000].shape[0]
> ```

Decide before you run it. Then run it.
"""))
    c.append(code("""
df[df['body_mass_g'] > 4000].shape[0]
"""))

    # ================== PART 2 ============================================
    c.append(md("""
---
---
# Part 2 — Wrangling and visualisation

Same data, harder questions. By the end of this part you will have made the
one chart that the whole second hour depends on.
"""))
    c.append(md(img("asset_07_wrangling_pipeline", 900,
                    "raw, clean, explore, visualise")))

    c.append(md("""
## Summarising

Three methods answer most first questions about a dataset.
"""))
    c.append(L(sol, "summarising", "describe, value_counts, isna().sum()", """
df.describe()                  # count/mean/std/min/quartiles/max, numeric only
df['species'].value_counts()   # how many of each category
df['island'].value_counts()
"""))

    c.append(md("""
## Missing values — a decision, not a command

`df.isna().sum()` counts the gaps in each column.

> **Before you run the next cell, answer out loud:** if we delete every row
> with any missing value, what have we lost? Is that acceptable here?
"""))
    c.append(L(sol, "finding missing values", "df.isna().sum()", """
df.isna().sum()
"""))
    c.append(L(sol, "dropping missing values — after discussing it", "df = df.dropna()", """
print("before:", df.shape)
df = df.dropna()
print("after: ", df.shape)

# 11 rows gone out of 344. Cheap here. On a medical dataset, the rows with
# missing values are often the *interesting* ones, and dropping them silently
# would be the whole error.
"""))

    c.append(md("""
## Split, apply, combine — `groupby`

*"Split the rows into groups, compute something per group, put the answers
back together."* It is the single most used operation in data work.
"""))
    c.append(L(sol, "groupby", "groupby('species')['body_mass_g'].mean()", """
df.groupby('species')['body_mass_g'].mean()

df.groupby(['species', 'sex'])['flipper_length_mm'].agg(['mean', 'count'])

df.sort_values('body_mass_g', ascending=False).head()
"""))

    c.append(md("""
---
## Visualisation

Three charts, in order of how much they tell you.
"""))
    c.append(md(libwhy("matplotlib", "Matplotlib", [
        "A table of 344 rows hides its patterns; a chart shows groups, trends, outliers and data errors in a second.",
        "Matplotlib is Python's base plotting library. <b>seaborn</b> (<code>sns</code>) sits on top of it for statistical charts, like colouring by species in one argument.",
        "Before you train a model, you look: the chart tells you whether a model even has a chance.",
    ])))
    c.append(md(img("asset_09_good_chart", 860,
                    "title, axis labels with units, legend, readable ticks") +
                "\n\n" +
                callout("key",
                        "Every chart you produce today gets a title, both axes "
                        "labelled <b>with units</b>, and a legend if colour "
                        "means anything. This is the standard, not a nag.")))
    c.append(L(sol, "a histogram — the shape of one variable", "df['body_mass_g'].hist(bins=30) + labels", """
import matplotlib.pyplot as plt
import seaborn as sns

df['body_mass_g'].hist(bins=30)
plt.xlabel('body mass (g)')
plt.ylabel('count')
plt.title('Mass distribution')
plt.show()

# Two humps. That is not noise — it is Gentoos versus everyone else.
"""))

    c.append(L(sol, "a scatter — two variables together", "sns.scatterplot(data=df, x=..., y=...)", """
sns.scatterplot(data=df, x='flipper_length_mm', y='body_mass_g')
plt.title('A cloud')
plt.show()
"""))

    c.append(md("""
### The one line that the whole workshop turns on

Add **one argument** to the chart you just made.
"""))
    c.append(L(sol, "the same scatter, coloured by species", "add hue='species'", """
sns.scatterplot(data=df, x='flipper_length_mm', y='body_mass_g', hue='species')
plt.title('Three groups')
plt.show()
"""))
    c.append(md("""
> The cloud was never a cloud. It was **three groups** all along.
>
> Those groups are what a classifier learns to draw a line between. That is
> the whole of Part 3, and you have just seen it with your own eyes.
"""))

    # --- Practice ---------------------------------------------------------
    c.append(md("""
---
# Independent practice

Three questions. Answer each with code **and one chart where it helps**.
Work in pairs. Question 4 is a stretch for fast finishers — or homework.
"""))
    c.append(md("**1.** Which species is heaviest on average?"))
    c.append(EX(sol, """
# hint: groupby, then mean

""", """
df.groupby('species')['body_mass_g'].mean().sort_values(ascending=False)
# Gentoo, ~5092 g — roughly 1.4 kg heavier than the other two
# (Adelie 3706, Chinstrap 3733).
"""))

    c.append(md("**2.** How many penguins are on each island?"))
    c.append(EX(sol, """
# hint: value_counts

""", """
df['island'].value_counts()
# Biscoe 163, Dream 123, Torgersen 47 (after dropna).
"""))

    c.append(md("**3.** Do flipper length and body mass move together? Show it."))
    c.append(EX(sol, """
# hint: a scatter plot

""", """
sns.scatterplot(data=df, x='flipper_length_mm', y='body_mass_g', hue='species')
plt.xlabel('flipper length (mm)')
plt.ylabel('body mass (g)')
plt.title('Flipper length vs body mass')
plt.show()
# Yes: longer flippers go with heavier penguins. But see the checkpoint
# below before you call it a law.
"""))

    c.append(md("""
**4.** *Stretch — only if you finish early.* Pick any two variables and produce **one labelled chart
that tells a story**. Title, both axes labelled, legend if you used colour.
"""))
    c.append(EX(sol, """
# your chart here — there is no single right answer

""", """
# One of many good answers: bill shape separates the species even better
# than size does, which is a nice preview of 'feature choice matters'.
sns.scatterplot(data=df, x='bill_length_mm', y='bill_depth_mm', hue='species')
plt.xlabel('bill length (mm)')
plt.ylabel('bill depth (mm)')
plt.title('Bill shape separates the species almost perfectly')
plt.show()
"""))

    c.append(md("""
### Checkpoint

> Penguins with longer flippers are heavier.
> Does having longer flippers **cause** a penguin to weigh more?

---

## End of NB1

Next: **NB2 — Machine Learning**. It loads its own data in cell 1, so it does
not matter if anything in this notebook is broken.
"""))
    return c


# ==========================================================================
# NB2 — Machine Learning.  Parts 3-4.
#
# THE critical design rule: cell 1 loads and cleans its own data. A student
# whose NB1 is broken still starts the ML block on time.
# ==========================================================================
def build_nb2(sol=False):
    c = []
    name = "NB-SOLUTIONS" if sol else "NB2"
    c.append(md(f"""
# {name} — Machine Learning
## Parts 3 and 4

{badge('NB2-machine-learning.ipynb')}

**Click *Copy to Drive* before you start.**

This notebook is **independent of NB1**. It loads and cleans its own data
below. If anything in NB1 went wrong, it does not matter now — run cell 1
and you are caught up with everyone else.
"""))

    c.append(md("""
---
## Cell 1 — run this first, whatever happened in NB1
"""))
    c.append(code(f"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

URL = "{PENGUINS_URL}"
df = pd.read_csv(URL).dropna().reset_index(drop=True)

print(f"{{len(df)}} penguins, no missing values.")
df.head()
"""))
    c.append(md("""
One line did the whole of Part 2's cleaning: `.dropna()`. You now know what
it cost us (11 rows) and why we accepted that.
"""))

    # ================== PART 3 ============================================
    c.append(md("""
---
---
# Part 3 — Concepts, then your first models

## The four ideas

**1. Supervised vs unsupervised.** Supervised learning has an *answer key* —
we know each penguin's species and the model learns to reproduce it.
Unsupervised has no answer key; the model finds groupings on its own.
Today is entirely supervised.

**2. Features and labels.** In the table you already know:

- the columns we learn **from** are the **features**, called `X`
- the column we learn **to predict** is the **label**, called `y`

**3. Train / test split.** We hide some rows from the model, then test it on
those. *You do not grade a student on the exact questions they studied.*

**4. Overfitting.** A model can memorise the training rows instead of
learning the pattern. It then scores brilliantly on what it has seen and
badly on anything new. The gap between those two scores is the warning sign.

> Write each of those four in **your own words** in the cell below. Not for
> marks — putting it in your own words is how you find out whether you have it.
"""))
    c.append(md("""
*Your definitions (double-click to edit this cell):*

1. Supervised vs unsupervised —
2. Features and labels —
3. Train / test split —
4. Overfitting —
"""))
    c.append(md(img("asset_11_supervised_unsupervised", 760,
                    "labelled data predicts a label; unlabelled data finds groups")))
    c.append(md(img("asset_12_train_test_split", 820,
                    "one bar of data splitting 80/20")))

    c.append(md(libwhy("scikit-learn", "scikit-learn", [
        "Dozens of algorithms (linear regression, logistic regression, KNN, trees...) all used with the same verbs: <code>fit</code>, <code>predict</code>, <code>score</code>.",
        "Learn the pattern once and swap the algorithm in one line.",
        "The tools around the model come with it: <code>train_test_split</code>, scalers, metrics, the confusion matrix.",
    ])))

    c.append(md("""
---
## Classification or regression?

Supervised learning asks one of two kinds of question:

| | **classification** | **regression** |
|---|---|---|
| the answer is | a **category** from a fixed list | a **number** on a scale |
| on our penguins | *which species?* | *how heavy, in grams?* |
| scored by | accuracy, the confusion matrix | average error (MAE), R² |
| today's algorithms | logistic regression, KNN | linear regression |

Same table, two questions: predict `species` and it is classification;
predict `body_mass_g` and it is regression. The **split → fit → predict →
score** pattern is identical for both; only the model and the score change.
"""))
    c.append(md("""
*Classify each task: classification (C) or regression (R)? Double-click to edit.*

1. Is this email spam? —
2. The price of an apartment —
3. Which digit (0–9) is in this image? —
4. Minutes until the next bus —
"""))

    # --- Algorithm 1: linear regression -------------------------------------
    c.append(md("""
---
## Algorithm 1 — Linear regression (predicting a number)

**Question:** can we predict a penguin's **body mass** from its **flipper length**?

In the scatter plot from NB1 the cloud rises: longer flippers, heavier
penguins. Linear regression draws the **best** straight line through it:

$$\\hat{y} = w\\,x + b$$

- `w`, the **slope**: grams gained per extra millimetre of flipper
- `b`, the **intercept**: where the line starts
- the **residual** `y − ŷ` is how far each penguin is from the line

`.fit()` picks the `w` and `b` that make the **mean squared error**
(the average of the squared residuals) as small as possible. That is
called *least squares*.
"""))
    c.append(L(sol, "split, fit a linear regression", "LinearRegression().fit(Xr_train, yr_train); print reg.coef_ and reg.intercept_", """
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

Xr = df[['flipper_length_mm']]     # one feature (double brackets)
yr = df['body_mass_g']             # the number to predict

Xr_train, Xr_test, yr_train, yr_test = train_test_split(
    Xr, yr, test_size=0.2, random_state=42)

reg = LinearRegression()
reg.fit(Xr_train, yr_train)
print("w (slope)     =", round(reg.coef_[0], 1), "g per mm")
print("b (intercept) =", round(reg.intercept_))
"""))
    c.append(md(callout("info",
                        "Read <code>w</code> as a sentence: <i>each extra "
                        "millimetre of flipper adds about 50 g</i>. Being "
                        "this easy to explain is linear regression's "
                        "superpower.")))
    c.append(L(sol, "predict and score a regression", "reg.predict(Xr_test); mean_absolute_error and r2_score", """
from sklearn.metrics import mean_absolute_error, r2_score

pred_mass = reg.predict(Xr_test)
print("MAE:", round(mean_absolute_error(yr_test, pred_mass)), "g off on average")
print("R² :", round(r2_score(yr_test, pred_mass), 3))

# The baseline to beat: always predict the average training mass.
baseline = [yr_train.mean()] * len(yr_test)
print("baseline MAE:", round(mean_absolute_error(yr_test, baseline)), "g")
"""))
    c.append(md("""
> There is no "accuracy" for a number: a prediction of 4 100 g for a 4 150 g
> penguin is nearly right, not wrong. Regression is scored by **how far off**
> it is: **MAE** (mean absolute error, in grams) and **R²** (the share of the
> variation explained: 1 is perfect, 0 is no better than the average).
"""))
    c.append(L(sol, "plot the fitted line", "scatter the test penguins, then plt.plot the predictions", """
plt.scatter(Xr_test['flipper_length_mm'], yr_test, alpha=0.6, label='real penguins (test)')
order = Xr_test['flipper_length_mm'].argsort()
plt.plot(Xr_test['flipper_length_mm'].iloc[order], pred_mass[order],
         color='#E07A2C', linewidth=3, label='the fitted line')
plt.xlabel('flipper length (mm)')
plt.ylabel('body mass (g)')
plt.title('Linear regression: one feature, one line')
plt.legend()
plt.show()
"""))
    c.append(md("""
### More features, one weight each

$$\\hat{y} = w_1x_1 + w_2x_2 + w_3x_3 + b$$

Add the penguin's sex and whether it is a Gentoo. Does the error go down?
"""))
    c.append(EX(sol, """
df['is_male']   = (df['sex'].str.upper() == 'MALE').astype(int)
df['is_gentoo'] = (df['species'] == 'Gentoo').astype(int)

Xm = df[['flipper_length_mm', ___, ___]]
Xm_train, Xm_test, ym_train, ym_test = train_test_split(
    Xm, yr, test_size=0.2, random_state=42)

reg2 = LinearRegression().fit(Xm_train, ym_train)
print("weights:", reg2.coef_.round(1))
print("MAE:", round(mean_absolute_error(ym_test, reg2.predict(Xm_test))), "g")
""", """
df['is_male']   = (df['sex'].str.upper() == 'MALE').astype(int)
df['is_gentoo'] = (df['species'] == 'Gentoo').astype(int)

Xm = df[['flipper_length_mm', 'is_male', 'is_gentoo']]
Xm_train, Xm_test, ym_train, ym_test = train_test_split(
    Xm, yr, test_size=0.2, random_state=42)

reg2 = LinearRegression().fit(Xm_train, ym_train)
print("weights:", reg2.coef_.round(1))
print("MAE:", round(mean_absolute_error(ym_test, reg2.predict(Xm_test))), "g")

# about 290 g -> about 209 g: sex and species carry information that
# flipper length alone does not.
"""))

    c.append(md("""
---
## Algorithm 2 — Logistic regression (predicting a category)

Back to the species question. Logistic regression computes the same
weighted sum as linear regression, then squashes it into a probability
between 0 and 1 with the sigmoid, `p = 1 / (1 + e^(−z))`.
"""))

    c.append(md("""
---
## Features and labels, on our data
"""))
    c.append(L(sol, "define X and y", "X = three numeric columns (double brackets), y = species", """
X = df[['flipper_length_mm', 'body_mass_g', 'bill_length_mm']]   # features
y = df['species']                                                # label

print(X.shape, y.shape)
X.head()
"""))
    c.append(md("""
> `X` uses **double** brackets (a DataFrame, many columns), `y` uses **single**
> (a Series, one column). Get this backwards and `.fit()` fails — which is the
> single most common error in this notebook.
"""))

    c.append(md("""
## Split, fit, predict, score

These four lines are the pattern. If you remember nothing else from today,
remember this shape.
"""))
    c.append(L(sol, "the split", "train_test_split(X, y, test_size=0.2, random_state=42)", """
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

print("train:", X_train.shape[0], " test:", X_test.shape[0])

# random_state=42 makes the split reproducible. Without it you get a
# different split every run and cannot compare two models honestly.
"""))

    c.append(L(sol, "fit the model", "LogisticRegression(max_iter=1000).fit(X_train, y_train)", """
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)
"""))
    c.append(md("""
> **That was it.** `.fit()` is the line the entire workshop was building
> toward. Everything before it was getting the data into a shape this line
> accepts; everything after it is checking whether to believe it.
"""))

    c.append(L(sol, "predict and score", "model.predict(X_test), accuracy_score(y_test, preds)", """
from sklearn.metrics import accuracy_score

preds = model.predict(X_test)
accuracy_score(y_test, preds)
"""))

    c.append(md("""
---
## Evaluate honestly

Accuracy is one number and it hides things. A confusion matrix shows you
*which* classes it confuses.
"""))
    c.append(L(sol, "confusion matrix", "ConfusionMatrixDisplay.from_estimator(model, X_test, y_test)", """
from sklearn.metrics import ConfusionMatrixDisplay

ConfusionMatrixDisplay.from_estimator(model, X_test, y_test)
plt.show()

# Rows are the truth, columns are the prediction. Everything off the
# diagonal is a mistake — and it tells you which pair it mixes up.
"""))
    c.append(md(img("asset_25_confusion_matrix_3x3", 820,
                    "the real 3x3 confusion matrix of the 67 test penguins, "
                    "with recall per row and precision per column") +
                "\n\n" +
                callout("key",
                        "The diagonal is where it was right. Everything off "
                        "the diagonal is a mistake — and the matrix tells you "
                        "<i>which</i> pair the model confuses, which a single "
                        "accuracy number never can.")))

    c.append(md("""
### Now look at a penguin it got wrong

Accuracy is a number. A misclassified row is a story.
"""))
    c.append(L(sol, "inspect the mistakes", "wrong = X_test[preds != y_test]", """
wrong = X_test[preds != y_test].copy()
wrong['actual']    = y_test[preds != y_test]
wrong['predicted'] = preds[preds != y_test]
wrong

# Pick one and ask the room: why would the model confuse this penguin?
# Usually it sits right on the boundary between two species — small Gentoo,
# large Chinstrap. The model is not stupid; the data genuinely overlaps there.
"""))

    c.append(md("""
### Checkpoint

> Our model scores about 97% on the **test** set. Suppose I now score it on
> the **training** set and get 100%. Is that good news?
"""))
    c.append(L(sol, "train accuracy vs test accuracy", "score the model on X_train too, and compare", """
print("train accuracy:", round(model.score(X_train, y_train), 4))
print("test  accuracy:", round(model.score(X_test,  y_test), 4))

# A small gap is normal. A large gap is overfitting. Training accuracy on
# its own was never the number that mattered.
"""))

    # ================== PART 4 ============================================
    c.append(md("""
---
---
# Part 4 — A third model, and the scaling trap

**Algorithm 3 — K-Nearest Neighbors** does not learn an equation. To classify a new
penguin it finds the `K` most similar penguins it has already seen, and
takes a vote.

"Most similar" means **closest** — and that is where it gets interesting.
"""))

    c.append(md("""
### First, run it on the raw numbers
"""))
    c.append(L(sol, "KNN, unscaled", "KNeighborsClassifier(n_neighbors=5), fit, score", """
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)

acc_unscaled = accuracy_score(y_test, knn.predict(X_test))
print("unscaled:", round(acc_unscaled, 4))
"""))

    c.append(md("""
That is noticeably worse than logistic regression. **Why?**

Look at the numbers: body mass is in the *thousands*, bill length in the
*tens*. When KNN measures distance, a 500 g difference in mass swamps a 5 mm
difference in bill — so it is effectively using mass alone and ignoring the
other two features entirely.

**Scaling** puts every feature on the same footing.
"""))
    c.append(md(img("asset_18_scaling", 880,
                    "the same points before and after standardisation") +
                "\n\n" +
                callout("info",
                        "KNN works out <b>distance</b>: "
                        "<code>d = sqrt(Δbill² + Δmass²)</code>. "
                        "For two penguins 5 mm and 500 g apart that is "
                        "<code>sqrt(25 + 250000)</code> — mass contributes "
                        "250 000, bill contributes 25. Bill length is "
                        "<b>0.01%</b> of the answer.")))
    c.append(L(sol, "KNN, scaled", "StandardScaler().fit(X_train), transform both, refit", """
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler().fit(X_train)     # learn mean+std from TRAIN only

knn.fit(scaler.transform(X_train), y_train)
acc_scaled = accuracy_score(y_test, knn.predict(scaler.transform(X_test)))

print("unscaled:", round(acc_unscaled, 4))
print("scaled:  ", round(acc_scaled, 4))
"""))
    c.append(md("""
> **Fit the scaler on the training set only.** If you fit it on all the data,
> information from the test set leaks into training and your score becomes a
> flattering lie. This is the most common subtle bug in applied ML.

Models have **preconditions**. KNN needs scaled features; logistic regression
mostly shrugs. Knowing which is which is most of the craft.
"""))

    c.append(md("""
### Optional: does K matter?
"""))
    c.append(EX(sol, """
# Try a few values of K and see what happens to accuracy.
for k in [1, 3, 5, 15, 50]:
    m = KNeighborsClassifier(n_neighbors=___)
    m.fit(scaler.transform(X_train), y_train)
    print(k, round(accuracy_score(y_test, m.predict(scaler.transform(X_test))), 4))
""", """
for k in [1, 3, 5, 15, 50]:
    m = KNeighborsClassifier(n_neighbors=k)
    m.fit(scaler.transform(X_train), y_train)
    print(k, round(accuracy_score(y_test, m.predict(scaler.transform(X_test))), 4))

# K=1 trusts the single nearest neighbour — jagged, and noise-sensitive.
# Very large K smooths so much it starts ignoring real structure.
# K is a *hyperparameter*: we choose it, the model does not learn it.
"""))

    # --- Titanic ----------------------------------------------------------
    c.append(md("""
---
---
# The Titanic challenge — in pairs

A messier dataset, on purpose. Penguins were tidy; almost nothing real is.

Your job: get from a raw CSV to a score, using the pattern you now know.
**Nobody is going to tell you the steps in order again.**
"""))
    c.append(code(f"""
tdf = pd.read_csv("{TITANIC_URL}")
print(tdf.shape)
tdf.head()
"""))

    c.append(md("""
### Step 1 — explore

What columns are there? What are you predicting? What is missing?
"""))
    c.append(EX(sol, """
# hint: .info(), .isna().sum(), and value_counts() on 'Survived'

""", """
tdf.info()
print(tdf.isna().sum())
tdf['Survived'].value_counts()

# 891 rows. 'Survived' is the label: 1 = survived, 0 = did not.
# Age is missing for 177 passengers, Cabin for 687 (unusable), Embarked for 2.
"""))

    c.append(md("""
### Step 2 — handle the missing `Age`

177 of 891 passengers have no recorded age. You have three options, and
**all three cost something**:

| option | what it costs |
|---|---|
| **drop the rows** | 20% of your data — and they are not a random 20% |
| **fill with a constant** (`0`, `-1`) | invents an age that is not an age |
| **fill with a statistic** (mean, median) | keeps every row, distorts the distribution |

Filling a gap is called **imputation**. The word matters because it is honest
about what you are doing:
"""))
    c.append(md(callout("key",
        "You are not <i>recovering</i> the missing value. "
        "You are <b>inventing</b> one. Every imputed passenger gets the "
        "<i>same</i> invented age, so they all pile up in one place.")))

    c.append(md("""
Run the cell below to see what a median fill does to the shape of the column
before you decide.
"""))
    c.append(code("""
import matplotlib.pyplot as plt

bins = range(0, 85, 5)
fig, ax = plt.subplots(1, 2, figsize=(11, 3.4), sharey=True)

ax[0].hist(tdf['Age'].dropna(), bins=bins, color='#2E5CA8')
ax[0].set_title(f"observed  (n={tdf['Age'].notna().sum()})")

ax[1].hist(tdf['Age'].fillna(tdf['Age'].median()), bins=bins, color='#E07A2C')
ax[1].set_title(f"after filling with the median ({tdf['Age'].median():.0f})")

for a in ax:
    a.set_xlabel('age (years)')
ax[0].set_ylabel('passengers')
plt.tight_layout(); plt.show()

print("std before:", round(tdf['Age'].std(), 2))
print("std after: ", round(tdf['Age'].fillna(tdf['Age'].median()).std(), 2))
"""))
    c.append(md("""
That spike is 177 people who now share one age. The column looks **less
variable than reality**, and a model reading it will be quietly overconfident
about 28-year-olds.

That may still be the right trade — but it is a trade, and you should be able
to say what you paid.
"""))
    c.append(md(callout("warn",
        "<b>Three rules for imputing.</b><br>"
        "1. Fit the imputer on the <b>training set only</b> — otherwise the "
        "median carries information from the test set into your model. Same "
        "leakage trap as fitting a scaler on all the data.<br>"
        "2. <b>Never impute the label.</b> Inventing answers is not cleaning.<br>"
        "3. <b>Record what you filled.</b> An <code>Age_was_missing</code> "
        "column of 0/1 costs nothing, and on the Titanic it is often "
        "predictive on its own — whose age went unrecorded was not random.")))

    c.append(md("""
Now pick one and do it. Write one sentence below saying why.
"""))
    c.append(EX(sol, """
# option A: tdf = tdf.dropna(subset=['Age'])
# option B: tdf['Age'] = tdf['Age'].fillna(tdf['Age'].median())
# pick one — and write one sentence below saying why

""", """
# Filling with the median keeps all 891 rows; dropping would throw away 20%
# of the data, and the passengers with no recorded age are not a random
# sample (more third-class). Median beats mean here because Age is skewed.

# Rule 3: record what we invented, BEFORE we overwrite it.
tdf['Age_was_missing'] = tdf['Age'].isna().astype(int)
tdf['Age'] = tdf['Age'].fillna(tdf['Age'].median())

print(tdf['Age'].isna().sum(), "missing ages remain")
print(tdf['Age_was_missing'].sum(), "rows flagged as imputed")

# Was the flag worth keeping? Survival rate differs between the two groups,
# so "we don't know this person's age" carries real information.
print(tdf.groupby('Age_was_missing')['Survived'].mean().round(3))
"""))

    c.append(md("""
### Step 3 — make `Sex` numeric

scikit-learn cannot do arithmetic on the word `'female'`. Turn that column
into numbers.
"""))
    c.append(code("""
#@title 💡 Hint for step 3 — click to open only if you need it
# A column of two categories becomes a column of 0/1 like this:
#
#     tdf['Sex_num'] = tdf['Sex'].map({'male': 0, 'female': 1})
#
# For a column with MORE than two categories (like 'Embarked') you would use
# pd.get_dummies(), which makes one 0/1 column per category.
""", collapsed=True))
    c.append(EX(sol, """
tdf['Sex_num'] = ___

tdf[['Sex', 'Sex_num']].head()
""", """
tdf['Sex_num'] = tdf['Sex'].map({'male': 0, 'female': 1})

tdf[['Sex', 'Sex_num']].head()
"""))

    c.append(md("""
### Step 4 — split, fit, predict, score

This is the real assessment. Same four lines as the penguins, new data.
"""))
    c.append(EX(sol, """
Xt = tdf[['Pclass', 'Sex_num', 'Age', 'SibSp']]
yt = tdf['Survived']

Xt_train, Xt_test, yt_train, yt_test = train_test_split(
    ___, ___, test_size=0.2, random_state=42)

tmodel = LogisticRegression(max_iter=1000)
tmodel.___(Xt_train, yt_train)

tpreds = tmodel.___(Xt_test)
print("accuracy:", round(accuracy_score(yt_test, tpreds), 4))
""", """
Xt = tdf[['Pclass', 'Sex_num', 'Age', 'SibSp']]
yt = tdf['Survived']

Xt_train, Xt_test, yt_train, yt_test = train_test_split(
    Xt, yt, test_size=0.2, random_state=42)

tmodel = LogisticRegression(max_iter=1000)
tmodel.fit(Xt_train, yt_train)

tpreds = tmodel.predict(Xt_test)
print("accuracy:", round(accuracy_score(yt_test, tpreds), 4))   # ~0.80

# Worth saying out loud: always guessing "did not survive" scores 0.59 on
# this test split (62% of all passengers died). 0.80 is a real improvement
# over that baseline — but ALWAYS check the baseline first. On an imbalanced
# dataset a high-looking accuracy can mean the model learned nothing.
print("baseline (always predict 0):", round((yt_test == 0).mean(), 4))
ConfusionMatrixDisplay.from_estimator(tmodel, Xt_test, yt_test)
plt.show()
"""))

    c.append(md("""
### Step 5 — *stretch:* does adding `Fare` help?

An honest experiment with an uncertain answer. Add it, re-run, compare.
"""))
    c.append(EX(sol, """
# your experiment here

""", """
for cols in (['Pclass', 'Sex_num', 'Age', 'SibSp'],
             ['Pclass', 'Sex_num', 'Age', 'SibSp', 'Fare']):
    Xa = tdf[cols]
    Xa_tr, Xa_te, ya_tr, ya_te = train_test_split(
        Xa, yt, test_size=0.2, random_state=42)
    m = LogisticRegression(max_iter=1000).fit(Xa_tr, ya_tr)
    print(f"{len(cols)} features: {accuracy_score(ya_te, m.predict(Xa_te)):.4f}")

# Usually barely moves. Fare carries much the same information as Pclass —
# a feature that repeats another is not a new feature. "More columns" is not a strategy.
"""))

    c.append(md("""
---
## Step 6 — enter the mini competition 🏆

The competition on **[Codabench](https://www.codabench.org/competitions/18588/)** uses its own split: 712 passengers with
the answer (`train.csv`) and 179 without it (`test.csv`). Your job: predict
`Survived` for the 179, save `predictions.csv`, zip it and upload the zip.
The leaderboard scores you on passengers you have never seen.

| to beat | accuracy |
|---|---|
| "nobody survived" | 0.615 |
| "only women survived" | 0.782 |
"""))
    c.append(EX(sol, f"""
import zipfile
COMP = "{COMP_URL}"
ctrain = pd.read_csv(COMP + "/train.csv")
ctest  = pd.read_csv(COMP + "/test.csv")

def prepare(df, age_median):
    X = pd.DataFrame()
    X['Pclass']  = df['Pclass']
    X['Sex_num'] = (df['Sex'] == 'female').astype(int)
    X['Age']     = df['Age'].fillna(age_median)      # the TRAIN median
    X['SibSp']   = df['SibSp']
    return X

age_median = ctrain['Age'].median()
cmodel = LogisticRegression(max_iter=1000).fit(prepare(ctrain, age_median), ctrain['Survived'])

sub = pd.DataFrame({{'PassengerId': ctest['PassengerId'],
                    'Survived': cmodel.___(prepare(ctest, age_median))}})
sub.to_csv('predictions.csv', index=False)
with zipfile.ZipFile('submission.zip', 'w') as z:
    z.write('predictions.csv')
print(sub.shape, "→ upload submission.zip on Codabench")
""", f"""
import zipfile
COMP = "{COMP_URL}"
ctrain = pd.read_csv(COMP + "/train.csv")
ctest  = pd.read_csv(COMP + "/test.csv")

def prepare(df, age_median):
    X = pd.DataFrame()
    X['Pclass']  = df['Pclass']
    X['Sex_num'] = (df['Sex'] == 'female').astype(int)
    X['Age']     = df['Age'].fillna(age_median)      # the TRAIN median
    X['SibSp']   = df['SibSp']
    return X

age_median = ctrain['Age'].median()
cmodel = LogisticRegression(max_iter=1000).fit(prepare(ctrain, age_median), ctrain['Survived'])

sub = pd.DataFrame({{'PassengerId': ctest['PassengerId'],
                    'Survived': cmodel.predict(prepare(ctest, age_median))}})
sub.to_csv('predictions.csv', index=False)
with zipfile.ZipFile('submission.zip', 'w') as z:
    z.write('predictions.csv')
print(sub.shape, "→ upload submission.zip on Codabench")
"""))
    c.append(md("""
**In Colab:** open the 📁 *Files* panel on the left, right-click
`submission.zip` → *Download*, then upload it under *My Submissions* on the
competition page. Then improve: the title in `Name` (Mr, Mrs, Miss,
Master…), family size, `Embarked`, another model. Compare ideas with
`cross_val_score` on the training set before spending a submission.
"""))

    c.append(md("""
---
## What you built today

    raw data  →  clean  →  split  →  train  →  evaluate  →  predict

You recognise every box in that line. That is the point.

"""))
    c.append(md(img("asset_19_pipeline", 920,
                    "raw, clean, split, train, evaluate, predict")))
    c.append(md("""
### Three next steps

1. **A course** — the free [scikit-learn MOOC](https://inria.github.io/scikit-learn-mooc/)
   by Inria and the scikit-learn team: today's library, properly.
2. **A dataset** — find one you actually care about and run this exact
   pipeline on it. That is how this becomes yours rather than ours.
3. **A community** — [Kaggle](https://www.kaggle.com/) for competitions and
   notebooks to learn from; [Hugging Face Learn](https://huggingface.co/learn)
   when you are ready for deep learning.

> The most valuable thing you can take from today is not `.fit()`. It is the
> habit of looking at a prediction the model got **wrong** before believing
> the ones it got right.
"""))
    return c


def main():
    OUT.mkdir(exist_ok=True)
    print("Building notebooks…")
    write("NB0-warmup.ipynb", build_nb0())
    write("NB1-python-data.ipynb", build_nb1(sol=False))
    write("NB2-machine-learning.ipynb", build_nb2(sol=False))
    write("NB-SOLUTIONS.ipynb", build_nb1(sol=True) + build_nb2(sol=True))
    if _MISSING_IMG:
        print(f"  WARNING: {len(set(_MISSING_IMG))} diagram(s) not built — "
              f"run `make -C assets tikz` then rebuild: "
              f"{', '.join(sorted(set(_MISSING_IMG)))}")
    print(f"Done. Set GH_USER/GH_REPO in {__file__.split('/')[-1]} to fix the Colab badges.")


if __name__ == "__main__":
    main()
