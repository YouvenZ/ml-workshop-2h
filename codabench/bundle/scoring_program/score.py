#!/usr/bin/env python
"""
Scoring program for "Titanic · Who Survives?" (Codabench).

    python score.py <input_dir> <output_dir>

<input_dir>/res/  the participant's submission: one CSV with PassengerId,Survived
<input_dir>/ref/  test_labels.csv: PassengerId,Survived,Sex,Pclass (hidden)

Writes <output_dir>/scores.json (keys = leaderboard columns) and
<output_dir>/detailed_results.html (the per-submission report).

Standard library only, so it runs unchanged in any Codabench docker image.
"""

import csv
import html
import json
import os
import sys

BASELINES = [
    ("Nobody survived", "predict 0 for everyone"),
    ("Only women survived", "predict 1 if Sex is female"),
]


class SubmissionError(Exception):
    pass


# --------------------------------------------------------------------------
# Reading files
# --------------------------------------------------------------------------
def find_submission(res_dir):
    csvs = []
    for root, _, files in os.walk(res_dir):
        if "__MACOSX" in root:
            continue
        for f in files:
            if f.lower().endswith(".csv") and not f.startswith("._"):
                csvs.append(os.path.join(root, f))
    if not csvs:
        raise SubmissionError(
            "No CSV file found in your submission. Zip a file named "
            "predictions.csv (columns PassengerId,Survived) and upload the zip.")
    for c in csvs:
        if os.path.basename(c).lower() == "predictions.csv":
            return c
    if len(csvs) > 1:
        print("WARNING: several CSV files found, using", os.path.basename(sorted(csvs)[0]))
    return sorted(csvs)[0]


def read_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        return list(csv.DictReader(f, dialect=dialect))


def col(row_keys, wanted):
    for k in row_keys:
        if k is not None and k.strip().lower() == wanted.lower():
            return k
    return None


def parse_label(v, pid):
    s = str(v).strip().lower()
    if s in ("1", "1.0", "true", "yes", "survived"):
        return 1
    if s in ("0", "0.0", "false", "no", "died"):
        return 0
    raise SubmissionError(
        f"PassengerId {pid}: Survived must be 0 or 1, got {v!r}. "
        "Did you submit probabilities? Use model.predict(), not predict_proba().")


def load_submission(path, expected_ids):
    rows = read_rows(path)
    if not rows:
        raise SubmissionError("Your predictions file is empty.")
    keys = list(rows[0].keys())
    k_id, k_y = col(keys, "PassengerId"), col(keys, "Survived")
    if not k_id or not k_y:
        raise SubmissionError(
            f"Expected columns PassengerId and Survived, found {keys}. "
            "Tip: sub.to_csv('predictions.csv', index=False)")
    preds = {}
    for r in rows:
        raw = (r.get(k_id) or "").strip()
        if not raw:
            continue
        try:
            pid = int(float(raw))
        except ValueError:
            raise SubmissionError(f"PassengerId {raw!r} is not a number.")
        if pid in preds:
            raise SubmissionError(f"PassengerId {pid} appears more than once.")
        preds[pid] = parse_label(r.get(k_y), pid)
    missing = expected_ids - preds.keys()
    extra = preds.keys() - expected_ids
    if missing:
        raise SubmissionError(
            f"{len(missing)} test passengers have no prediction "
            f"(e.g. PassengerId {sorted(missing)[:5]}). Predict every row of test.csv.")
    if extra:
        print(f"WARNING: ignoring {len(extra)} PassengerIds that are not in test.csv")
    return preds


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------
def confusion(y, p):
    tp = sum(1 for a, b in zip(y, p) if a == 1 and b == 1)
    tn = sum(1 for a, b in zip(y, p) if a == 0 and b == 0)
    fp = sum(1 for a, b in zip(y, p) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(y, p) if a == 1 and b == 0)
    return tp, tn, fp, fn


def metrics(y, p):
    tp, tn, fp, fn = confusion(y, p)
    n = len(y)
    div = lambda a, b: a / b if b else 0.0
    rec = div(tp, tp + fn)
    spec = div(tn, tn + fp)
    prec = div(tp, tp + fp)
    return {
        "accuracy": div(tp + tn, n),
        "balanced_accuracy": (rec + spec) / 2,
        "f1": div(2 * prec * rec, prec + rec),
        "precision": prec,
        "recall": rec,
        "_cm": (tp, tn, fp, fn),
    }


