# Backup datasets

Committed on purpose. These are the **fallback** for the one failure mode
that reliably ruins a workshop: a hosted dataset URL being down at 0:03.

The notebooks read from the hosted URLs by default (see `PENGUINS_URL` and
`TITANIC_URL` in `tools/build_notebooks.py`). If `tools/check_notebooks.py`
fails at T−1 day because a URL moved, point those constants at these files'
raw GitHub URLs instead, re-run the generator, and re-push.

| File | Rows | Source |
|---|---|---|
| `penguins.csv` | 344 (333 after `dropna`) | palmerpenguins, via seaborn-data. CC0. |
| `titanic.csv` | 891 | datasciencedojo/datasets. Public domain. |
