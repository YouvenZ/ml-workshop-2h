"""
Manim Community Edition scenes for the Python & ML workshop.

All 7 clips live in this one file so the shared palette and helpers stay
consistent. Render everything with:

    make -C assets manim

or one scene at a time:

    manim -qm --format=mp4 assets/manim/scenes.py OverfitUnderfit

-qm is deliberate: it is exactly 1280x720 @30fps, which is the size the
asset spec calls for. -qh would be 1080p60 and three times the file size
for no visible gain on a projector.
"""

import pathlib

import numpy as np
from manim import *

# ---------------------------------------------------------------------
# Shared visual system — identical hex values to the TikZ diagrams and
# the slide theme. Blue always means the same thing across all 19 assets.
# ---------------------------------------------------------------------
NAVY = "#1B2A4A"
BLUE = "#2E5CA8"
ORANGE = "#E07A2C"
TEAL = "#2A9D8F"
GRAY = "#D9DCE1"

SPECIES_COLOR = {"Adelie": BLUE, "Chinstrap": ORANGE, "Gentoo": TEAL}

config.background_color = WHITE
Text.set_default(color=NAVY, font="Inter")
MathTex.set_default(color=NAVY)

DATA = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "penguins.csv"
PENGUINS_URL = ("https://raw.githubusercontent.com/mwaskom/seaborn-data/"
                "master/penguins.csv")
TITANIC = DATA.parent / "titanic.csv"
TITANIC_URL = ("https://raw.githubusercontent.com/datasciencedojo/datasets/"
               "master/titanic.csv")


def load_penguins():
    """Two well-separated features, scaled to [0,1]. Local file, URL fallback."""
    import pandas as pd

    src = DATA if DATA.exists() else PENGUINS_URL
    df = pd.read_csv(src).dropna()
    X = df[["bill_length_mm", "flipper_length_mm"]].to_numpy(float)
    X = (X - X.min(0)) / (X.max(0) - X.min(0))
    return X, df["species"].to_numpy()


def panel(width=3.6, height=2.6, center=ORIGIN):
    """A framed plotting box plus a data->scene mapping for it.

    Manim's Axes carry a lot of furniture (ticks, numbers) that is noise at
    this size. A plain frame and a mapping function reads cleaner on a
    projector and keeps every panel pixel-identical.
    """
    frame = Rectangle(width=width, height=height,
                      stroke_color=GRAY, stroke_width=3).move_to(center)
    pad = 0.12

    def to_pt(x, y):
        x = np.clip(x, -0.05, 1.05)
        y = np.clip(y, -0.05, 1.05)
        return center + np.array([
            (x - 0.5) * (width - 2 * pad),
            (y - 0.5) * (height - 2 * pad),
            0.0,
        ])

    return frame, to_pt


def curve_through(to_pt, xs, ys, color, width=5):
    """A smooth VMobject through mapped points — used for every fitted line."""
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly(
        [to_pt(x, y) for x, y in zip(xs, ys)]
    )


def boundary_image(clf, resolution=200):
    """Render a classifier's decision regions as a soft RGB image.

    Returned as an ImageMobject rather than a grid of squares: one raster
    fades into the next cleanly, and it is a few hundred KB instead of a
    thousand mobjects.
    """
    g = np.linspace(0, 1, resolution)
    xx, yy = np.meshgrid(g, g)
    grid = np.c_[xx.ravel(), yy.ravel()]
    labels = clf.predict(grid).reshape(resolution, resolution)

    rgb = np.zeros((resolution, resolution, 3), dtype=np.uint8)
    for name, hexcode in SPECIES_COLOR.items():
        c = np.array([int(hexcode[i:i + 2], 16) for i in (1, 3, 5)])
        tint = (255 - (255 - c) * 0.28).astype(np.uint8)   # pale wash
        rgb[labels == name] = tint
    return np.flipud(rgb)      # image rows run top-down, data runs bottom-up


# =====================================================================
# Asset 3 — for-loop walkthrough.  GIF, ~10s.  Tier 1.
# =====================================================================
class ForLoopWalkthrough(Scene):
    """A pointer sweeps a list, an accumulator updates live."""

    def construct(self):
        values = [3750, 3800, 3250, 3450]

        boxes = VGroup(*[
            VGroup(
                Square(side_length=1.3, color=GRAY, fill_opacity=1,
                       fill_color=WHITE, stroke_width=3),
                Text(str(v), font_size=28),
            )
            for v in values
        ]).arrange(RIGHT, buff=0.25).shift(UP * 0.8)

        for box in boxes:
            box[1].move_to(box[0].get_center())

        title = Text("for m in masses:", font_size=34, color=BLUE).to_edge(UP)
        total = 0
        acc = Text("total = 0", font_size=30, color=TEAL).shift(DOWN * 1.8)

        self.play(Write(title), FadeIn(boxes), Write(acc))
        self.wait(0.4)

        pointer = Triangle(color=ORANGE, fill_opacity=1)\
            .scale(0.18).rotate(PI)\
            .next_to(boxes[0], UP, buff=0.2)
        self.play(FadeIn(pointer))

        for i, v in enumerate(values):
            if i > 0:
                self.play(pointer.animate.next_to(boxes[i], UP, buff=0.2),
                          run_time=0.45)
            self.play(boxes[i][0].animate.set_fill(ORANGE, opacity=0.25),
                      run_time=0.3)
            total += v
            new_acc = Text(f"total = {total}", font_size=30, color=TEAL)\
                .move_to(acc)
            self.play(Transform(acc, new_acc), run_time=0.45)
            self.play(boxes[i][0].animate.set_fill(WHITE, opacity=1),
                      run_time=0.25)

        self.play(FadeOut(pointer))
        self.wait(1.2)


