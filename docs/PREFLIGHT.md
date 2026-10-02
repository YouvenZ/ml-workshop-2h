# Pre-flight checklist

The workshop plan says what to teach. This says what to check, and when.
Everything here has bitten a live session somewhere.

---

## T−3 days

- [ ] **Send NB0 and the setup email.** One link. The entire instruction is:
      *"Open it, click Copy to Drive, confirm you see the output of cell 1."*
      In the two-hour format, say the warm-up is **expected**, not optional —
      there is no slack to teach `Shift+Enter` on the day.
- [ ] Open the Colab badge links yourself, **in a private window**. A badge
      that works while you are logged in can still 404 for everyone else if
      the repo is private or the branch name is wrong.
- [ ] Confirm the repo is public, or the Colab links will fail for the room.

## T−1 day

- [ ] **Run the dataset check.** This is the single highest-value five
      seconds in the list:

      ```bash
      python tools/check_notebooks.py
      ```

      It executes NB0 and every solution cell against the **live** dataset
      URLs. If Penguins or Titanic has moved, you find out now rather than
      at 0:03 in front of everyone.

- [ ] If a URL has moved, swap in the local backups (`data/penguins.csv`,
      `data/titanic.csv`): change `PENGUINS_URL` / `TITANIC_URL` in
      `tools/build_notebooks.py`, re-run it, re-push.
- [ ] Re-send the link, plus *"bring headphones if you like working ahead"*.
- [ ] Open the deployed slides on the **projector you will actually use**.
      Check the back row can read a code block.

## T−0, before the room fills

- [ ] Slides open, presenter view working (**S** key).
- [ ] **NB-SOLUTIONS open in a second tab**, already run top to bottom.
- [ ] NB1 and NB2 open in two more tabs, cell 1 already run.
- [ ] Click through one clip slide and the correlation playground **on the
      deployed site**, on the projector laptop.
- [ ] **Warm the live Python cells.** Open slide 7 on the deployed site and
      wait for *Run Code* to turn green — the first load downloads Python into
      the browser and took **~2 minutes** in testing. Then run slide 48 once
      (it fetches scikit-learn, another ~1 minute). After that both are cached
      and run in about a second.
- [ ] Wifi checked from where the students will sit, not from the podium.
- [ ] Laptop on mains power, notifications off, screen sleep disabled.
- [ ] A pen. You will want to draw the train/test split on the slide
      (press **B** for the chalkboard).

---

## If something breaks mid-session

| Symptom | Do this |
|---|---|
| A student's notebook is in a weird state | **Runtime → Restart and run all.** Teach it on slide 4, before anyone needs it. |
| A student's NB1 is broken at 0:55 | Nothing. NB2 loads its own data in cell 1. Move them straight to NB2. |
| A hosted dataset URL is down | Have the two backup CSVs ready to upload: in Colab, the folder icon → upload → `pd.read_csv('penguins.csv')`. |
| A live Python cell is still loading | Keep talking and come back to it, or skip it — nothing load-bearing lives in an in-slide cell. The notebook has the same code. |
| A clip won't autoplay | Click it. Clips play once per visit; clicking restarts them. |
| You are running late | Use the cut list in [WORKSHOP-PLAN.md](WORKSHOP-PLAN.md#timing-triage--what-to-cut-in-order). Decide **now**, not at 1:45. |

---

## After

- [ ] Release NB-SOLUTIONS (it is already in the repo — just say so).
- [ ] Note where the room actually got stuck. The plan's timings are a
      hypothesis; your notes are the evidence.
