# Interactive widgets

Plain HTML/JS, no build step. Embedded in the slides via `<iframe class="widget">`.
Shared look in `widget.css`, shared helpers (drag-into-bins game, sliders,
clicker forwarding to the deck) in `widget.js`. `data/*.js` is generated from
`data/*.csv` by `tools/build_widget_data.py`.

| widget | interaction | slide |
|---|---|---|
| `types-sort.html` | drag values into `str` / `int` / `float` / `bool` | Part 1, values and types |
| `mask-filter.html` | threshold slider + species buttons filter a table row by row | Part 1, pandas filtering |
| `class-vs-reg.html` | drag ten tasks into classification / regression | Part 3 |
| `overfit-slider.html` | complexity slider, train vs new error U-curve | Part 3, overfitting |
| `correlation-playground.html` | drag points, watch *r* | Part 3, before linear regression |
| `linreg-playground.html` | drag the line, residuals, MAE, R², animated least-squares fit | Part 3, linear regression |
| `sigmoid-playground.html` | steepness and boundary sliders, probability probe, animated fit | Part 3, logistic regression |
| `threshold-matrix.html` | drag the threshold, live 2×2 confusion matrix on real Titanic predictions | Part 3, evaluation |
| `knn-playground.html` | drag a newcomer, K slider, decision regions, raw vs scaled distance | Part 4, KNN |
| `pipeline-order.html` | drag-to-reorder the six pipeline steps | the wrap-up |

Clicker-safe: once the presenter clicks inside a widget, PageDown/PageUp (and
←/→ when no slider is focused) are forwarded to the deck.