# =====================================================================
# Asset 12 companion — train / test split.  MP4, ~8s.
# =====================================================================
class TrainTestSplit(Scene):
    """One bar of data splitting 80 / 20."""

    def construct(self):
        title = Text("Split before you train", font_size=38).to_edge(UP)
        self.play(Write(title))

        blocks = VGroup(*[
            Square(side_length=0.55, stroke_width=2,
                   stroke_color=NAVY, fill_opacity=1, fill_color=GRAY)
            for _ in range(20)
        ]).arrange_in_grid(rows=2, cols=10, buff=0.08)
        self.play(FadeIn(blocks, lag_ratio=0.04))
        self.wait(0.5)

        train = VGroup(*blocks[:16])
        test = VGroup(*blocks[16:])

        self.play(
            train.animate.set_fill(BLUE).shift(LEFT * 1.2),
            test.animate.set_fill(ORANGE).shift(RIGHT * 1.2),
            run_time=1.4,
        )

        lbl_train = Text("train  80%", font_size=26, color=BLUE)\
            .next_to(train, DOWN, buff=0.45)
        lbl_test = Text("test  20%", font_size=26, color=ORANGE)\
            .next_to(test, DOWN, buff=0.45)
        self.play(Write(lbl_train), Write(lbl_test))

        note = Text("You don't grade a student on the questions they studied.",
                    font_size=24, color=NAVY).to_edge(DOWN)
        self.play(FadeIn(note, shift=UP * 0.2))
        self.wait(2)


# =====================================================================
# Asset 5 — broadcasting.  GIF, ~8s.  Tier 2.
# =====================================================================
class Broadcasting(Scene):
    """A scalar fans out across every element, then a full array-to-array op."""

    def construct(self):
        def row(values, color, fs=26):
            g = VGroup(*[
                VGroup(
                    Square(side_length=1.05, stroke_width=3, stroke_color=color,
                           fill_color=WHITE, fill_opacity=1),
                    Text(str(v), font_size=fs),
                )
                for v in values
            ]).arrange(RIGHT, buff=0.18)
            for cell in g:
                cell[1].move_to(cell[0].get_center())
            return g

        a = [3750, 3800, 3250, 3450]

        title = Text("a * 2", font_size=40, color=BLUE).to_edge(UP)
        arr = row(a, NAVY).shift(UP * 1.0)
        self.play(Write(title), FadeIn(arr))

        # --- scalar fans out to every element at once ---------------------
        scalar = Text("2", font_size=38, color=ORANGE).next_to(arr, DOWN, buff=1.1)
        self.play(FadeIn(scalar, scale=0.6))

        arrows = VGroup(*[
            Arrow(scalar.get_top(), cell[0].get_bottom(), buff=0.12,
                  stroke_width=3, color=ORANGE, max_tip_length_to_length_ratio=0.12)
            for cell in arr
        ])
        self.play(LaggedStart(*[GrowArrow(x) for x in arrows], lag_ratio=0.12),
                  run_time=1.0)

        doubled = row([v * 2 for v in a], ORANGE).move_to(arr)
        self.play(FadeOut(arrows), FadeOut(scalar),
                  ReplacementTransform(arr, doubled), run_time=0.9)
        self.wait(0.5)

        note = Text("one operation, every element — no loop",
                    font_size=26, color=TEAL).next_to(doubled, DOWN, buff=0.9)
        self.play(FadeIn(note, shift=UP * 0.15))
        self.wait(1.0)

        # --- array to array -----------------------------------------------
        self.play(FadeOut(note), FadeOut(doubled),
                  Transform(title, Text("a + b", font_size=40, color=BLUE).to_edge(UP)))

        b = [50, 100, 25, 75]
        top = row(a, NAVY).shift(UP * 1.25)
        mid = row(b, TEAL).shift(UP * 0.05)
        plus = Text("+", font_size=34, color=NAVY).next_to(mid, LEFT, buff=0.3)
        self.play(FadeIn(top), FadeIn(mid), Write(plus))
        self.wait(0.4)

        line = Line(mid.get_left() + LEFT * 0.35, mid.get_right() + RIGHT * 0.15,
                    color=NAVY, stroke_width=3).next_to(mid, DOWN, buff=0.22)
        out = row([x + y for x, y in zip(a, b)], ORANGE)\
            .next_to(line, DOWN, buff=0.22)
        self.play(Create(line))
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in out],
                              lag_ratio=0.15), run_time=1.0)
        self.wait(1.6)


