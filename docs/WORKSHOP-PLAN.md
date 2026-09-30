# Python & Machine Learning Workshop — 2-Hour Plan

> The fast cut of the four-hour workshop. **Same four steps, same order, same
> notebooks** — Python → explore → first model → compare & challenge — with
> the animations removed and the explanations moved off the slides and into
> the notebooks.

| | |
|---|---|
| **Audience** | University students, CS / STEM — no prior Python or ML background |
| **Duration** | 2h wall-clock (1h55 teaching + a 5-minute break) |
| **Environment** | Google Colab — browser only, no install |
| **Balance** | First hour Python for data · second hour applied ML |
| **Datasets** | Palmer Penguins (taught), Titanic (final challenge) |
| **Stack** | numpy · pandas · matplotlib / seaborn · scikit-learn |
| **Deliverables** | 38-slide deck, 3 Colab notebooks + solutions, 9 static diagrams |

---

## What changed from the four-hour version

| | 4 hours | 2 hours |
|---|---|---|
| Slides | 114, one idea per slide | 38, one *step* per slide |
| Animated clips (Manim) | 11 | **none** — replaced by the static diagram or a table |
| In-slide live Python (Pyodide) | 3 cells | **none** — all typing happens in Colab |
| Slide transitions | slide / fade | none |
| Exercise 1 | 6 min | 5 min |
| Independent practice | 20 min, 4 questions | 8 min, questions 1–3 (Q4 is homework) |
| Imputation | 5 slides + clip | 1 slide, with the Titanic numbers |
| Logistic regression maths | clip + 3 slides | 1 slide, both equations |
| KNN | 2 clips + 5 slides | 1 slide + the scaling trap |
| Pretrained image demo | 12 min | **cut** (removed from NB2) |
| Titanic challenge | 20 min | 12 min |
| Break | 15 min | 5 min |

**Nothing in the sequence moved.** A student who later attends — or reads —
the four-hour version meets the same steps in the same order, with more room.

### The fast-version rule

> Show the idea, type the code, move on. If the room needs an explanation,
> it lives in the notebook markdown, not on a slide.

The notebooks were already written to stand alone, so a student who wants
the "why" finds it one scroll below the cell they just ran.

### Honest risk on the timing

> Two hours from zero Python to a scored model is **tight**. It only works if
> most of the room has done **NB0** (the 20-minute warm-up) beforehand. Push
> the pre-work harder than for the four-hour version: it is the difference
> between a room that types along and a room that watches.

---

## Before the workshop

| When | Item | Detail |
|---|---|---|
| **T−3 days** | Pre-work notebook | NB0, 20 min. **Strongly recommended** — say so in the email. |
| **T−3 days** | Setup email | One link. "Open it, click *Copy to Drive*, confirm you see the output of cell 1." |
| **T−1 day** | Reminder | Re-send the link. Run `python tools/check_notebooks.py`. |
| **T−0** | Instructor kit | NB-SOLUTIONS open and run in a second tab, NB1 and NB2 open, backup CSVs to hand. |

---

## Timeline at a glance

Slide numbers are as shown in the deck's corner counter (the title is 1).

| Clock | Block | Slides | Notebook |
|---|---|---|---|
| 0:00 – 0:05 | Welcome, open NB1, run cell 1 | 1–4 | NB1 cell 1 |
| 0:05 – 0:30 | **Part 1 · Python for data** | 5–14 | NB1 Part 1 + Exercise 1 |
| 0:30 – 0:55 | **Part 2 · Explore & visualise** | 15–22 | NB1 Part 2 + practice |
| 0:55 – 1:00 | Break — open NB2, run cell 1 | 23 | NB2 cell 1 |
| 1:00 – 1:30 | **Part 3 · Your first model** | 24–31 | NB2 Part 3 |
| 1:30 – 2:00 | **Part 4 · Compare & challenge** | 32–38 | NB2 Part 4 + Titanic |

---

## Part 1 — Python for data · 0:05 – 0:30

**By 0:30 students can:** run and re-run Colab cells; use variables, lists,
dicts, loops, conditionals and functions; explain why NumPy beats a list;
load a CSV and filter rows.

| Clock | Slide | Do |
|---|---|---|
| 0:05 | Values, names and types | Type 3 variables. `=` vs `==` in one sentence. |
| 0:07 | Lists by position, dicts by name | Zero-indexing is the only thing worth a pause. |
| 0:10 | Loops, choices, functions | Type the loop and `size_label`, don't dissect them. |
| 0:13 | Why NumPy? Speed | Run `%timeit` live. Sixty seconds. |
| 0:15 | One operation, every element | Masking is the bridge to pandas — say so. |
| 0:17 | DataFrame anatomy + selecting | Single vs double brackets: flag it now. |
| 0:20 | **Exercise 1** (5 min) | Circulate. If a third are stuck on task 1 at 3 min, do it on screen. |
| 0:27 | Checkpoint | `df[df['body_mass_g'] > 4000].shape[0]` — a number. |

