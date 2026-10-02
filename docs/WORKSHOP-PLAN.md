# Python & Machine Learning Workshop — 2-Hour Plan

> The fast cut of the four-hour workshop. **Same four steps, same order, same
> notebooks, same animations** — Python → explore → first model → compare &
> challenge — with the long explanations moved off the slides and into the
> notebooks. The clips do the explaining now: each one replaces a minute of talk.
>
> Presenter: **Dr. Rachid Zeghlache**, Assistant Professor of Artificial Intelligence, American University in Dubai

| | |
|---|---|
| **Audience** | University students, CS / STEM — no prior Python or ML background |
| **Duration** | 2h wall-clock (1h55 teaching + a 5-minute break) |
| **Environment** | Google Colab — browser only, no install |
| **Balance** | First hour Python for data · second hour applied ML |
| **Datasets** | Palmer Penguins (taught), Titanic (final challenge) |
| **Stack** | numpy · pandas · matplotlib / seaborn · scikit-learn |
| **Deliverables** | 56-slide deck, 12 animated clips, 3 live Python cells, 1 interactive, 9 static diagrams, 3 Colab notebooks + solutions |

---

## What changed from the four-hour version

| | 4 hours | 2 hours |
|---|---|---|
| Slides | 114, one idea per slide | 56, one *step* per slide |
| Animated clips (Manim) | 11 | **all 11 kept** — each replaces the explanation slides around it |
| Correlation playground | during the break | during the break (slide 26) |
| In-slide live Python (Pyodide) | 3 cells | **3 cells**: change a value (7), vectorise & mask (14), **new:** pick your own K on real penguins (49) |
| Exercise 1 | 6 min | 5 min |
| Independent practice | 20 min, 4 questions | 8 min, questions 1–3 (Q4 is homework) |
| Imputation | 5 slides + clip | 1 slide + clip |
| Logistic regression maths | clip + 3 slides | clip + 1 slide, both equations |
| KNN | 3 clips + 5 slides | 3 clips + 1 slide + the scaling trap |
| Pretrained image demo | 12 min | **cut** (removed from NB2) |
| Titanic challenge | 20 min | 12 min |
| Break | 15 min | 5 min |

**Nothing in the sequence moved.** A student who later attends — or reads —
the four-hour version meets the same steps in the same order, with more room.

### The fast-version rule

> Let the clip show the idea, type the code, move on. If the room needs more
> explanation, it lives in the notebook markdown, not on a slide.
>
> Clips play **once** when their slide arrives and stop on their TAKEAWAY
> frame. **Don't talk over a clip** — every one explains itself in 19–29 s.
> When it stops, ask the one question in its speaker notes, then move on.
> Click a clip (or ↻ replay) to run it again. The eleven clips total ~4½
> minutes and replace the explanation you would otherwise give live.

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
| 0:05 – 0:30 | **Part 1 · Python for data** | 5–18 | NB1 Part 1 + Exercise 1 |
| 0:30 – 0:55 | **Part 2 · Explore & visualise** | 19–29 | NB1 Part 2 + practice |
| 0:55 – 1:00 | Break — playground on screen, open NB2 | 28–30 | NB2 cell 1 |
| 1:00 – 1:30 | **Part 3 · Your first model** | 31–44 | NB2 Part 3 |
| 1:30 – 2:00 | **Part 4 · Compare & challenge** | 45–56 | NB2 Part 4 + Titanic |

Live Python slides: 7, 14, 49 — ~90 seconds each; take one suggestion from the
room and run it. Clips: 9 (for-loop), 12 (broadcasting), 22 (imputation), 23
(split-apply-combine), 34 (train/test split), 35 (overfitting), 38 (decision
boundary), 39 (logistic curve), **41 (confusion matrix)**, 46 (KNN), 48 (effect
of K), 50 (KNN distance).

Slide 32 is the rule-based vs machine-learning figure (asset 24). The confusion
matrix runs over three slides: 41 the clip, 42 the annotated real matrix (asset
25: recall per row, precision per column), 43 "what to look at in the errors"
(six habits + classification_report). Slide 44 is the "which model would
you trust?" checkpoint (real accuracies: logistic regression 98.1% train / 97.0%
test vs 1-nearest-neighbour 100% / 80.6%).

---

## Part 1 — Python for data · 0:05 – 0:30

**By 0:30 students can:** run and re-run Colab cells; use variables, lists,
dicts, loops, conditionals and functions; explain why NumPy beats a list;
load a CSV and filter rows.

| Clock | Slide | Do |
|---|---|---|
| 0:05 | Values, names and types → **live:** change a value | `=` vs `==` in one sentence; delete the quotes live and read the error. |
| 0:07 | Lists by position, dicts by name | Zero-indexing is the only thing worth a pause. |
| 0:10 | **Clip:** for-loop → loops, choices, functions | Let the clip explain the loop; type the loop and `size_label`. |
| 0:13 | Why NumPy? Speed | Run `%timeit` live. Sixty seconds. |
| 0:15 | **Clip:** broadcasting → one operation, every element → **live:** masking | Masking is the bridge to pandas — say so. |
| 0:17 | DataFrame anatomy + selecting | Single vs double brackets: flag it now. |
| 0:20 | **Exercise 1** (5 min) | Circulate. If a third are stuck on task 1 at 3 min, do it on screen. |
| 0:27 | Checkpoint | `df[df['body_mass_g'] > 4000].shape[0]` — a number. |

## Part 2 — Explore & visualise · 0:30 – 0:55

**By 0:55 students can:** summarise with `describe` / `value_counts` /
`groupby`; treat missing values as a decision; make the hue scatter.