# =====================================================================
# Asset 8 — split / apply / combine.  GIF, ~12s.  Tier 1.
# =====================================================================
class SplitApplyCombine(Scene):
    """Rows sort into coloured buckets, each collapses to one number,
    then the numbers recombine into the result table."""

    def construct(self):
        rows_spec = [
            ("Adelie", 3750), ("Gentoo", 5000), ("Chinstrap", 3733),
            ("Adelie", 3800), ("Gentoo", 5200), ("Adelie", 3568),
            ("Chinstrap", 3733), ("Gentoo", 5076),
        ]

        title = Text("df.groupby('species')['body_mass_g'].mean()",
                     font_size=30, color=BLUE).to_edge(UP)
        self.play(Write(title))

        def make_row(sp, mass):
            box = RoundedRectangle(width=3.0, height=0.46, corner_radius=0.08,
                                   stroke_width=2.5,
                                   stroke_color=SPECIES_COLOR[sp],
                                   fill_color=WHITE, fill_opacity=1)
            label = Text(f"{sp}   {mass}", font_size=19,
                         color=SPECIES_COLOR[sp]).move_to(box)
            return VGroup(box, label)

        table = VGroup(*[make_row(s, m) for s, m in rows_spec])\
            .arrange(DOWN, buff=0.1).shift(LEFT * 4.1 + DOWN * 0.3)
        self.play(LaggedStart(*[FadeIn(r) for r in table], lag_ratio=0.08),
                  run_time=1.2)
        self.wait(0.4)

        # --- SPLIT ---------------------------------------------------------
        step = Text("split", font_size=26, color=NAVY).to_edge(DOWN, buff=0.45)
        self.play(FadeIn(step))

        order = ["Adelie", "Chinstrap", "Gentoo"]
        buckets = {sp: [] for sp in order}
        for row_mob, (sp, _) in zip(table, rows_spec):
            buckets[sp].append(row_mob)

        targets, headers = VGroup(), VGroup()
        for i, sp in enumerate(order):
            x = -0.3 + 0 * i
            y = 1.7 - i * 1.55
            head = Text(sp, font_size=22, color=SPECIES_COLOR[sp])\
                .move_to([x - 1.9, y + 0.42, 0])
            headers.add(head)
            for j, row_mob in enumerate(buckets[sp]):
                targets.add(row_mob)
                row_mob.generate_target()
                row_mob.target.scale(0.62).move_to([x, y - j * 0.33, 0])

        self.play(FadeIn(headers),
                  LaggedStart(*[MoveToTarget(r) for r in targets],
                              lag_ratio=0.05), run_time=1.8)
        self.wait(0.4)

        # --- APPLY ---------------------------------------------------------
        self.play(Transform(step, Text("apply  (mean)", font_size=26, color=NAVY)
                            .to_edge(DOWN, buff=0.45)))

        means = {"Adelie": 3706, "Chinstrap": 3733, "Gentoo": 5092}
        collapsed = VGroup()
        anims = []
        for i, sp in enumerate(order):
            y = 1.7 - i * 1.55
            val = Text(f"{means[sp]}", font_size=30, color=SPECIES_COLOR[sp])\
                .move_to([2.6, y, 0])
            collapsed.add(val)
            group = VGroup(*buckets[sp])
            anims.append(ReplacementTransform(group, val))
        self.play(LaggedStart(*anims, lag_ratio=0.2), run_time=1.6)
        self.wait(0.4)

        # --- COMBINE -------------------------------------------------------
        self.play(Transform(step, Text("combine", font_size=26, color=NAVY)
                            .to_edge(DOWN, buff=0.45)))

        # Two independently aligned columns — arranging each row on its own
        # would let "Chinstrap" push its number out of line with the others.
        names = VGroup(*[Text(sp, font_size=22, color=SPECIES_COLOR[sp])
                         for sp in order])\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        vals = VGroup(*[Text(str(means[sp]), font_size=22, color=NAVY)
                        for sp in order])\
            .arrange(DOWN, buff=0.3, aligned_edge=RIGHT)\
            .next_to(names, RIGHT, buff=0.7)
        for n, v in zip(names, vals):
            v.set_y(n.get_y())
        result_rows = VGroup(names, vals).move_to(DOWN * 0.3)

        self.play(FadeOut(headers),
                  ReplacementTransform(collapsed, result_rows), run_time=1.2)

        box = SurroundingRectangle(result_rows, color=TEAL, buff=0.32,
                                   stroke_width=3, corner_radius=0.1)
        self.play(Create(box))
        self.wait(1.8)