## Part 2 — Explore & visualise · 0:30 – 0:55

**By 0:55 students can:** summarise with `describe` / `value_counts` /
`groupby`; treat missing values as a decision; make the hue scatter.

| Clock | Slide | Do |
|---|---|---|
| 0:30 | The first three questions | Run all three in NB1. |
| 0:33 | Missing values are a decision | Ask what `dropna` loses **before** running it. |
| 0:36 | Split, apply, combine | One `groupby`, change `.mean()` to `.max()`. |
| 0:38 | Charts: label them | Histogram, then the plain scatter. |
| 0:40 | **The hinge** | Add `hue='species'`. Say: *"those groups are what a classifier learns to draw a line between."* **Never cut.** |
| 0:43 | **Practice** (8 min) | Questions 1–3, pairs. Q4 is homework. |
| 0:52 | Checkpoint | Correlation is not causation — 60 seconds. |

## Break · 0:55 – 1:00

Students open NB2 and run cell 1 **before** they stand up. NB2 loads its own
clean data, so a broken NB1 costs nothing.

## Part 3 — Your first model · 1:00 – 1:30

**By 1:30 students can:** name features and labels; say why we split; train,
predict and score a classifier; read a confusion matrix.

| Clock | Slide | Do |
|---|---|---|
| 1:00 | Machine learning in one slide | "Who writes the `if` statement?" + supervised vs unsupervised. |
| 1:03 | Features, labels, and the split | *You don't grade a student on the questions they studied.* |
| 1:06 | Underfit / good / overfit | The table. Ask which they'd trust. |
| 1:09 | **split → fit → predict → score** | Type all four in NB2 with the arrow-key highlight. Pause on `.fit()`. **Never cut.** |
| 1:17 | What `.fit()` learned | Both equations, one slide. Point at `predict_proba`. |
| 1:21 | 97% of what? | Confusion matrix, then pull up one wrong penguin. |
| 1:27 | Checkpoint | 97% test, 100% train — the gap is the overfitting signal. |

## Part 4 — Compare & challenge · 1:30 – 2:00

**By 2:00 students can:** explain KNN; show why scaling changes its answer;
run the whole pipeline alone on unfamiliar data.

| Clock | Slide | Do |
|---|---|---|
| 1:30 | K-Nearest Neighbors | Vote of the K closest. K is a hyperparameter. |
| 1:33 | The scaling trap | Run unscaled **first** in NB2, ask why it's worse, then scale: 0.82 → 0.99. |
| 1:38 | Fit the scaler on train only | Same leakage rule as the imputer. |
| 1:40 | **Titanic** (12 min) | Pairs. Steps 1–4 are the real assessment; step 5 is for fast finishers. |
| 1:53 | Baseline question | "What does always guessing *did not survive* score?" — 0.59. |
| 1:55 | What you built + next steps | Narrate the pipeline once. Release NB-SOLUTIONS. |

---

## Timing triage — what to cut, in order

| Cut order | Drop this | Saves |
|---|---|---|
| 1st | The `%timeit` demo — just assert NumPy is faster. | 2 min |
| 2nd | "What `.fit()` learned" (equations). | 4 min |
| 3rd | Titanic step 5 (Fare). | 3 min |
| 4th | Run KNN scaled only; tell, don't show, the unscaled result. | 4 min |
| **Never cut** | Exercise 1, the hue scatter, split/fit/predict/score, Titanic steps 1–4. | — |

### If you are ahead

1. Open practice Q4 (the open chart) and show two student charts.
2. Try a few values of K in NB2 and plot accuracy against K.
3. Add `DecisionTreeClassifier` as a third model.

---

## Success criteria

| Measure | Target |
|---|---|
| Students with a working, scored classifier by 1:30 | **Above 85%** |
| Students who complete Titanic steps 1–4 | Above 50% |
| Students who can say why we split train and test | Above 80% |

---

## Visual assets used

9 static TikZ diagrams from the four-hour set, as SVG in the slides and PNG in
the notebooks: 01 variable boxes, 04 list vs array, 06 DataFrame anatomy,
09 good chart, 11 supervised vs unsupervised, 12 train/test split, 15
confusion matrix, 18 scaling, 19 pipeline. Diagrams 02 and 07 appear in the
notebooks only. No clips.

---

*Licensed CC BY 4.0 for content, MIT for code.*
