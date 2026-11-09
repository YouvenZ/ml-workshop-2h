"""
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
SRC = "." if os.path.exists("train.csv") else "https://raw.githubusercontent.com/YouvenZ/ml-workshop-2h/main/codabench/bundle/input_data"
train = pd.read_csv(f"{SRC}/train.csv")
test = pd.read_csv(f"{SRC}/test.csv")


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
print(f"5-fold cross-validated accuracy on train: {cv:.3f}")

model.fit(X_train, y_train)
sub = pd.DataFrame({"PassengerId": test["PassengerId"], "Survived": model.predict(X_test)})
sub.to_csv("predictions.csv", index=False)
with zipfile.ZipFile("submission.zip", "w") as z:
    z.write("predictions.csv")
print("Wrote predictions.csv and submission.zip: upload submission.zip on Codabench.")