# =====================================================================
# Asset 13 — underfit / good fit / overfit.  MP4, ~15s.  TIER 1, BUILD FIRST.
# =====================================================================
class OverfitUnderfit(Scene):
    """Three panels, identical points, three curves drawing in.

    The labels deliberately arrive LAST. Students should pick the curve they
    trust before being told which one is 'right'.
    """

    def construct(self):
        from scipy.interpolate import CubicSpline

        # Near-even spacing with a little jitter. Random x positions can put
        # two points almost on top of each other, which makes any exact
        # interpolator explode rather than wiggle — wrong lesson, ugly frame.
        rng = np.random.default_rng(7)
        xs = np.linspace(0.07, 0.93, 11) + rng.normal(0, 0.012, 11)
        xs = np.sort(np.clip(xs, 0.05, 0.95))
        ys = np.clip(0.48 + 0.85 * (xs - 0.5) - 1.5 * (xs - 0.5) ** 2
                     + rng.normal(0, 0.062, xs.size), 0.08, 0.92)

        title = Text("Same data. Three models.", font_size=36).to_edge(UP, buff=0.4)
        self.play(Write(title))

        centers = [LEFT * 4.3, ORIGIN, RIGHT * 4.3]
        frames, mappers, dotgroups = [], [], []
        for c in centers:
            frame, to_pt = panel(width=3.9, height=2.9, center=c + DOWN * 0.35)
            dots = VGroup(*[Dot(to_pt(x, y), radius=0.055, color=NAVY)
                            for x, y in zip(xs, ys)])
            frames.append(frame)
            mappers.append(to_pt)
            dotgroups.append(dots)

        self.play(LaggedStart(*[Create(f) for f in frames], lag_ratio=0.15),
                  run_time=0.9)
        self.play(LaggedStart(*[FadeIn(d, lag_ratio=0.06) for d in dotgroups],
                              lag_ratio=0.15), run_time=1.1)
        self.wait(0.4)

        # Degree 1 barely bends. Degree 3 tracks the real shape. The third is
        # an exact interpolating spline — forced through every single point,
        # which is precisely what memorising the training set looks like.
        # (A degree-10 polynomial would also interpolate, but Runge
        # oscillation sends it off the panel and it reads as a glitch.)
        fine = np.linspace(xs.min(), xs.max(), 300)
        colors = [BLUE, TEAL, ORANGE]
        fits = [
            np.polyval(np.polyfit(xs, ys, 1), fine),
            np.polyval(np.polyfit(xs, ys, 3), fine),
            CubicSpline(xs, ys)(fine),
        ]
        curves = [curve_through(to_pt, fine, f, c, width=5)
                  for f, to_pt, c in zip(fits, mappers, colors)]

        self.play(*[Create(c) for c in curves], run_time=2.2)
        self.wait(1.0)

        question = Text("Which would you trust on a penguin you've never seen?",
                        font_size=27, color=NAVY).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(question, shift=UP * 0.15))
        self.wait(2.0)

        labels = VGroup(*[
            Text(t, font_size=26, color=col).next_to(f, UP, buff=0.22)
            for t, col, f in zip(("underfit", "good fit", "overfit"),
                                 colors, frames)
        ])
        self.play(FadeOut(question),
                  LaggedStart(*[FadeIn(l, shift=DOWN * 0.12) for l in labels],
                              lag_ratio=0.25), run_time=1.2)

        verdict = Text("The overfit curve is perfect on these points — "
                       "and useless on the next one.",
                       font_size=24, color=NAVY).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(verdict, shift=UP * 0.15))
        self.wait(1.8)


# =====================================================================
# Asset 14 — decision boundary forming.  MP4, ~12s.  Tier 2.
# =====================================================================
class DecisionBoundary(Scene):
    """The boundary shifts across training steps until it separates the classes."""

    def construct(self):
        from sklearn.linear_model import SGDClassifier

        X, y = load_penguins()
        title = Text("Learning where to draw the line", font_size=34)\
            .to_edge(UP, buff=0.4)
        self.play(Write(title))

        frame, to_pt = panel(width=8.6, height=5.0, center=DOWN * 0.35)
        dots = VGroup(*[Dot(to_pt(x, yv), radius=0.045,
                            color=SPECIES_COLOR[s])
                        for (x, yv), s in zip(X, y)])
        self.play(Create(frame), FadeIn(dots, lag_ratio=0.01), run_time=1.3)
        self.wait(0.5)

        clf = SGDClassifier(loss="log_loss", learning_rate="constant",
                            eta0=0.55, random_state=0)
        classes = np.unique(y)

        # One partial_fit pass == one visible step. Early steps are wrong on
        # purpose: the point is that the boundary MOVES, not that it arrives.
        img, caption, seen = None, None, 0
        for n_passes in (1, 1, 2, 3, 5, 8, 15, 30):
            for _ in range(n_passes):
                clf.partial_fit(X, y, classes=classes)
            seen += n_passes

            raster = boundary_image(clf, resolution=180)
            new_img = ImageMobject(raster).stretch_to_fit_width(8.6 - 0.24)\
                .stretch_to_fit_height(5.0 - 0.24).move_to(frame)
            new_cap = Text(f"training step {seen}", font_size=24,
                           color=NAVY).to_edge(DOWN, buff=0.4)

            if img is None:
                caption = new_cap
                self.add(new_img)
                self.bring_to_back(new_img)
                self.play(FadeIn(new_img), FadeIn(caption), run_time=0.5)
            else:
                self.play(FadeTransform(img, new_img),
                          Transform(caption, new_cap), run_time=0.75)
                self.bring_to_back(new_img)
            img = new_img

        self.wait(0.6)
        note = Text("fit() is this, repeated — until moving stops helping",
                    font_size=25, color=TEAL).to_edge(DOWN, buff=0.4)
        self.play(FadeOut(caption), FadeIn(note, shift=UP * 0.15))
        self.wait(2.2)


