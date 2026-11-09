#!/usr/bin/env python3
"""
Build the Codabench competition bundle for the workshop's closing challenge.

    python codabench/build_bundle.py

1. splits data/titanic.csv into a public train set (712 passengers, with
   labels), a public test set (179, without) and the hidden answer key;
2. writes the starting kit (notebook, baseline script, sample submission);
3. self-tests the scoring program on three reference submissions;
4. zips codabench/bundle/ into codabench/dist/titanic-who-survives_bundle.zip,
   the file you upload at codabench.org → Benchmarks → Upload.

Everything is regenerated from scratch, so the bundle can never drift from
the data or the scorer. Re-run it after editing anything in bundle/.
"""

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import zipfile

import pandas as pd
from sklearn.model_selection import train_test_split

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
B = HERE / "bundle"
DIST = HERE / "dist"
SEED = 2026
N_TEST = 179
RAW = "https://raw.githubusercontent.com/YouvenZ/ml-workshop-2h/main/codabench/bundle/input_data"

# --------------------------------------------------------------------------
# 1. Data
# --------------------------------------------------------------------------
df = pd.read_csv(ROOT / "data" / "titanic.csv")
train, test = train_test_split(df, test_size=N_TEST, random_state=SEED, stratify=df["Survived"])
train = train.sort_values("PassengerId")
test = test.sort_values("PassengerId")

for d in ("input_data", "reference_data"):
    shutil.rmtree(B / d, ignore_errors=True)
    (B / d).mkdir(parents=True)

train.to_csv(B / "input_data" / "train.csv", index=False)
test.drop(columns=["Survived"]).to_csv(B / "input_data" / "test.csv", index=False)
sample = pd.DataFrame({"PassengerId": test["PassengerId"], "Survived": 0})
sample.to_csv(B / "input_data" / "sample_submission.csv", index=False)
test[["PassengerId", "Survived", "Sex", "Pclass"]].to_csv(
    B / "reference_data" / "test_labels.csv", index=False)
(B / "input_data" / "README.md").write_text(f"""# Titanic · Who Survives? — data

| file | rows | what it is |
|---|---|---|
| `train.csv` | {len(train)} | passengers **with** the answer (`Survived`: 1 = survived, 0 = died) |
| `test.csv` | {len(test)} | passengers **without** the answer: predict these |
| `sample_submission.csv` | {len(test)} | the exact format to upload (everyone predicted 0) |

Columns: PassengerId, Survived (train only), Pclass, Name, Sex, Age, SibSp,
Parch, Ticket, Fare, Cabin, Embarked. See the *Data* page of the competition.
""")

# --------------------------------------------------------------------------
# 2. Starting kit
# --------------------------------------------------------------------------
KIT = B / "starting_kit"
shutil.rmtree(KIT, ignore_errors=True)
KIT.mkdir()
for f in ("train.csv", "test.csv", "sample_submission.csv"):
    shutil.copy(B / "input_data" / f, KIT / f)

BASELINE = f'''"""
Baseline for Titanic · Who Survives?  Produces submission.zip, ready to upload.

    python baseline.py

Logistic regression on 5 features, the same split → fit → predict pattern
as the workshop. Beat it!
"""
import os
import zipfile

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

# Local files if present (starting kit), otherwise straight from GitHub.
SRC = "." if os.path.exists("train.csv") else "{RAW}"
train = pd.read_csv(f"{{SRC}}/train.csv")
test = pd.read_csv(f"{{SRC}}/test.csv")


def prepare(df, age_median):
    X = pd.DataFrame()
    X["Pclass"] = df["Pclass"]
    X["is_female"] = (df["Sex"] == "female").astype(int)
    X["Age"] = df["Age"].fillna(age_median)      # fill with the TRAIN median
    X["Fare"] = df["Fare"].fillna(0)
    X["family"] = df["SibSp"] + df["Parch"]
    return X


age_median = train["Age"].median()
X_train, y_train = prepare(train, age_median), train["Survived"]
X_test = prepare(test, age_median)

model = LogisticRegression(max_iter=1000)
cv = cross_val_score(model, X_train, y_train, cv=5).mean()
print(f"5-fold cross-validated accuracy on train: {{cv:.3f}}")

model.fit(X_train, y_train)
sub = pd.DataFrame({{"PassengerId": test["PassengerId"], "Survived": model.predict(X_test)}})
sub.to_csv("predictions.csv", index=False)
with zipfile.ZipFile("submission.zip", "w") as z:
    z.write("predictions.csv")
print("Wrote predictions.csv and submission.zip: upload submission.zip on Codabench.")
'''
(KIT / "baseline.py").write_text(BASELINE)


def md(t):
    return {"cell_type": "markdown", "metadata": {}, "source": t.strip("\n").splitlines(True)}


def code(t):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": t.strip("\n").splitlines(True)}