| Clock | Slide | Do |
|---|---|---|
| 0:30 | The first three questions | Run all three in NB1. |
| 0:33 | Missing values + **clip:** imputation | Ask what `dropna` loses **before** running it; let the 106 → 283 spike land. |
| 0:36 | **Clip:** split-apply-combine → `groupby` | One `groupby`, change `.mean()` to `.max()`. |
| 0:38 | Charts: label them | Histogram, then the plain scatter. |
| 0:40 | **The hinge** | Add `hue='species'`. Say: *"those groups are what a classifier learns to draw a line between."* **Never cut.** |
| 0:43 | **Practice** (8 min) | Questions 1–3, pairs. Q4 is homework. |
| 0:51 | Correlation playground | Two students drag points; hit the *curved* preset. |
| 0:53 | Checkpoint | Correlation is not causation — 60 seconds. |

## Break · 0:55 – 1:00

Students open NB2 and run cell 1 **before** they stand up. NB2 loads its own
clean data, so a broken NB1 costs nothing.

## Part 3 — Your first model · 1:00 – 1:30

**By 1:30 students can:** name features and labels; say why we split; train,
predict and score a classifier; read a confusion matrix.

| Clock | Slide | Do |
|---|---|---|
| 1:00 | Machine learning in one slide | "Who writes the `if` statement?" + supervised vs unsupervised. |
| 1:03 | Features, labels + **clip:** the split | *You don't grade a student on the questions they studied.* |
| 1:06 | **Clip:** overfitting → which would you trust? | Ask which they'd trust **before** the labels appear. |
| 1:09 | **split → fit → predict → score** | Type all four in NB2 with the arrow-key highlight. Pause on `.fit()`. **Never cut.** |
| 1:16 | **Clips:** decision boundary, logistic curve → what `.fit()` learned | Point at `predict_proba`. |
| 1:21 | 97% of what? | Confusion matrix, then pull up one wrong penguin. |
| 1:27 | Checkpoint | 97% test, 100% train — the gap is the overfitting signal. |

## Part 4 — Compare & challenge · 1:30 – 2:00

**By 2:00 students can:** explain KNN; show why scaling changes its answer;
run the whole pipeline alone on unfamiliar data.

| Clock | Slide | Do |
|---|---|---|
| 1:30 | **Clip:** KNN → K-Nearest Neighbors → **clip:** effect of K → **live:** pick your own K → **clip:** distance | Take K values from the room (1, 15, 250). Swap in `body_mass_g` to feel the scaling trap before the slide. |
| 1:33 | The scaling trap | Run unscaled **first** in NB2, ask why it's worse, then scale: 0.82 → 0.99. |
| 1:38 | Fit the scaler on train only | Same leakage rule as the imputer. |
| 1:40 | **Titanic** (12 min) | Pairs. Steps 1–4 are the real assessment; step 5 is for fast finishers. |
| 1:53 | Baseline question | "What does always guessing *did not survive* score?" — 0.59. |
| 1:55 | What you built → next steps → thank you | Narrate the pipeline once. Homework: submit Titanic to Kaggle. Release NB-SOLUTIONS. |

---

## Timing triage — what to cut, in order

| Cut order | Drop this | Saves |
|---|---|---|
| 1st | The `%timeit` demo — just assert NumPy is faster. | 2 min |
| 1½ | The two Part 1 live cells (keep the KNN one). | 3 min |
| 2nd | "What `.fit()` learned" (keep the logistic clip, skip the equation slide). | 3 min |
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

All 22 assets of the four-hour set are in the repo:

- **11 Manim clips** (`assets/manim/scenes.py` → `assets/rendered/*.mp4`, 1280×720,
  ≤30 s, ≤4 MB each; ~4½ minutes in total). Each is a **self-contained
  micro-lesson**: a question as its title, one plain-English caption per step
  (held ~0.3 s per word + 1 s so the back row can read it), real numbers from
  the workshop data, and a **TAKEAWAY** box as the final frame — the frame the
  player stops on. A student who sees only the clip gets the concept.

  | Clip | Question it answers | Takeaway (final frame) | Length |
  |---|---|---|---|
  | 03 for-loop | What does a for loop do? | A loop repeats the same steps for every item in a list. | 29 s |
  | 05 broadcasting | How does NumPy do maths on a whole array? | One operation hits every element — no loop, 50–250× faster. | 21 s |
  | 20 imputation | What happens when you fill in missing ages? | Filling gaps invents data (106 → 283, std 14.5 → 13.0). | 20 s |
  | 08 split-apply-combine | What does groupby do? | Split, apply, combine — one answer per group. | 19 s |
  | 12b train/test split | Why hide some data from the model? | Judge a model on data it has never seen (266 / 67). | 25 s |
  | 13 overfitting | Underfit, good fit, overfit | Overfitting = memorising the examples (training 0.00, new 0.11). | 26 s |
  | 14 decision boundary | What does .fit() actually do? | Nudging the boundaries step by step (23% → 95%). | 23 s |
  | 22 logistic curve | How does the model output a probability? | A weighted score, squashed into a probability. | 25 s |
  | 16 KNN | How does K-Nearest Neighbours decide? | Find the K most similar examples and let them vote (3–2). | 23 s |
  | 17 effect of K | What does K change in KNN? | Too small is jumpy, too large ignores groups (0.99 vs 0.81). | 24 s |
  | 21 KNN distance | What does "nearest" mean for KNN? | Scale your features (25 vs 250 000; 0.82 → 0.99). | 26 s |
- **9 TikZ diagrams** on the slides (01, 04, 06, 09, 11, 12, 15, 18, 19) plus 02
  and 07 in the notebooks only. The pipeline diagram (19) is labelled Part 1–4.
- **1 interactive**: the correlation playground.

---

*Licensed CC BY 4.0 for content, MIT for code.*