# =====================================================================
# Asset 16 — KNN mechanism.  MP4, ~12s.  Tier 1.
# =====================================================================
class KNNMechanism(Scene):
    """A new point lands, a circle expands until it captures K neighbours,
    and those K vote."""

    def construct(self):
        rng = np.random.default_rng(3)
        pts, labels = [], []
        for sp, cx, cy in (("Adelie", 0.30, 0.34),
                           ("Chinstrap", 0.70, 0.40),
                           ("Gentoo", 0.52, 0.76)):
            for _ in range(11):
                pts.append((rng.normal(cx, 0.105), rng.normal(cy, 0.095)))
                labels.append(sp)
        pts = np.array(pts)

        title = Text("K-Nearest Neighbors, K = 5", font_size=36)\
            .to_edge(UP, buff=0.4)
        self.play(Write(title))

        frame, to_pt = panel(width=7.4, height=4.8, center=DOWN * 0.3)
        dots = VGroup(*[Dot(to_pt(x, y), radius=0.06, color=SPECIES_COLOR[s])
                        for (x, y), s in zip(pts, labels)])
        self.play(Create(frame), FadeIn(dots, lag_ratio=0.03), run_time=1.2)
        self.wait(0.4)

        # --- the unknown penguin arrives ----------------------------------
        new = np.array([0.50, 0.50])
        star = Star(n=5, outer_radius=0.17, color=NAVY,
                    fill_opacity=1, fill_color=WHITE, stroke_width=4)\
            .move_to(to_pt(*new))
        q = Text("new penguin — which species?", font_size=25, color=NAVY)\
            .to_edge(DOWN, buff=0.4)
        self.play(FadeIn(star, scale=0.3), FadeIn(q), run_time=0.8)
        self.wait(0.8)

        # --- the circle grows until exactly 5 are inside -------------------
        d = np.linalg.norm(pts - new, axis=1)
        order = np.argsort(d)
        r5 = d[order[4]]

        # scene-space radius: the panel mapping is anisotropic, so measure it
        unit = np.linalg.norm(to_pt(new[0] + 0.1, new[1]) - to_pt(*new)) / 0.1
        circle = Circle(radius=0.01, color=ORANGE, stroke_width=4)\
            .move_to(to_pt(*new))
        self.add(circle)
        self.play(Transform(
            circle,
            Circle(radius=r5 * unit * 1.04, color=ORANGE, stroke_width=4)
            .move_to(to_pt(*new))), run_time=2.2)

        neigh = order[:5]
        rings = VGroup(*[
            Circle(radius=0.115, color=ORANGE, stroke_width=3.5)
            .move_to(dots[i].get_center())
            for i in neigh
        ])
        self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.12),
                  run_time=1.0)

        # --- they vote ------------------------------------------------------
        votes = {}
        for i in neigh:
            votes[labels[i]] = votes.get(labels[i], 0) + 1
        winner = max(votes, key=votes.get)

        tally = VGroup(*[
            Text(f"{sp}  {n}", font_size=25, color=SPECIES_COLOR[sp])
            for sp, n in sorted(votes.items(), key=lambda kv: -kv[1])
        ]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)\
          .next_to(frame, RIGHT, buff=0.35)

        self.play(FadeOut(q), LaggedStart(*[FadeIn(t, shift=LEFT * 0.2)
                                            for t in tally], lag_ratio=0.2),
                  run_time=1.1)

        verdict = Text(f"majority wins  →  {winner}", font_size=28,
                       color=SPECIES_COLOR[winner]).to_edge(DOWN, buff=0.4)
        self.play(star.animate.set_fill(SPECIES_COLOR[winner], opacity=1)
                  .set_stroke(SPECIES_COLOR[winner]),
                  FadeIn(verdict, shift=UP * 0.15), run_time=1.0)
        self.wait(2.0)