# --------------------------------------------------------------------------
# The detailed report shown next to each submission
# --------------------------------------------------------------------------
def report(m, base, groups, n, filename):
    tp, tn, fp, fn = m["_cm"]
    acc = m["accuracy"]
    best_base = max(b["accuracy"] for _, _, b in base)
    if acc >= 0.85:
        verdict, vcol = "Outstanding: you are in expert territory.", "#2A9D8F"
    elif acc > best_base:
        verdict, vcol = "You beat every baseline. That is a real model.", "#2A9D8F"
    elif acc > base[0][2]["accuracy"]:
        verdict, vcol = "Better than guessing, but “only women survived” still wins. Keep going!", "#E07A2C"
    else:
        verdict, vcol = "No better than predicting that nobody survived. Check your features.", "#E07A2C"

    def bar(label, sub, value, colour, bold=False):
        return f"""
        <div class="bar{' me' if bold else ''}">
          <div class="bl"><b>{html.escape(label)}</b><span>{html.escape(sub)}</span></div>
          <div class="bt"><i style="width:{value * 100:.1f}%;background:{colour}"></i></div>
          <div class="bv">{value:.3f}</div>
        </div>"""

    bars = bar("Your submission", filename, acc, "#2E5CA8", True)
    for name, sub, b in base:
        bars += bar(name, sub, b["accuracy"], "#AEB5C2")

    grows = "".join(
        f"<tr><td>{html.escape(g)}</td><td>{c}/{k}</td>"
        f"<td><div class='mini'><i style='width:{c / k * 100:.0f}%'></i></div></td>"
        f"<td><b>{c / k:.0%}</b></td></tr>"
        for g, (c, k) in groups.items())

    tiles = "".join(
        f"<div class='tile'><span>{lab}</span><b>{m[key]:.3f}</b></div>"
        for key, lab in [("balanced_accuracy", "Balanced accuracy"), ("f1", "F1 (survived)"),
                         ("precision", "Precision"), ("recall", "Recall")])

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Your Titanic results</title>
<style>
  :root{{--navy:#1B2A4A;--blue:#2E5CA8;--orange:#E07A2C;--teal:#2A9D8F;--gray:#D9DCE1;--muted:#6b7689}}
  *{{box-sizing:border-box}}
  body{{margin:0;font:15px/1.5 Inter,"Helvetica Neue",Arial,sans-serif;color:var(--navy);background:#F4F6FA}}
  .hero{{background:linear-gradient(135deg,#14203A,#22365E);color:#fff;padding:28px 32px 26px;border-radius:0 0 22px 22px}}
  .kick{{color:var(--orange);font-weight:800;letter-spacing:.2em;font-size:12px}}
  .hero h1{{margin:6px 0 4px;font-size:26px}}
  .score{{display:flex;align-items:baseline;gap:14px;margin-top:10px;flex-wrap:wrap}}
  .score b{{font-size:58px;line-height:1;font-weight:800}}
  .score span{{color:rgba(255,255,255,.75)}}
  .verdict{{margin-top:10px;display:inline-block;padding:6px 14px;border-radius:999px;background:rgba(255,255,255,.1);font-weight:600}}
  .wrap{{max-width:980px;margin:0 auto;padding:22px 20px 40px;display:grid;gap:18px}}
  .card{{background:#fff;border-radius:16px;padding:18px 20px;box-shadow:0 1px 2px rgba(27,42,74,.06),0 12px 30px -18px rgba(27,42,74,.35)}}
  h2{{font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 12px}}
  .tiles{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
  .tile{{background:#F6F8FB;border-radius:12px;padding:12px 14px;border-top:4px solid var(--blue)}}
  .tile:nth-child(2){{border-color:var(--teal)}} .tile:nth-child(3){{border-color:var(--orange)}} .tile:nth-child(4){{border-color:var(--navy)}}
  .tile span{{display:block;font-size:12px;color:var(--muted);font-weight:600}}
  .tile b{{font-size:24px}}
  .two{{display:grid;grid-template-columns:1fr 1.2fr;gap:18px}}
  .cm{{display:grid;grid-template-columns:auto 1fr 1fr;gap:8px;align-items:stretch}}
  .cm .h{{font-size:12px;color:var(--muted);font-weight:700;text-align:center}}
  .cm .r{{font-size:12px;color:var(--muted);font-weight:700;align-self:center;text-align:right}}
  .cell{{border-radius:12px;padding:14px 8px;text-align:center}}
  .cell b{{display:block;font-size:30px;line-height:1.1}}
  .cell span{{font-size:12px;font-weight:600}}
  .ok{{background:rgba(42,157,143,.14);color:#1f7a70}} .bad{{background:rgba(224,122,44,.14);color:#b85d17}}
  .bar{{display:grid;grid-template-columns:200px 1fr 56px;gap:12px;align-items:center;padding:7px 0}}
  .bar.me .bl b{{color:var(--blue)}}
  .bl span{{display:block;font-size:12px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
  .bt{{height:14px;border-radius:7px;background:#EEF0F4;overflow:hidden}} .bt i{{display:block;height:100%;border-radius:7px}}
  .bv{{font-weight:800;text-align:right;font-variant-numeric:tabular-nums}}
  table{{width:100%;border-collapse:collapse;font-size:14px}}
  td{{padding:7px 6px;border-bottom:1px solid #EEF0F4}} tr:last-child td{{border:0}}
  .mini{{height:8px;border-radius:4px;background:#EEF0F4;width:120px;overflow:hidden}} .mini i{{display:block;height:100%;background:var(--teal)}}
  .tip{{font-size:14px;color:var(--navy);background:#FDF2E9;border-left:4px solid var(--orange);border-radius:0 10px 10px 0;padding:10px 14px}}
  @media (max-width:720px){{.tiles{{grid-template-columns:repeat(2,1fr)}}.two{{grid-template-columns:1fr}}.bar{{grid-template-columns:120px 1fr 50px}}}}
</style></head><body>
<div class="hero">
  <div class="kick">TITANIC · WHO SURVIVES?</div>
  <h1>Your results on {n} unseen passengers</h1>
  <div class="score"><b>{acc:.1%}</b><span>accuracy · {tp + tn} of {n} passengers right</span></div>
  <div class="verdict" style="color:{vcol if vcol != '#E07A2C' else '#FFC48F'}">{html.escape(verdict)}</div>
</div>
<div class="wrap">
  <div class="card"><h2>Every score</h2><div class="tiles">{tiles}</div></div>
  <div class="two">
    <div class="card"><h2>Confusion matrix</h2>
      <div class="cm">
        <div></div><div class="h">said: died</div><div class="h">said: survived</div>
        <div class="r">really died</div><div class="cell ok"><b>{tn}</b><span>correct</span></div><div class="cell bad"><b>{fp}</b><span>false alarm</span></div>
        <div class="r">really survived</div><div class="cell bad"><b>{fn}</b><span>missed</span></div><div class="cell ok"><b>{tp}</b><span>correct</span></div>
      </div>
    </div>
    <div class="card"><h2>Against the baselines</h2>{bars}</div>
  </div>
  <div class="card"><h2>Where are you right? Accuracy by group</h2>
    <table>{grows}</table>
  </div>
  <div class="tip"><b>Next step:</b> compare your accuracy by group. If one group is much worse, a feature
  that describes it (class, age, family size, the title in the name…) may be missing from your model.</div>
</div>
</body></html>"""


# --------------------------------------------------------------------------
def main():
    input_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./output"
    os.makedirs(output_dir, exist_ok=True)

    ref_rows = read_rows(os.path.join(input_dir, "ref", "test_labels.csv"))
    truth = {int(r["PassengerId"]): int(r["Survived"]) for r in ref_rows}
    info = {int(r["PassengerId"]): r for r in ref_rows}
    ids = sorted(truth)

    sub_path = find_submission(os.path.join(input_dir, "res"))
    print("Scoring", os.path.basename(sub_path))
    preds = load_submission(sub_path, set(ids))

    y = [truth[i] for i in ids]
    p = [preds[i] for i in ids]
    m = metrics(y, p)

    base = [
        (BASELINES[0][0], BASELINES[0][1], metrics(y, [0] * len(ids))),
        (BASELINES[1][0], BASELINES[1][1],
         metrics(y, [1 if info[i]["Sex"] == "female" else 0 for i in ids])),
    ]

    groups = {}
    for label, key, fmt in [("Women", "Sex", "female"), ("Men", "Sex", "male"),
                            ("1st class", "Pclass", "1"), ("2nd class", "Pclass", "2"),
                            ("3rd class", "Pclass", "3")]:
        sel = [i for i in ids if info[i][key] == fmt]
        if sel:
            groups[label] = (sum(1 for i in sel if preds[i] == truth[i]), len(sel))

    scores = {k: round(v, 6) for k, v in m.items() if not k.startswith("_")}
    with open(os.path.join(output_dir, "scores.json"), "w") as f:
        json.dump(scores, f)
    with open(os.path.join(output_dir, "detailed_results.html"), "w", encoding="utf-8") as f:
        f.write(report(m, base, groups, len(ids), os.path.basename(sub_path)))

    for k, v in scores.items():
        print(f"{k:>18}: {v:.4f}")


if __name__ == "__main__":
    try:
        main()
    except SubmissionError as e:
        # Shown to the participant in the submission's error log.
        print("SUBMISSION ERROR:", e, file=sys.stderr)
        sys.exit(1)