cells = [
    md("""
# 🚢 Titanic · Who Survives? — starting kit

**Python & ML Workshop · American University in Dubai**

Your mission: predict which of the **179 test passengers** survived, then
upload your predictions to the Codabench leaderboard.

The plan is the one from the workshop: **load → explore → prepare → split →
fit → predict → score → submit.** Run every cell once to make a valid
submission in under a minute, then make it better.
"""),
    md("## 1 · Load the data"),
    code(f"""
import os, zipfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Works in the starting kit folder, and in Google Colab (reads from GitHub).
SRC = "." if os.path.exists("train.csv") else "{RAW}"
train = pd.read_csv(f"{{SRC}}/train.csv")
test  = pd.read_csv(f"{{SRC}}/test.csv")
print(train.shape, test.shape)
train.head()
"""),
    md("## 2 · Explore: the first three questions"),
    code("""
print(train['Survived'].value_counts(normalize=True).round(3))   # the baseline
train.isna().sum()
"""),
    code("""
train.groupby('Sex')['Survived'].mean().plot(kind='bar', color=['#E07A2C', '#2E5CA8'])
plt.ylabel('survival rate'); plt.title('Survival rate by sex'); plt.show()
"""),
    md("""
## 3 · Two baselines to beat

| baseline | idea |
|---|---|
| *Nobody survived* | predict 0 for everyone |
| *Only women survived* | predict 1 if `Sex == 'female'` |

A model is only interesting if it beats these.
"""),
    md("## 4 · Prepare the features (numbers only, no gaps)"),
    code("""
def prepare(df, age_median):
    X = pd.DataFrame()
    X['Pclass']    = df['Pclass']
    X['is_female'] = (df['Sex'] == 'female').astype(int)
    X['Age']       = df['Age'].fillna(age_median)   # fill with the TRAIN median
    X['Fare']      = df['Fare'].fillna(0)
    X['family']    = df['SibSp'] + df['Parch']
    return X

age_median = train['Age'].median()
X, y = prepare(train, age_median), train['Survived']
X_test = prepare(test, age_median)
X.head()
"""),
    md("## 5 · Split → fit → predict → score (on your own validation set)"),
    code("""
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model = LogisticRegression(max_iter=1000).fit(X_tr, y_tr)
print('validation accuracy:', round(accuracy_score(y_val, model.predict(X_val)), 3))
"""),
    md("""
## 6 · Make it better

Ideas, from easy to clever:

- try `KNeighborsClassifier` (scale the features first!) or `RandomForestClassifier`
- add `Embarked` (one-hot with `pd.get_dummies`)
- extract the **title** from `Name` (Mr, Mrs, Miss, Master…): it encodes sex *and* age
- does having a `Cabin` number tell you anything?
- use `cross_val_score(model, X, y, cv=5)` to compare ideas honestly
"""),
    md("## 7 · Train on all of train.csv, predict test.csv, write the submission"),
    code("""
model = LogisticRegression(max_iter=1000).fit(X, y)

sub = pd.DataFrame({'PassengerId': test['PassengerId'],
                    'Survived': model.predict(X_test)})
sub.to_csv('predictions.csv', index=False)
with zipfile.ZipFile('submission.zip', 'w') as z:
    z.write('predictions.csv')
print(sub.shape, sub['Survived'].mean().round(3), '→ submission.zip is ready')
"""),
    md("""
## 8 · Submit

Codabench → **My Submissions** → upload **`submission.zip`**. Your score and a
detailed report (confusion matrix, baselines, accuracy by group) appear within
a minute. In Colab, download the zip first from the 📁 Files panel.
"""),
]
nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python3"},
                                    "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
(KIT / "starting_kit.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
(KIT / "README.md").write_text("""# Starting kit — Titanic · Who Survives?

| file | what it is |
|---|---|
| `starting_kit.ipynb` | step-by-step notebook: explore, baselines, a first model, the submission |
| `baseline.py` | the same model as one script: `python baseline.py` → `submission.zip` |
| `train.csv` / `test.csv` | the data (also on the *Files* tab of the competition) |
| `sample_submission.csv` | the exact format: `PassengerId,Survived` with one row per test passenger |

**Submit** a `.zip` containing one file, `predictions.csv`, with a 0 or 1 for every
`PassengerId` in `test.csv`.
""")

# --------------------------------------------------------------------------
# 3. Self-test the scorer
# --------------------------------------------------------------------------
def score(pred_df, label):
    with tempfile.TemporaryDirectory() as t:
        t = pathlib.Path(t)
        (t / "in" / "res").mkdir(parents=True)
        shutil.copytree(B / "reference_data", t / "in" / "ref")
        pred_df.to_csv(t / "in" / "res" / "predictions.csv", index=False)
        r = subprocess.run([sys.executable, str(B / "scoring_program" / "score.py"),
                            str(t / "in"), str(t / "out")], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"scorer failed on {label}:\n{r.stdout}\n{r.stderr}")
        s = json.loads((t / "out" / "scores.json").read_text())
        if label == "baseline model":
            shutil.copy(t / "out" / "detailed_results.html", DIST / "example_detailed_results.html")
        print(f"  {label:<22} accuracy {s['accuracy']:.3f} · balanced {s['balanced_accuracy']:.3f} · F1 {s['f1']:.3f}")
        return s


DIST.mkdir(exist_ok=True)
print("Scorer self-test on the hidden test set:")
score(sample, "nobody survived")
score(pd.DataFrame({"PassengerId": test["PassengerId"],
                    "Survived": (test["Sex"] == "female").astype(int)}), "only women survived")
with tempfile.TemporaryDirectory() as t:
    for f in ("baseline.py", "train.csv", "test.csv"):
        shutil.copy(KIT / f, t)
    subprocess.run([sys.executable, "baseline.py"], cwd=t, check=True, capture_output=True)
    base_pred = pd.read_csv(pathlib.Path(t) / "predictions.csv")
    shutil.copy(pathlib.Path(t) / "submission.zip", DIST / "example_submission.zip")
score(base_pred, "baseline model")

# --------------------------------------------------------------------------
# 4. Zip the bundle (competition.yaml must sit at the root of the zip)
# --------------------------------------------------------------------------
out = DIST / "titanic-who-survives_bundle.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(B.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            z.write(p, p.relative_to(B))
print(f"\nBundle: {out.relative_to(ROOT)}  ({out.stat().st_size / 1024:.0f} KB) — upload this file.")