# =====================================================================
# Asset 17 — the effect of K.  MP4, ~10s.  Tier 2.
# =====================================================================
class EffectOfK(Scene):
    """The boundary morphs from jagged at K=1 to smooth at large K."""

    def construct(self):
        from sklearn.neighbors import KNeighborsClassifier

        X, y = load_penguins()
        title = Text("K controls how much the model smooths", font_size=34)\
            .to_edge(UP, buff=0.4)
        self.play(Write(title))

        frame, to_pt = panel(width=8.2, height=4.8, center=DOWN * 0.45)
        dots = VGroup(*[Dot(to_pt(a, b), radius=0.042, color=SPECIES_COLOR[s])
                        for (a, b), s in zip(X, y)])
        self.play(Create(frame), FadeIn(dots, lag_ratio=0.01), run_time=1.2)

        img, klabel = None, None
        for k in (1, 3, 7, 15, 35, 75):
            clf = KNeighborsClassifier(n_neighbors=k).fit(X, y)
            raster = boundary_image(clf, resolution=170)
            new_img = ImageMobject(raster)\
                .stretch_to_fit_width(8.2 - 0.24)\
                .stretch_to_fit_height(4.8 - 0.24).move_to(frame)
            new_lbl = Text(f"K = {k}", font_size=30, color=NAVY)\
                .to_edge(DOWN, buff=0.45)

            if img is None:
                self.add(new_img)
                self.bring_to_back(new_img)
                klabel = new_lbl
                self.play(FadeIn(new_img), FadeIn(klabel), run_time=0.6)
            else:
                self.play(FadeTransform(img, new_img),
                          Transform(klabel, new_lbl), run_time=0.9)
                self.bring_to_back(new_img)
            img = new_img
            self.wait(0.35)

        note = Text("K=1 trusts one neighbour. Large K ignores real structure.",
                    font_size=24, color=TEAL).next_to(frame, DOWN, buff=0.12)
        self.play(FadeOut(klabel), FadeIn(note, shift=UP * 0.12))
        self.wait(2.0)


def bar_chart(counts, origin, width, height, top, color, stroke=NAVY):
    """A simple histogram as a row of rectangles, scaled to `top`.

    Manim ships BarChart, but it brings axis furniture and its own colour
    defaults; drawing the bars directly keeps these clips inside the shared
    palette and makes a single bar easy to animate on its own.
    """
    n = len(counts)
    bw = width / n
    bars = VGroup()
    for i, c in enumerate(counts):
        h = max(height * c / top, 0.001)
        bar = Rectangle(
            width=bw * 0.86, height=h,
            stroke_width=1.2, stroke_color=stroke,
            fill_color=color, fill_opacity=1,
        )
        bar.move_to(origin + np.array([(i + 0.5) * bw - width / 2, h / 2, 0]))
        bars.add(bar)
    return bars


# =====================================================================
# Asset 20 — imputation.  MP4, ~15s.  Tier 1 (Hour 4, Titanic).
# =====================================================================
class Imputation(Scene):
    """Filling a gap is inventing data — and every invented value lands in
    exactly the same place.

    Uses the real Titanic ages so the distortion on screen is the distortion
    students will actually produce in the notebook.
    """

    def construct(self):
        import pandas as pd

        src = TITANIC if TITANIC.exists() else TITANIC_URL
        age = pd.read_csv(src)["Age"]
        observed = age.dropna().to_numpy()
        n_missing = int(age.isna().sum())
        median = float(age.median())

        edges = np.arange(0, 85, 5)
        h_obs, _ = np.histogram(observed, bins=edges)
        h_fill, _ = np.histogram(age.fillna(median).to_numpy(), bins=edges)
        top = float(h_fill.max())
        med_bin = int(np.digitize(median, edges) - 1)

        title = Text(f"Age is missing for {n_missing} of {len(age)} passengers",
                     font_size=32).to_edge(UP, buff=0.42)
        self.play(Write(title))

        W, H = 9.6, 3.6
        base = DOWN * 1.9
        axis = Line(base + LEFT * W / 2, base + RIGHT * W / 2,
                    color=NAVY, stroke_width=3)
        self.play(Create(axis), run_time=0.5)

        bars = bar_chart(h_obs, base, W, H, top, BLUE)
        xlab = Text("age (years)", font_size=22, color=NAVY)\
            .next_to(axis, DOWN, buff=0.28)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars],
                              lag_ratio=0.04), FadeIn(xlab), run_time=1.4)
        self.wait(0.4)

        # --- the three options ------------------------------------------
        opts = VGroup(
            Text("drop the 177 rows", font_size=24, color=GRAY),
            Text(f"fill with the mean  {age.mean():.1f}", font_size=24, color=GRAY),
            Text(f"fill with the median  {median:.0f}", font_size=24, color=NAVY),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT).to_edge(UP, buff=1.35)
        self.play(LaggedStart(*[FadeIn(o, shift=RIGHT * 0.15) for o in opts],
                              lag_ratio=0.18), run_time=1.2)
        self.wait(0.5)

        chosen = SurroundingRectangle(opts[2], color=TEAL, buff=0.14,
                                      stroke_width=3, corner_radius=0.08)
        self.play(Create(chosen), FadeOut(opts[0]), FadeOut(opts[1]),
                  run_time=0.7)
        # Left, not centre: centred it sat directly on top of the 106 -> 283
        # label that grows out of the spike.
        self.play(VGroup(opts[2], chosen).animate
                  .to_corner(UL, buff=0.55).shift(DOWN * 0.55),
                  run_time=0.5)

        # --- every filled value lands in ONE bin -------------------------
        marker = Line(base, base + UP * H, color=TEAL,
                      stroke_width=2.5).set_opacity(0.55)
        marker.move_to(bars[med_bin].get_center() + UP * (H / 2 -
                       bars[med_bin].height / 2))
        marker.align_to(base, DOWN)

        tall = bar_chart(h_fill, base, W, H, top, BLUE)
        grown = tall[med_bin].copy().set_fill(ORANGE)

        drops = VGroup(*[
            Dot(bars[med_bin].get_top() + UP * (0.35 + 0.16 * (i % 12))
                + RIGHT * (0.42 * ((i // 12) - 1.5)),
                radius=0.045, color=ORANGE)
            for i in range(48)
        ])
        self.play(FadeIn(drops, lag_ratio=0.02), run_time=0.8)
        self.play(
            drops.animate.move_to(bars[med_bin].get_center()).scale(0.1),
            Transform(bars[med_bin], grown),
            run_time=1.5,
        )
        self.remove(drops)

        lbl = Text(f"{h_obs[med_bin]}  →  {h_fill[med_bin]}", font_size=26,
                   color=ORANGE).next_to(grown, UP, buff=0.18)
        self.play(FadeIn(lbl, shift=UP * 0.12), run_time=0.6)
        self.wait(0.8)

        verdict = Text("every filled value is the same guess — "
                       "the shape is now a lie",
                       font_size=26, color=NAVY).to_edge(DOWN, buff=0.28)
        self.play(FadeOut(xlab), FadeIn(verdict, shift=UP * 0.12))
        self.wait(1.8)


# =====================================================================
# Asset 21 — the distance behind KNN.  MP4, ~15s.  Tier 1 (Hour 4).
# =====================================================================
class KNNDistance(Scene):
    """What "nearest" actually computes — and why raw units wreck it.

    This is the missing half of the scaling lesson: students are told mass
    dominates, but the squared terms show exactly how badly.
    """

    def construct(self):
        title = Text("What \"nearest\" actually means", font_size=34)\
            .to_edge(UP, buff=0.4)
        self.play(Write(title))

        frame, to_pt = panel(width=5.6, height=3.9, center=LEFT * 3.6 + DOWN * 0.5)
        self.play(Create(frame), run_time=0.5)

        a, b = np.array([0.22, 0.26]), np.array([0.74, 0.72])
        pa = Dot(to_pt(*a), radius=0.09, color=BLUE)
        pb = Star(n=5, outer_radius=0.15, color=NAVY, fill_opacity=1,
                  fill_color=WHITE, stroke_width=3.5).move_to(to_pt(*b))
        la = Text("known", font_size=19, color=BLUE).next_to(pa, DOWN, buff=0.14)
        lb = Text("new", font_size=19, color=NAVY).next_to(pb, UP, buff=0.14)
        self.play(FadeIn(pa), FadeIn(pb), FadeIn(la), FadeIn(lb), run_time=0.7)

        corner = to_pt(b[0], a[1])
        dx = Line(to_pt(*a), corner, color=ORANGE, stroke_width=4)
        dy = Line(corner, to_pt(*b), color=TEAL, stroke_width=4)
        hyp = DashedLine(to_pt(*a), to_pt(*b), color=NAVY, stroke_width=3.5)
        dxl = Text("Δ bill", font_size=20, color=ORANGE).next_to(dx, DOWN, buff=0.12)
        dyl = Text("Δ mass", font_size=20, color=TEAL).next_to(dy, RIGHT, buff=0.12)

        self.play(Create(dx), FadeIn(dxl), run_time=0.6)
        self.play(Create(dy), FadeIn(dyl), run_time=0.6)
        self.play(Create(hyp), run_time=0.7)

        eq = MathTex(r"d=\sqrt{(\Delta\text{bill})^2+(\Delta\text{mass})^2}",
                     font_size=40).move_to(RIGHT * 3.3 + UP * 1.6)
        self.play(Write(eq), run_time=1.1)
        self.wait(0.6)

        # --- the raw-units disaster --------------------------------------
        raw = MathTex(r"d=\sqrt{5^2+500^2}=\sqrt{25+250000}",
                      font_size=34, color=NAVY).move_to(RIGHT * 3.3 + UP * 0.35)
        self.play(FadeIn(raw, shift=UP * 0.12), run_time=0.8)

        share = VGroup(
            Text("mass contributes  250 000", font_size=23, color=TEAL),
            Text("bill contributes           25", font_size=23, color=ORANGE),
            Text("bill is 0.01% of the answer", font_size=23, color=NAVY),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)\
         .move_to(RIGHT * 3.3 + DOWN * 1.15)
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.12) for t in share],
                              lag_ratio=0.25), run_time=1.5)
        self.wait(1.3)

        # --- scaled -------------------------------------------------------
        fixed = MathTex(r"\text{scaled:}\quad d=\sqrt{1.1^2+0.9^2}",
                        font_size=34, color=TEAL)\
            .move_to(RIGHT * 3.3 + DOWN * 1.15)
        self.play(FadeOut(share), FadeIn(fixed, shift=UP * 0.12), run_time=0.9)
        note = Text("now both features actually get a vote",
                    font_size=25, color=TEAL).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(note, shift=UP * 0.12))
        self.wait(1.8)


# =====================================================================
# Asset 22 — how logistic regression turns a score into a probability.
# MP4, ~14s.  Tier 2 (Hour 3).
# =====================================================================
class LogisticCurve(Scene):
    """The equation behind the model they trained first.

    Kept to two moves: a weighted sum, then a squash into 0-1. No calculus,
    no log-odds — just why the output can be read as a probability.

    Layout note: both equations live ABOVE the plot. Putting the sigmoid
    beside it collided with the annotated point, because the curve is high
    on exactly the side the equation wanted.
    """

    def construct(self):
        title = Text("What the model actually computes", font_size=34)\
            .to_edge(UP, buff=0.35)
        self.play(Write(title))

        step1 = MathTex(r"z = w_1x_1 + w_2x_2 + w_3x_3 + b",
                        font_size=42).move_to(UP * 1.9)
        self.play(Write(step1), run_time=1.0)

        cap1 = Text("a weighted sum of the features — any number at all",
                    font_size=24, color=NAVY).next_to(step1, DOWN, buff=0.3)
        self.play(FadeIn(cap1, shift=UP * 0.1), run_time=0.6)
        self.wait(0.6)

        note = Text("fit() is what chooses  w  and  b",
                    font_size=24, color=TEAL).next_to(cap1, DOWN, buff=0.24)
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(0.9)

        self.play(FadeOut(cap1), FadeOut(note),
                  step1.animate.scale(0.74).move_to(UP * 2.55))

        step2 = MathTex(r"p=\frac{1}{1+e^{-z}}", font_size=40, color=BLUE)\
            .move_to(UP * 1.35)
        arrow = MathTex(r"\downarrow", font_size=30, color=NAVY)\
            .move_to(UP * 2.15)
        self.play(FadeIn(arrow), Write(step2), run_time=1.0)

        # --- the squash ---------------------------------------------------
        ax = Axes(
            x_range=[-6, 6, 2], y_range=[0, 1.05, 0.5],
            x_length=8.0, y_length=2.9,
            axis_config={"color": NAVY, "stroke_width": 2.5, "font_size": 20},
            tips=False,
        ).shift(DOWN * 1.45)
        ax.get_y_axis().add_numbers([1.0], font_size=20, color=NAVY)
        xlab = MathTex("z", font_size=30).next_to(ax.x_axis, RIGHT, buff=0.16)
        ylab = Text("probability", font_size=19, color=NAVY)\
            .next_to(ax.c2p(0, 1.05), UP, buff=0.08).shift(LEFT * 0.55)
        self.play(Create(ax), FadeIn(xlab), FadeIn(ylab), run_time=1.0)

        curve = ax.plot(lambda z: 1 / (1 + np.exp(-z)), color=BLUE,
                        stroke_width=5)
        self.play(Create(curve), run_time=1.2)

        half = DashedLine(ax.c2p(-6, 0.5), ax.c2p(6, 0.5),
                          color=ORANGE, stroke_width=2.5)
        # Labelled at the end of the line, not on the y-axis: an axis tick at
        # 0.5 sits exactly where the line crosses it and reads as struck out.
        hl = Text("0.5", font_size=20, color=ORANGE)\
            .next_to(ax.c2p(-6, 0.5), LEFT, buff=0.14)
        self.play(Create(half), FadeIn(hl), run_time=0.7)

        # Annotated point sits BELOW the curve on the right, where the gap
        # between the 0.5 line and the curve is empty.
        z0 = 2.2
        p0 = 1 / (1 + np.exp(-z0))
        dot = Dot(ax.c2p(z0, p0), radius=0.09, color=TEAL)
        drop = DashedLine(ax.c2p(z0, 0), dot.get_center(), color=TEAL,
                          stroke_width=2)
        # Right of z=0 and below 0.5 the plot is empty — the curve is above
        # the line there. Anywhere else this label crossed the curve.
        rd = Text(f"z = {z0}  →  p = {p0:.2f}  →  Gentoo",
                  font_size=23, color=TEAL).move_to(ax.c2p(3.0, 0.22))
        self.play(Create(drop), FadeIn(dot), run_time=0.6)
        self.play(FadeIn(rd, shift=UP * 0.1), run_time=0.6)

        verdict = Text("above the orange line → one class, below → the other",
                       font_size=24, color=NAVY).to_edge(DOWN, buff=0.22)
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait(1.4)
