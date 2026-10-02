"""
Manim Community Edition scenes for the two-hour Python & ML workshop.

Every clip is a SELF-SUFFICIENT micro-lesson: a student who sees only the
clip, with no speaker, should understand the concept. They all share one
grammar, implemented once in `Lesson` below:

    1. a question as the title            ("What does a for loop do?")
    2. the idea built step by step, one plain-English caption per step,
       held long enough to read (0.3 s per word + 1 s)
    3. a TAKEAWAY box as the final frame — the deck's clip player stops on
       the last frame, so the last frame is the most informative one

Render everything with:

    python tools/build_assets.py --manim

or one scene at a time:

    python tools/build_assets.py --scene OverfitUnderfit

-qm is deliberate: exactly 1280x720 @30fps, the size the asset spec calls
for. Budget per clip: <= 30 s, <= 4 MB (tools/check_assets.py).

All numbers on screen come from the real data in data/ — the same numbers the
deck and the notebooks show (333 penguins, 266/67 split, 106 -> 283,
std 14.5 -> 13.0, 0.82 -> 0.99).
"""

import pathlib

import numpy as np
from manim import *

# ---------------------------------------------------------------------
# Shared visual system — identical hex values to the TikZ diagrams and
# the slide theme. Blue always means the same thing across all assets.
# ---------------------------------------------------------------------
NAVY = "#1B2A4A"
BLUE = "#2E5CA8"
ORANGE = "#E07A2C"
TEAL = "#2A9D8F"
GRAY = "#D9DCE1"
INK_SOFT = "#5A6680"          # secondary text
PAPER = "#F4F5F7"             # code / card background
TEAL_WASH = "#E3F3F1"         # takeaway background
ORANGE_WASH = "#FCEFE4"

SPECIES = ("Adelie", "Chinstrap", "Gentoo")
SPECIES_COLOR = {"Adelie": BLUE, "Chinstrap": ORANGE, "Gentoo": TEAL}

MONO = "DejaVu Sans Mono"
TITLE_SIZE = 40
CAPTION_SIZE = 31

config.background_color = WHITE
Text.set_default(color=NAVY, font="Inter")
MathTex.set_default(color=NAVY)

DATA = pathlib.Path(__file__).resolve().parent.parent.parent / "data" / "penguins.csv"
PENGUINS_URL = ("https://raw.githubusercontent.com/mwaskom/seaborn-data/"
                "master/penguins.csv")
TITANIC = DATA.parent / "titanic.csv"
TITANIC_URL = ("https://raw.githubusercontent.com/datasciencedojo/datasets/"
               "master/titanic.csv")


# ---------------------------------------------------------------------
# data
# ---------------------------------------------------------------------
def penguins_df():
    import pandas as pd
    src = DATA if DATA.exists() else PENGUINS_URL
    return pd.read_csv(src).dropna().reset_index(drop=True)


def load_penguins():
    """Bill length and flipper length, min-max scaled to [0, 1]."""
    df = penguins_df()
    X = df[["bill_length_mm", "flipper_length_mm"]].to_numpy(float)
    X = (X - X.min(0)) / (X.max(0) - X.min(0))
    return X, df["species"].to_numpy()


# ---------------------------------------------------------------------
# drawing helpers
# ---------------------------------------------------------------------
def fit_width(mob, max_width):
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


def marker(species, point, r=0.055):
    """One penguin. Shape AND colour encode species — never colour alone."""
    c = SPECIES_COLOR[species]
    if species == "Adelie":
        m = Dot(radius=r, color=c)
    elif species == "Chinstrap":
        m = Square(side_length=r * 1.75, color=c, fill_opacity=1, stroke_width=0)
    else:
        m = Triangle(color=c, fill_opacity=1, stroke_width=0).scale(r * 1.3)
    return m.move_to(point)


def legend(font_size=24, r=0.08):
    return VGroup(*[
        VGroup(marker(sp, ORIGIN, r),
               Text(sp, font_size=font_size, color=SPECIES_COLOR[sp]))
        .arrange(RIGHT, buff=0.16)
        for sp in SPECIES
    ]).arrange(DOWN, buff=0.18, aligned_edge=LEFT)


def panel(width=3.6, height=2.6, center=ORIGIN):
    """A framed plotting box plus a data->scene mapping for it."""
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


def axis_labels(frame, x_text, y_text, font_size=22):
    xl = Text(x_text, font_size=font_size, color=INK_SOFT)\
        .next_to(frame, DOWN, buff=0.12)
    yl = Text(y_text, font_size=font_size, color=INK_SOFT)\
        .rotate(PI / 2).next_to(frame, LEFT, buff=0.12)
    return VGroup(xl, yl)


def curve_through(to_pt, xs, ys, color, width=5):
    return VMobject(stroke_color=color, stroke_width=width).set_points_smoothly(
        [to_pt(x, y) for x, y in zip(xs, ys)]
    )


def boundary_image(predict, resolution=200):
    """Decision regions of `predict` as a soft RGB image (pale species wash)."""
    g = np.linspace(0, 1, resolution)
    xx, yy = np.meshgrid(g, g)
    labels = np.asarray(predict(np.c_[xx.ravel(), yy.ravel()]))\
        .reshape(resolution, resolution)
    rgb = np.full((resolution, resolution, 3), 255, dtype=np.uint8)
    for name, hexcode in SPECIES_COLOR.items():
        c = np.array([int(hexcode[i:i + 2], 16) for i in (1, 3, 5)])
        rgb[labels == name] = (255 - (255 - c) * 0.26).astype(np.uint8)
    return np.flipud(rgb)


def region_mobject(predict, frame, resolution=200):
    img = ImageMobject(boundary_image(predict, resolution))
    img.stretch_to_fit_width(frame.width - 0.24)\
       .stretch_to_fit_height(frame.height - 0.24).move_to(frame)
    return img


def cell_row(values, stroke, size=1.1, font_size=30, fill=WHITE, mono=False):
    cells = VGroup()
    for v in values:
        sq = RoundedRectangle(width=size, height=size * 0.82, corner_radius=0.08,
                              stroke_width=3, stroke_color=stroke,
                              fill_color=fill, fill_opacity=1)
        kw = {"font": MONO} if mono else {}
        t = Text(str(v), font_size=font_size, **kw).move_to(sq)
        cells.add(VGroup(sq, t))
    return cells.arrange(RIGHT, buff=0.16)


def code_card(lines, font_size=28, t2c=None):
    t2c = t2c or {}
    # Text() drops leading spaces, so indentation is applied by measurement.
    char_w = Text("0000000000", font=MONO, font_size=font_size).width / 10
    indents = [len(l) - len(l.lstrip(" ")) for l in lines]
    text = VGroup(*[Text(l.strip(" "), font=MONO, font_size=font_size, t2c=t2c)
                    for l in lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    for line, n in zip(text, indents):
        line.shift(RIGHT * n * char_w)
    box = SurroundingRectangle(text, buff=0.24, corner_radius=0.1,
                               stroke_color=GRAY, stroke_width=2,
                               fill_color=PAPER, fill_opacity=1)
    return VGroup(box, text)


def bar_chart(counts, origin, width, height, top, color, stroke=NAVY):
    n = len(counts)
    bw = width / n
    bars = VGroup()
    for i, c in enumerate(counts):
        h = max(height * c / top, 0.001)
        bar = Rectangle(width=bw * 0.86, height=h, stroke_width=1.2,
                        stroke_color=stroke, fill_color=color, fill_opacity=1)
        bar.move_to(origin + np.array([(i + 0.5) * bw - width / 2, h / 2, 0]))
        bars.add(bar)
    return bars


# ---------------------------------------------------------------------
# the lesson grammar
# ---------------------------------------------------------------------
def read_time(text):
    return 0.3 * len(text.split()) + 1.0


class Lesson(Scene):
    """Title question -> captioned steps -> takeaway frame."""

    def setup(self):
        self.caption = None

    def heading(self, text):
        t = Text(text, font_size=TITLE_SIZE, weight=BOLD).to_edge(UP, buff=0.34)
        fit_width(t, 12.8)
        rule = Line(LEFT, RIGHT, color=TEAL, stroke_width=4)\
            .set_length(1.2).next_to(t, DOWN, buff=0.14).align_to(t, LEFT)
        self.play(FadeIn(t, shift=DOWN * 0.15), Create(rule), run_time=0.6)
        self.title_group = VGroup(t, rule)
        return t

    def _caption(self, text, color):
        t = Text(text, font_size=CAPTION_SIZE, color=color)
        fit_width(t, 12.4)
        bg = RoundedRectangle(corner_radius=0.14, width=t.width + 0.7,
                              height=t.height + 0.36, stroke_width=0,
                              fill_color=WHITE, fill_opacity=0.94)
        return VGroup(bg, t.move_to(bg)).to_edge(DOWN, buff=0.26)

    def say(self, text, *anims, run_time=None, color=NAVY, extra=0.0):
        """Show a caption, optionally animating alongside it, then hold it
        until it has been on screen long enough to read."""
        new = self._caption(text, color)
        cap_anims = [FadeIn(new, shift=UP * 0.12)]
        if self.caption is not None:
            # Hand-off, not a crossfade: the old caption is gone in the first
            # quarter, the new one arrives over the rest. Two sentences
            # overlapping in the same spot read as neither. Same run time.
            cap_anims = [
                FadeOut(self.caption, shift=UP * 0.12,
                        rate_func=lambda t: smooth(min(1.0, t * 4))),
                FadeIn(new, shift=UP * 0.12,
                       rate_func=lambda t: smooth(max(0.0, (t - 0.25) / 0.75))),
            ]
        rt = run_time if run_time is not None else (1.0 if anims else 0.45)
        self.play(*cap_anims, *anims, run_time=rt)
        self.caption = new
        rest = read_time(text) - rt + extra
        if rest > 0.05:
            self.wait(rest)

    def takeaway(self, text, hold=3.2):
        label = Text("TAKEAWAY", font_size=19, color=TEAL, weight=BOLD)
        body = Text(text, font_size=31, color=NAVY, weight=BOLD)
        fit_width(body, 12.2)
        inner = VGroup(label, body).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        box = SurroundingRectangle(inner, buff=0.2, corner_radius=0.14,
                                   stroke_color=TEAL, stroke_width=3,
                                   fill_color=TEAL_WASH, fill_opacity=1)
        g = VGroup(box, inner).to_edge(DOWN, buff=0.2)
        anims = [FadeIn(g, shift=UP * 0.15)]
        if self.caption is not None:
            anims.append(FadeOut(self.caption))
        self.play(*anims, run_time=0.7)
        self.caption = None
        self.wait(hold)


# =====================================================================
# Asset 3 — what a for loop does.
# =====================================================================
class ForLoopWalkthrough(Lesson):
    def construct(self):
        self.heading("What does a for loop do?")
        values = [3750, 3800, 3250, 3450]

        code = code_card(["for m in masses:", "    total = total + m"],
                         font_size=30, t2c={"for": BLUE, " in ": BLUE})
        code.move_to(UP * 1.75)
        body_line = code[1][1]
        hl = SurroundingRectangle(body_line, buff=0.08, corner_radius=0.06,
                                  stroke_width=0, fill_color=ORANGE,
                                  fill_opacity=0.18)

        boxes = cell_row(values, NAVY, size=1.45, font_size=32).move_to(DOWN * 0.15)
        name = Text("masses", font=MONO, font_size=26, color=INK_SOFT)\
            .next_to(boxes, LEFT, buff=0.35)
        idx = VGroup(*[Text(f"item {i + 1}", font_size=20, color=INK_SOFT)
                       .next_to(b, DOWN, buff=0.12) for i, b in enumerate(boxes)])

        m_val = Text("m = —", font=MONO, font_size=32, color=ORANGE)
        total_val = Text("total = 0", font=MONO, font_size=32, color=TEAL)
        state = VGroup(m_val, total_val).arrange(RIGHT, buff=1.4)\
            .move_to(DOWN * 1.75)

        self.say("A loop visits each item of a list, one at a time.",
                 FadeIn(code), FadeIn(boxes, lag_ratio=0.15), FadeIn(name),
                 FadeIn(idx), FadeIn(state), run_time=1.2)

        pointer = Triangle(color=ORANGE, fill_opacity=1, stroke_width=0)\
            .scale(0.16).rotate(PI).next_to(boxes[0], UP, buff=0.14)

        total = 0
        captions = {
            0: "Pass 1: m takes the first value, 3750.",
            1: "Pass 2: same line of code, next value.",
            3: "The indented line runs once per item.",
        }
        for i, v in enumerate(values):
            total += v
            new_m = Text(f"m = {v}", font=MONO, font_size=32, color=ORANGE)\
                .move_to(m_val)
            new_t = Text(f"total = {total}", font=MONO, font_size=32,
                         color=TEAL).move_to(total_val)
            move = (FadeIn(pointer, shift=DOWN * 0.1) if i == 0 else
                    pointer.animate.next_to(boxes[i], UP, buff=0.14))
            step = [move,
                    boxes[i][0].animate.set_fill(ORANGE, opacity=0.2),
                    Transform(m_val, new_m)]
            if i > 0:
                step.append(boxes[i - 1][0].animate.set_fill(WHITE, opacity=1))
            if i in captions:
                self.say(captions[i], *step, run_time=0.6)
            else:
                self.play(*step, run_time=0.5)
            self.play(FadeIn(hl), run_time=0.25)
            self.play(Transform(total_val, new_t), run_time=0.35)
            self.play(Indicate(total_val, color=TEAL, scale_factor=1.12),
                      run_time=0.35)
            self.play(FadeOut(hl), run_time=0.2)

        self.play(FadeOut(pointer),
                  boxes[-1][0].animate.set_fill(WHITE, opacity=1), run_time=0.4)
        self.say("4 items, so the body ran 4 times: total = 14250.",
                 Circumscribe(total_val, color=TEAL), run_time=1.0)
        self.takeaway("A loop repeats the same steps for every item in a list.")


# =====================================================================
# Asset 5 — broadcasting / vectorised operations.
# =====================================================================
class Broadcasting(Lesson):
    def construct(self):
        self.heading("How does NumPy do maths on a whole array?")
        a = [3750, 3800, 3250, 3450]

        arr = cell_row(a, NAVY, size=1.5, font_size=30).move_to(UP * 1.55)
        la = Text("a", font=MONO, font_size=32, color=NAVY)\
            .next_to(arr, LEFT, buff=0.45)
        code = Text("a * 2", font=MONO, font_size=34, color=BLUE)\
            .next_to(arr, RIGHT, buff=0.55)
        self.say("a * 2 — one line of code, no loop.",
                 FadeIn(arr, lag_ratio=0.1), FadeIn(la), FadeIn(code))

        scalar = cell_row([2], ORANGE, size=1.5, font_size=30)\
            .next_to(arr[0], DOWN, buff=0.35)
        twos = cell_row([2, 2, 2, 2], ORANGE, size=1.5, font_size=30,
                        fill=ORANGE_WASH).next_to(arr, DOWN, buff=0.35)
        times = Text("×", font_size=38, color=NAVY).next_to(twos, LEFT, buff=0.5)
        self.play(FadeIn(scalar, scale=0.6), run_time=0.5)
        self.say("NumPy stretches the 2 to match the array's shape.",
                 *[TransformFromCopy(scalar[0], t) for t in twos],
                 FadeOut(scalar), FadeIn(times), run_time=1.2)

        line = Line(LEFT, RIGHT, color=NAVY, stroke_width=3)\
            .set_width(arr.width + 1.0).next_to(twos, DOWN, buff=0.22)\
            .align_to(times, LEFT)
        out = cell_row([v * 2 for v in a], TEAL, size=1.5, font_size=30,
                       fill=TEAL_WASH).next_to(twos, DOWN, buff=0.5)
        pairs = [TransformFromCopy(VGroup(arr[i], twos[i]), out[i])
                 for i in range(4)]
        self.say("Then every pair is multiplied — all at the same time.",
                 Create(line), *pairs, run_time=1.2)
        self.wait(0.3)

        # --- a comparison is vectorised too: the bridge to masking ---------
        code2 = Text("a > 3700", font=MONO, font_size=34, color=BLUE)\
            .move_to(code).align_to(code, LEFT)
        thr = cell_row([3700] * 4, ORANGE, size=1.5, font_size=28,
                       fill=ORANGE_WASH).move_to(twos)
        gt = Text(">", font_size=38, color=NAVY).move_to(times)
        flags = [v > 3700 for v in a]
        out2 = VGroup()
        for f, tgt in zip(flags, out):
            box = RoundedRectangle(width=1.5, height=1.23, corner_radius=0.08,
                                   stroke_width=3,
                                   stroke_color=TEAL if f else GRAY,
                                   fill_color=TEAL_WASH if f else WHITE,
                                   fill_opacity=1).move_to(tgt)
            t = Text(str(f), font=MONO, font_size=26,
                     color=TEAL if f else INK_SOFT).move_to(box)
            out2.add(VGroup(box, t))
        self.say("Comparisons work the same way: one True/False each.",
                 Transform(code, code2), Transform(twos, thr),
                 Transform(times, gt), ReplacementTransform(out, out2),
                 run_time=1.2)
        self.takeaway("Vectorised: one operation hits every element — "
                      "no loop, 50–250× faster.")


# =====================================================================
# Asset 8 — split / apply / combine.
# =====================================================================
class SplitApplyCombine(Lesson):
    def construct(self):
        df = penguins_df()
        means = df.groupby("species")["body_mass_g"].mean().round().astype(int)
        # 8 real rows, species interleaved the way a raw table is
        picks = []
        for sp, n in (("Adelie", 3), ("Chinstrap", 2), ("Gentoo", 3)):
            picks += list(df[df.species == sp].head(n).itertuples())
        order_idx = [0, 5, 3, 1, 6, 4, 2, 7]
        rows_spec = [(picks[i].species, int(picks[i].body_mass_g))
                     for i in order_idx]

        self.heading("What does groupby do?")
        code = Text("df.groupby('species')['body_mass_g'].mean()", font=MONO,
                    font_size=24, color=BLUE)\
            .next_to(self.title_group, DOWN, buff=0.22)\
            .align_to(self.title_group, LEFT)
        self.play(FadeIn(code), run_time=0.4)

        def make_row(sp, mass):
            box = RoundedRectangle(width=2.9, height=0.42, corner_radius=0.07,
                                   stroke_width=2.5,
                                   stroke_color=SPECIES_COLOR[sp],
                                   fill_color=WHITE, fill_opacity=1)
            m = marker(sp, ORIGIN, 0.07)
            label = Text(sp, font_size=20, color=SPECIES_COLOR[sp])
            val = Text(f"{mass} g", font_size=20, color=NAVY)
            content = VGroup(m, label).arrange(RIGHT, buff=0.12)
            content.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.15)
            val.move_to(box).align_to(box, RIGHT).shift(LEFT * 0.15)
            return VGroup(box, content, val)

        table = VGroup(*[make_row(s, m) for s, m in rows_spec])\
            .arrange(DOWN, buff=0.08).move_to(LEFT * 4.9 + DOWN * 0.45)
        more = Text(f"… {len(df) - len(rows_spec)} more rows", font_size=20,
                    color=INK_SOFT).next_to(table, DOWN, buff=0.12)
        self.say("The raw table: one row per penguin, species mixed.",
                 LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in table],
                             lag_ratio=0.06), FadeIn(more), run_time=1.2)

        # --- SPLIT ---------------------------------------------------------
        buckets = {sp: [] for sp in SPECIES}
        for row_mob, (sp, _) in zip(table, rows_spec):
            buckets[sp].append(row_mob)
        frames, targets = VGroup(), []
        ys = {"Adelie": 1.3, "Chinstrap": -0.05, "Gentoo": -1.15}
        for sp in SPECIES:
            y = ys[sp]
            n = len(buckets[sp])
            fr = RoundedRectangle(width=2.35, height=0.3 * n + 0.34,
                                  corner_radius=0.1, stroke_width=2.5,
                                  stroke_color=SPECIES_COLOR[sp],
                                  fill_color=SPECIES_COLOR[sp],
                                  fill_opacity=0.07)\
                .move_to([-0.9, y - 0.15 * (n - 1), 0])
            frames.add(fr)
            for j, r in enumerate(buckets[sp]):
                r.generate_target()
                r.target.scale(0.7).move_to([-0.9, y - j * 0.3, 0])
                targets.append(r)
        stepw = Text("1 · SPLIT", font_size=24, color=TEAL, weight=BOLD)\
            .move_to([-0.9, 2.05, 0])
        self.say("Split: rows go into one group per species.",
                 FadeIn(stepw), FadeIn(frames),
                 LaggedStart(*[MoveToTarget(r) for r in targets], lag_ratio=0.05),
                 FadeOut(more), run_time=1.6)

        # --- APPLY ---------------------------------------------------------
        vals = VGroup()
        anims = []
        for sp, fr in zip(SPECIES, frames):
            v = Text(f"{means[sp]} g", font_size=30, color=SPECIES_COLOR[sp],
                     weight=BOLD).move_to([1.85, fr.get_y(), 0])
            vals.add(v)
            anims.append(TransformFromCopy(VGroup(*buckets[sp]), v))
        stepa = Text("2 · APPLY  mean", font_size=24, color=TEAL, weight=BOLD)\
            .move_to([1.85, 2.05, 0])
        arrows = VGroup(*[Arrow(fr.get_right(), v.get_left(), buff=0.15,
                                color=GRAY, stroke_width=3)
                          for fr, v in zip(frames, vals)])
        note = Text("each mean uses all of that\nspecies' rows, not just these",
                    font_size=17, color=INK_SOFT, line_spacing=0.9)\
            .next_to(vals, DOWN, buff=0.25)
        self.say("Apply: each group shrinks to one number, its mean.",
                 FadeIn(stepa), *[GrowArrow(a_) for a_ in arrows], *anims,
                 FadeIn(note), run_time=1.5)

        # --- COMBINE -------------------------------------------------------
        names = VGroup(*[VGroup(marker(sp, ORIGIN, 0.07),
                                Text(sp, font_size=24, color=SPECIES_COLOR[sp]))
                         .arrange(RIGHT, buff=0.12) for sp in SPECIES])\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        nums = VGroup(*[Text(str(means[sp]), font_size=24, color=NAVY)
                        for sp in SPECIES])\
            .arrange(DOWN, buff=0.3, aligned_edge=RIGHT)\
            .next_to(names, RIGHT, buff=0.6)
        for n_, nm in zip(nums, names):
            n_.set_y(nm.get_y())
        result = VGroup(names, nums)
        rbox = SurroundingRectangle(result, color=TEAL, buff=0.28,
                                    stroke_width=3, corner_radius=0.1)
        VGroup(rbox, result).move_to([4.75, -0.25, 0])
        stepc = Text("3 · COMBINE", font_size=24, color=TEAL, weight=BOLD)\
            .next_to(rbox, UP, buff=0.3)
        self.say("Combine: the answers form a new, small table.",
                 FadeIn(stepc), TransformFromCopy(vals, nums), FadeIn(names),
                 Create(rbox), run_time=1.3)
        self.takeaway("groupby = split, apply, combine — one answer per group.")


# =====================================================================
# Asset 12b — why we split into train and test.
# =====================================================================
def padlock(color=ORANGE):
    body = RoundedRectangle(width=0.42, height=0.34, corner_radius=0.06,
                            fill_color=color, fill_opacity=1, stroke_width=0)
    shackle = Arc(radius=0.14, start_angle=0, angle=PI, color=color,
                  stroke_width=6).next_to(body, UP, buff=-0.02)
    return VGroup(shackle, body)


class TrainTestSplit(Lesson):
    def construct(self):
        self.heading("Why hide some data from the model?")

        blocks = VGroup(*[
            RoundedRectangle(width=0.5, height=0.5, corner_radius=0.06,
                             stroke_width=2, stroke_color=NAVY,
                             fill_opacity=1, fill_color=GRAY)
            for _ in range(20)
        ]).arrange_in_grid(rows=2, cols=10, buff=0.08).move_to(UP * 1.1)
        cap_all = Text("333 penguins, species known", font_size=24,
                       color=INK_SOFT).next_to(blocks, UP, buff=0.18)
        self.say("We have 333 penguins whose species we know.",
                 FadeIn(blocks, lag_ratio=0.03), FadeIn(cap_all), run_time=1.0)

        rng = np.random.default_rng(4)
        perm = rng.permutation(20)
        pos = [b.get_center() for b in blocks]
        self.play(*[blocks[i].animate.move_to(pos[perm[i]]) for i in range(20)],
                  run_time=0.8)
        # after the shuffle, the right-most 2 columns become the test set
        order = sorted(range(20), key=lambda i: (perm[i] % 10, perm[i] // 10))
        train = VGroup(*[blocks[i] for i in order[:16]])
        test = VGroup(*[blocks[i] for i in order[16:]])

        self.say("Shuffle, then set 20% of them aside.",
                 train.animate.set_fill(BLUE).shift(LEFT * 1.1),
                 test.animate.set_fill(ORANGE).shift(RIGHT * 1.1),
                 FadeOut(cap_all), run_time=1.2)
        lt = Text("training set · 266", font_size=26, color=BLUE, weight=BOLD)\
            .next_to(train, UP, buff=0.2)
        ls = Text("test set · 67", font_size=26, color=ORANGE, weight=BOLD)\
            .next_to(test, UP, buff=0.2)
        lock = padlock().next_to(test, DOWN, buff=0.18)
        self.play(FadeIn(lt), FadeIn(ls), FadeIn(lock, scale=0.5), run_time=0.6)

        model = VGroup(
            RoundedRectangle(width=2.2, height=0.95, corner_radius=0.16,
                             stroke_color=NAVY, stroke_width=3,
                             fill_color=PAPER, fill_opacity=1),
            Text("model", font_size=30, weight=BOLD),
        ).move_to(DOWN * 1.35 + LEFT * 1.1)
        model[1].move_to(model[0])
        learn = Arrow(train.get_bottom(), model.get_top(), buff=0.12,
                      color=BLUE, stroke_width=5)
        learn_l = Text("learns", font_size=22, color=BLUE)\
            .next_to(learn, LEFT, buff=0.12)
        self.say("The model learns from the 266 training penguins only.",
                 FadeIn(model), GrowArrow(learn), FadeIn(learn_l), run_time=1.0)

        score = VGroup(
            Text("exam on 67 unseen penguins", font_size=24, color=ORANGE),
            Text("accuracy 0.97", font_size=32, color=NAVY, weight=BOLD),
        ).arrange(DOWN, buff=0.1).move_to(RIGHT * 3.9 + DOWN * 1.35)
        exam = Arrow(model.get_right(), score.get_left(), buff=0.2,
                     color=ORANGE, stroke_width=5)
        self.say("Then it sits an exam on the 67 it never saw.",
                 FadeOut(lock), GrowArrow(exam), FadeIn(score[0]), run_time=1.1)
        self.play(FadeIn(score[1], scale=1.2), run_time=0.5)
        self.say("You don't grade a student on the questions they studied.",
                 color=INK_SOFT)
        self.takeaway("Judge a model on data it has never seen — "
                      "not on what it memorised.")


# =====================================================================
# Asset 13 — underfit / good fit / overfit.
# =====================================================================
class OverfitUnderfit(Lesson):
    def construct(self):
        from scipy.interpolate import CubicSpline

        # Seed chosen (from a sweep) so the classic pattern reads clearly:
        # the good fit is best on new points, the interpolating model is
        # perfect on training and worst on new points. All numbers on screen
        # are computed below, not typed in.
        rng = np.random.default_rng(147)

        def truth(x):
            return 0.48 + 0.85 * (x - 0.5) - 1.5 * (x - 0.5) ** 2

        xs = np.sort(np.clip(np.linspace(0.07, 0.93, 11)
                             + rng.normal(0, 0.012, 11), 0.05, 0.95))
        ys = np.clip(truth(xs) + rng.normal(0, 0.062, xs.size), 0.08, 0.92)
        # new points: between the training points, same noisy process
        xt = (xs[:-1] + xs[1:]) / 2
        yt = np.clip(truth(xt) + rng.normal(0, 0.062, xt.size), 0.08, 0.92)

        models = [
            np.poly1d(np.polyfit(xs, ys, 1)),
            np.poly1d(np.polyfit(xs, ys, 3)),
            CubicSpline(xs, ys),
        ]

        def rmse(f, x, y):
            return float(np.sqrt(np.mean((f(x) - y) ** 2)))

        tr = [rmse(f, xs, ys) for f in models]
        te = [rmse(f, xt, yt) for f in models]

        self.heading("Underfit, good fit, overfit")

        centers = [LEFT * 4.35, ORIGIN, RIGHT * 4.35]
        frames, mappers, dots = [], [], []
        for c in centers:
            frame, to_pt = panel(width=3.95, height=2.45, center=c + UP * 0.55)
            frames.append(frame)
            mappers.append(to_pt)
            dots.append(VGroup(*[Dot(to_pt(x, y), radius=0.06, color=NAVY)
                                 for x, y in zip(xs, ys)]))
        self.say("Three models learn from the same 11 points.",
                 *[Create(f) for f in frames],
                 *[FadeIn(d, lag_ratio=0.05) for d in dots], run_time=1.1)

        fine = np.linspace(xs.min(), xs.max(), 300)
        colors = [BLUE, TEAL, ORANGE]
        names = ["underfit", "good fit", "overfit"]
        lines = [
            "Too simple: a straight line misses the bend.",
            "Just right: it follows the real trend.",
            "Too flexible: it hits every single point.",
        ]
        for k in range(3):
            curve = curve_through(mappers[k], fine, models[k](fine), colors[k])
            lbl = Text(names[k], font_size=28, color=colors[k], weight=BOLD)\
                .next_to(frames[k], UP, buff=0.12)
            self.say(lines[k], Create(curve), FadeIn(lbl), run_time=1.0)

        tests = VGroup()
        for to_pt in mappers:
            tests.add(VGroup(*[
                Square(side_length=0.15, color=ORANGE, stroke_width=3,
                       fill_opacity=0).move_to(to_pt(x, y))
                for x, y in zip(xt, yt)]))
        self.say("Now test all three on new points (□) they never saw.",
                 *[FadeIn(t, lag_ratio=0.05) for t in tests], run_time=1.0)

        worst = 2
        scores = VGroup()
        for k in range(3):
            g = VGroup(
                Text(f"error on training   {tr[k]:.2f}", font_size=23,
                     color=NAVY),
                Text(f"error on new points {te[k]:.2f}", font_size=23,
                     color=ORANGE if k == worst else NAVY,
                     weight=BOLD if k == worst else NORMAL),
            ).arrange(DOWN, buff=0.1, aligned_edge=LEFT)\
             .next_to(frames[k], DOWN, buff=0.2)
            scores.add(g)
        self.say("Overfit: perfect on training, worst on new points.",
                 LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in scores],
                             lag_ratio=0.2), run_time=1.3)
        self.play(Circumscribe(scores[worst], color=ORANGE), run_time=0.8)
        self.takeaway("Overfitting = memorising the examples "
                      "instead of learning the pattern.")


# =====================================================================
# Asset 14 — what fit() does: the boundary moving step by step.
# =====================================================================
class _Softmax:
    """A tiny multinomial logistic regression trained by plain gradient
    descent from a deliberately bad start, so every step is visible."""

    def __init__(self, X, y, seed=1):
        self.classes = np.array(SPECIES)
        self.Xb = np.c_[X, np.ones(len(X))]
        self.y = y
        self.Y = (y[:, None] == self.classes[None, :]).astype(float)
        rng = np.random.default_rng(seed)
        self.W = rng.normal(0, 2.0, (3, 3))

    def step(self, n, lr=2.5):
        for _ in range(n):
            z = self.Xb @ self.W
            z -= z.max(1, keepdims=True)
            p = np.exp(z)
            p /= p.sum(1, keepdims=True)
            self.W -= lr * self.Xb.T @ (p - self.Y) / len(self.Xb)

    def predict(self, X):
        return self.classes[np.argmax(np.c_[X, np.ones(len(X))] @ self.W, 1)]

    def accuracy(self):
        return float(np.mean(self.predict(self.Xb[:, :2]) == self.y))


class DecisionBoundary(Lesson):
    def construct(self):
        X, y = load_penguins()
        self.heading("What does .fit() actually do?")

        frame, to_pt = panel(width=7.7, height=4.3, center=LEFT * 1.9 + DOWN * 0.1)
        dots = VGroup(*[marker(s, to_pt(a, b), 0.045) for (a, b), s in zip(X, y)])
        labels = axis_labels(frame, "bill length →", "flipper length →")
        leg = legend(font_size=24).move_to(RIGHT * 4.6 + UP * 1.3)
        self.say("Each shape is a real penguin, placed by two measurements.",
                 Create(frame), FadeIn(dots, lag_ratio=0.004), FadeIn(labels),
                 FadeIn(leg), run_time=1.3)

        model = _Softmax(X, y, seed=4)     # starts at 23%: three wrong regions
        self.add_foreground_mobjects(dots)

        def readout(step, acc):
            return VGroup(
                Text(f"training step {step}", font_size=26, color=NAVY),
                Text(f"{acc:.0%} correct", font_size=40, color=TEAL, weight=BOLD),
            ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)\
             .move_to(RIGHT * 4.6 + DOWN * 0.9)

        img = region_mobject(model.predict, frame, 170)
        ro = readout(0, model.accuracy())
        self.add(img)
        self.bring_to_back(img)
        img.set_opacity(0)
        self.say("fit() starts from a random guess at the boundaries.",
                 img.animate.set_opacity(1), FadeIn(ro), run_time=0.9)

        seen = 0
        first = True
        for n in (1, 3, 8, 20, 50, 120, 300, 800):
            model.step(n - seen)
            seen = n
            new_img = region_mobject(model.predict, frame, 170)
            new_ro = readout(seen, model.accuracy())
            anims = [FadeTransform(img, new_img), Transform(ro, new_ro)]
            if first:
                self.say("Each step nudges the boundaries to fix mistakes.",
                         *anims, run_time=0.8)
                first = False
            else:
                self.play(*anims, run_time=0.55)
            self.bring_to_back(new_img)
            img = new_img
        self.say("It stops when moving them no longer helps.",
                 Circumscribe(ro, color=TEAL), run_time=1.0)
        self.takeaway("Training = nudging the boundaries, step by step, "
                      "to make fewer mistakes.")


# =====================================================================
# Asset 16 — how KNN decides.
# =====================================================================
def split_vote_point(X, y, K=5):
    """A spot INSIDE the data (dense surroundings) where the K nearest real
    penguins genuinely split 3-2, with a neighbourhood big enough to see."""
    best = None
    for gx in np.linspace(0.15, 0.85, 71):
        for gy in np.linspace(0.15, 0.85, 71):
            p = np.array([gx, gy])
            d = np.linalg.norm(X - p, axis=1)
            nn = np.argsort(d)[:K]
            _, cnt = np.unique(y[nn], return_counts=True)
            r = d[nn[-1]]
            if sorted(cnt.tolist()) == [2, 3] and 0.045 <= r <= 0.08:
                density = int((d < 0.12).sum())
                if best is None or density > best[0]:
                    best = (density, r, p, nn)
    return best[1:]


class KNNMechanism(Lesson):
    def construct(self):
        X, y = load_penguins()
        K = 5
        r5, new, nn = split_vote_point(X, y, K)
        votes = {sp: int(np.sum(y[nn] == sp)) for sp in SPECIES}
        winner = max(votes, key=votes.get)
        loser = [sp for sp in SPECIES if votes[sp] and sp != winner][0]

        self.heading("How does K-Nearest Neighbours decide?")
        frame, to_pt = panel(width=7.6, height=4.3, center=LEFT * 1.9 + DOWN * 0.1)
        dots = VGroup(*[marker(s, to_pt(a, b), 0.045) for (a, b), s in zip(X, y)])
        labels = axis_labels(frame, "bill length →", "flipper length →")
        leg = legend(font_size=24).move_to(RIGHT * 4.6 + UP * 1.3)
        self.play(Create(frame), FadeIn(dots, lag_ratio=0.004), FadeIn(labels),
                  FadeIn(leg), run_time=1.0)

        star = Star(n=5, outer_radius=0.19, color=NAVY, fill_opacity=1,
                    fill_color=WHITE, stroke_width=4).move_to(to_pt(*new))
        qmark = Text("?", font_size=24, weight=BOLD).move_to(star)
        self.say("A new penguin arrives. Which species is it?",
                 FadeIn(star, scale=0.3), FadeIn(qmark), run_time=0.8)

        # --- zoom: re-map the same data into a window around the newcomer.
        # The window keeps the panel's aspect ratio so one unit of distance is
        # the same length across and up: the neighbourhood is a true circle.
        aspect = (frame.width - 0.24) / (frame.height - 0.24)
        half = np.array([0.16 * aspect, 0.16])
        lo = new - half

        def to_zoom(a, b):
            u, v = (a - lo[0]) / (2 * half[0]), (b - lo[1]) / (2 * half[1])
            return to_pt(u, v)

        inside = np.all(np.abs(X - new) < half * 0.97, axis=1)
        zoom_anims = []
        for i, dmob in enumerate(dots):
            if inside[i]:
                zoom_anims.append(dmob.animate.move_to(to_zoom(*X[i])).scale(1.8))
            else:
                zoom_anims.append(FadeOut(dmob))
        zoom_tag = Text("zoomed in", font_size=22, color=INK_SOFT)\
            .next_to(frame, UP, buff=0.08).align_to(frame, RIGHT)
        star_z = star.copy().move_to(to_zoom(*new))
        self.say("Zoom in around the newcomer.",
                 *zoom_anims, star.animate.move_to(to_zoom(*new)),
                 qmark.animate.move_to(star_z), FadeIn(zoom_tag), run_time=1.3)

        d = np.linalg.norm(X - new, axis=1)
        near = [i for i in np.argsort(d) if inside[i]][:40]
        spokes = VGroup(*[Line(star_z.get_center(), dots[i].get_center(),
                               stroke_width=1.5, color=INK_SOFT)
                          .set_opacity(0.5) for i in near])
        self.bring_to_back(spokes)
        self.say("Measure its distance to every known penguin.",
                 LaggedStart(*[Create(s_) for s_ in spokes], lag_ratio=0.02),
                 run_time=1.2)

        ux = (to_zoom(new[0] + 0.1, new[1]) - to_zoom(*new))[0] / 0.1
        uy = (to_zoom(new[0], new[1] + 0.1) - to_zoom(*new))[1] / 0.1
        ring = Circle(radius=r5 * ux * 1.06, color=NAVY,
                      stroke_width=4).move_to(star_z)
        halos = VGroup(*[Circle(radius=0.17, color=NAVY, stroke_width=3)
                         .move_to(dots[i].get_center()) for i in nn])
        self.say(f"Keep only the K = {K} closest ones.",
                 FadeOut(spokes), GrowFromCenter(ring),
                 LaggedStart(*[Create(h) for h in halos], lag_ratio=0.1),
                 run_time=1.2)

        tally = VGroup()
        for sp in (winner, loser):
            row = VGroup(*[marker(sp, ORIGIN, 0.09) for _ in range(votes[sp])])\
                .arrange(RIGHT, buff=0.14)
            tally.add(VGroup(row, Text(f"{votes[sp]} × {sp}", font_size=26,
                                       color=SPECIES_COLOR[sp], weight=BOLD))
                      .arrange(RIGHT, buff=0.25))
        tally.arrange(DOWN, buff=0.28, aligned_edge=LEFT)\
            .move_to(RIGHT * 4.6 + DOWN * 0.7)
        vote_t = Text("the vote", font_size=22, color=INK_SOFT)\
            .next_to(tally, UP, buff=0.2).align_to(tally, LEFT)
        self.say(f"They vote: {votes[winner]} {winner}, {votes[loser]} {loser}.",
                 FadeIn(vote_t),
                 LaggedStart(*[FadeIn(t, shift=LEFT * 0.2) for t in tally],
                             lag_ratio=0.3), run_time=1.0)

        verdict = marker(winner, star_z.get_center(), 0.17)
        article = "an" if winner[0] in "AEIOU" else "a"
        self.say(f"The majority wins: it's {article} {winner}.",
                 FadeOut(qmark), Transform(star, verdict),
                 Circumscribe(tally[0], color=SPECIES_COLOR[winner]),
                 run_time=1.0)
        self.takeaway("KNN: find the K most similar examples "
                      "and let them vote.")


# =====================================================================
# Asset 17 — what K changes.
# =====================================================================
class EffectOfK(Lesson):
    def construct(self):
        from sklearn.model_selection import train_test_split
        from sklearn.neighbors import KNeighborsClassifier

        X, y = load_penguins()
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2,
                                              random_state=42)

        def acc(k):
            return KNeighborsClassifier(n_neighbors=k).fit(Xtr, ytr)\
                .score(Xte, yte)

        self.heading("What does K change in KNN?")
        frame, to_pt = panel(width=7.6, height=4.3, center=LEFT * 1.9 + DOWN * 0.1)
        dots = VGroup(*[marker(s, to_pt(a, b), 0.042) for (a, b), s in zip(X, y)])
        labels = axis_labels(frame, "bill length →", "flipper length →")
        leg = legend(font_size=24).move_to(RIGHT * 4.6 + UP * 1.3)
        self.play(Create(frame), FadeIn(dots, lag_ratio=0.004), FadeIn(labels),
                  FadeIn(leg), run_time=1.0)

        self.add_foreground_mobjects(dots)

        def k_label(k):
            return Text(f"K = {k}", font_size=50, weight=BOLD, color=NAVY)\
                .move_to(RIGHT * 4.6 + DOWN * 0.2)

        def regions(k):
            clf = KNeighborsClassifier(n_neighbors=k).fit(X, y)
            return region_mobject(clf.predict, frame, 180)

        img, kl = regions(1), k_label(1)
        self.add(img)
        self.bring_to_back(img)
        img.set_opacity(0)
        self.say("K = 1: each spot copies its single nearest penguin.",
                 img.animate.set_opacity(1), FadeIn(kl), run_time=0.9)
        self.say("Jagged edges: it trusts every point, noise included.")

        for k, cap in ((5, "A bigger K averages more neighbours…"),
                       (15, "…so the boundary gets smoother.")):
            new_img, new_kl = regions(k), k_label(k)
            self.say(cap, FadeTransform(img, new_img), Transform(kl, new_kl),
                     run_time=0.9)
            self.bring_to_back(new_img)
            img = new_img

        new_img, new_kl = regions(200), k_label(200)
        self.say("Too big: small groups get outvoted by the majority.",
                 FadeTransform(img, new_img), Transform(kl, new_kl),
                 run_time=0.9)
        self.bring_to_back(new_img)

        cmp_ = VGroup(
            Text("accuracy on unseen penguins", font_size=20, color=INK_SOFT),
            Text(f"K = 15     {acc(15):.2f}", font_size=27, color=TEAL,
                 weight=BOLD),
            Text(f"K = 200   {acc(200):.2f}", font_size=27, color=ORANGE,
                 weight=BOLD),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).next_to(kl, DOWN, buff=0.3)
        self.play(FadeIn(cmp_, shift=UP * 0.1), run_time=0.6)
        self.wait(1.2)
        self.takeaway("K is your choice: too small is jumpy, "
                      "too large ignores real groups.")


# =====================================================================
# Asset 20 — imputation: filling gaps invents data.
# =====================================================================
class Imputation(Lesson):
    def construct(self):
        import pandas as pd

        src = TITANIC if TITANIC.exists() else TITANIC_URL
        age = pd.read_csv(src)["Age"]
        observed = age.dropna().to_numpy()
        n_missing = int(age.isna().sum())
        median = float(age.median())
        filled = age.fillna(median).to_numpy()

        edges = np.arange(0, 85, 5)
        h_obs, _ = np.histogram(observed, bins=edges)
        h_fill, _ = np.histogram(filled, bins=edges)
        top = float(h_fill.max())
        med_bin = int(np.digitize(median, edges) - 1)

        self.heading("What happens when you fill in missing ages?")

        W, H = 8.6, 3.3
        base = DOWN * 1.5 + LEFT * 1.6
        axis = Line(base + LEFT * W / 2, base + RIGHT * W / 2, color=NAVY,
                    stroke_width=3)
        ticks = VGroup(*[
            Text(str(v), font_size=18, color=INK_SOFT)
            .move_to(base + RIGHT * (v / 80 * W - W / 2) + DOWN * 0.22)
            for v in (0, 20, 40, 60, 80)])
        xlab = Text("age (years)", font_size=20, color=INK_SOFT)\
            .next_to(axis, RIGHT, buff=0.2)
        bars = bar_chart(h_obs, base, W, H, top, BLUE)

        missing = VGroup(*[Text("?", font_size=22, color=ORANGE, weight=BOLD)
                           for _ in range(40)])\
            .arrange_in_grid(rows=5, cols=8, buff=(0.16, 0.06))
        miss_lbl = Text(f"{n_missing} ages missing", font_size=24,
                        color=ORANGE, weight=BOLD)
        VGroup(miss_lbl, missing).arrange(DOWN, buff=0.18)\
            .move_to(RIGHT * 5.0 + UP * 0.7)
        self.say(f"Titanic: {n_missing} of {len(age)} passengers "
                 "have no recorded age.",
                 Create(axis), FadeIn(ticks), FadeIn(xlab),
                 LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars],
                             lag_ratio=0.03),
                 FadeIn(miss_lbl), FadeIn(missing), run_time=1.5)

        mx = base + RIGHT * (median / 80 * W - W / 2)
        mline = DashedLine(mx, mx + UP * H, color=TEAL, stroke_width=3)
        mlab = Text(f"median = {median:.0f}", font_size=24, color=TEAL,
                    weight=BOLD).next_to(mline, UP, buff=0.1)\
            .shift(LEFT * 0.9)
        self.say(f"A common fix: give every one the median age, {median:.0f}.",
                 Create(mline), FadeIn(mlab), run_time=0.9)

        grown = bar_chart(h_fill, base, W, H, top, BLUE)[med_bin]\
            .set_fill(ORANGE)
        self.say(f"All {n_missing} land in one bar: "
                 f"{h_obs[med_bin]} → {h_fill[med_bin]}.",
                 missing.animate.move_to(bars[med_bin].get_top() + UP * 0.2)
                 .scale(0.15).set_opacity(0),
                 Transform(bars[med_bin], grown), FadeOut(miss_lbl),
                 run_time=1.5)
        jump = Text(f"{h_obs[med_bin]} → {h_fill[med_bin]}", font_size=28,
                    color=ORANGE, weight=BOLD)\
            .next_to(grown, RIGHT, buff=0.15).align_to(grown, UP)
        self.play(FadeIn(jump, shift=LEFT * 0.1), run_time=0.4)

        sd = VGroup(
            Text("spread (standard deviation)", font_size=21, color=INK_SOFT),
            Text(f"{np.std(observed, ddof=1):.1f}  →  "
                 f"{np.std(filled, ddof=1):.1f} years",
                 font_size=30, color=NAVY, weight=BOLD),
        ).arrange(DOWN, buff=0.1).move_to(RIGHT * 5.0 + UP * 0.7)
        self.say("The ages now look less varied than they really were.",
                 FadeIn(sd, shift=UP * 0.1), run_time=0.8)
        self.takeaway("Filling gaps invents data — it can distort "
                      "the real shape.")


# =====================================================================
# Asset 21 — what "nearest" means, and why raw units wreck it.
# =====================================================================
class KNNDistance(Lesson):
    def construct(self):
        self.heading("What does “nearest” mean for KNN?")

        frame, to_pt = panel(width=4.8, height=3.5, center=LEFT * 3.95 + DOWN * 0.35)
        a, b = np.array([0.18, 0.2]), np.array([0.8, 0.78])
        pa = marker("Adelie", to_pt(*a), 0.1)
        pb = Star(n=5, outer_radius=0.17, color=NAVY, fill_opacity=1,
                  fill_color=WHITE, stroke_width=4).move_to(to_pt(*b))
        hyp = Line(to_pt(*a), to_pt(*b), color=NAVY, stroke_width=4)
        dl = Text("distance", font_size=22, color=NAVY)\
            .rotate(hyp.get_angle())\
            .move_to(hyp.get_center() + rotate_vector(UP * 0.28, hyp.get_angle()))
        self.say("Distance = the straight line between two penguins.",
                 Create(frame), FadeIn(pa), FadeIn(pb), Create(hyp), FadeIn(dl),
                 run_time=1.1)

        corner = to_pt(b[0], a[1])
        dx = Line(to_pt(*a), corner, color=ORANGE, stroke_width=5)
        dy = Line(corner, to_pt(*b), color=TEAL, stroke_width=5)
        dxl = Text("Δ bill", font_size=22, color=ORANGE)\
            .next_to(dx, DOWN, buff=0.1)
        dyl = Text("Δ mass", font_size=22, color=TEAL).next_to(dy, RIGHT, buff=0.1)
        eq = MathTex(r"d=\sqrt{(\Delta\,\text{bill})^2+(\Delta\,\text{mass})^2}",
                     font_size=42).move_to(RIGHT * 2.6 + UP * 1.75)
        self.say("Pythagoras: square each difference, add, take the root.",
                 Create(dx), Create(dy), FadeIn(dxl), FadeIn(dyl), Write(eq),
                 run_time=1.3)

        raw = VGroup(
            Text("Δ bill = 5 mm", font_size=28, color=ORANGE, weight=BOLD),
            Text("Δ mass = 500 g", font_size=28, color=TEAL, weight=BOLD),
        ).arrange(RIGHT, buff=0.9).move_to(RIGHT * 2.6 + UP * 0.8)
        self.say("In raw units: 5 mm of bill, 500 g of body mass.",
                 FadeIn(raw, shift=UP * 0.1), run_time=0.7)

        # squared contributions as bars, drawn to scale
        full = 6.0
        left = RIGHT * (2.6 - full / 2) + DOWN * 0.15

        def hbar(value, total, color, y):
            w = max(full * value / total, 0.03)
            return Rectangle(width=w, height=0.46, stroke_width=0,
                             fill_color=color, fill_opacity=1)\
                .move_to(left + RIGHT * w / 2 + DOWN * y)

        tot = 25 + 250000
        b1 = hbar(25, tot, ORANGE, 0)
        b2 = hbar(250000, tot, TEAL, 0.66)
        t1 = Text("bill²  =  25", font_size=24, color=ORANGE, weight=BOLD)\
            .next_to(b1, RIGHT, buff=0.15)
        t2 = Text("mass²  =  250 000", font_size=24, color=WHITE, weight=BOLD)\
            .move_to(b2)
        self.say("Squared, that is 25 versus 250 000.",
                 GrowFromEdge(b1, LEFT), GrowFromEdge(b2, LEFT),
                 FadeIn(t1), FadeIn(t2), run_time=1.1)
        pct = Text("bill decides 0.01% of the distance", font_size=26,
                   color=NAVY, weight=BOLD).next_to(b2, DOWN, buff=0.32)\
            .align_to(b2, LEFT)
        self.say("So mass decides alone — bill is ignored.",
                 FadeIn(pct, shift=UP * 0.1), run_time=0.7)

        # after scaling
        tot2 = 1.21 + 0.81
        s1 = hbar(1.21, tot2 * 1.6, ORANGE, 0)
        s2 = hbar(0.81, tot2 * 1.6, TEAL, 0.66)
        st1 = Text("bill² = 1.1² = 1.21", font_size=24, color=ORANGE,
                   weight=BOLD).next_to(s1, RIGHT, buff=0.15)
        st2 = Text("mass² = 0.9² = 0.81", font_size=24, color=TEAL,
                   weight=BOLD).next_to(s2, RIGHT, buff=0.15)
        res = Text("penguins, KNN accuracy:  0.82 → 0.99", font_size=26,
                   color=TEAL, weight=BOLD).move_to(pct).align_to(pct, LEFT)
        raw2 = Text("after scaling both features", font_size=28,
                    color=NAVY, weight=BOLD).move_to(raw)
        self.say("Fix: scale both features to the same range.",
                 Transform(b1, s1), Transform(b2, s2), Transform(t1, st1),
                 Transform(t2, st2), Transform(pct, res), Transform(raw, raw2),
                 run_time=1.3)
        self.takeaway("Scale your features, or the biggest units "
                      "decide who is ‘near’.")


# =====================================================================
# Asset 22 — how logistic regression turns features into a probability.
# =====================================================================
class LogisticCurve(Lesson):
    def construct(self):
        self.heading("How does the model output a probability?")

        s1 = Text("STEP 1", font_size=20, color=TEAL, weight=BOLD)
        z_eq = MathTex(r"z", r"=", r"w_1", r"\cdot\text{flipper}", r"+",
                       r"w_2", r"\cdot\text{mass}", r"+", r"w_3",
                       r"\cdot\text{bill}", r"+", r"b", font_size=38)
        for i in (2, 5, 8, 11):
            z_eq[i].set_color(BLUE)
        row1 = VGroup(s1, z_eq).arrange(RIGHT, buff=0.35).move_to(UP * 2.0)
        self.say("Step 1: weigh each measurement and add them up.",
                 FadeIn(s1), Write(z_eq), run_time=1.2)
        wnote = Text("the weights w and b are what fit() learns",
                     font_size=22, color=BLUE).next_to(z_eq, DOWN, buff=0.12)
        self.say("The result z is a score: any number, −40 or +17.",
                 FadeIn(wnote), run_time=0.6)

        s2 = Text("STEP 2", font_size=20, color=TEAL, weight=BOLD)
        p_eq = MathTex(r"p=\frac{1}{1+e^{-z}}", font_size=36, color=NAVY)
        VGroup(s2, p_eq).arrange(RIGHT, buff=0.35)\
            .next_to(row1, DOWN, buff=0.55).align_to(row1, LEFT)
        ax = Axes(x_range=[-6, 6, 2], y_range=[0, 1, 0.5],
                  x_length=7.6, y_length=2.45,
                  axis_config={"color": NAVY, "stroke_width": 2.5},
                  tips=False).move_to(DOWN * 1.0 + RIGHT * 1.6)
        ylab = VGroup(
            Text("1", font_size=20, color=INK_SOFT)
            .next_to(ax.c2p(-6, 1), LEFT, buff=0.12),
            Text("0", font_size=20, color=INK_SOFT)
            .next_to(ax.c2p(-6, 0), LEFT, buff=0.12),
        )
        zlab = MathTex("z", font_size=30).next_to(ax.x_axis, RIGHT, buff=0.15)
        curve = ax.plot(lambda z: 1 / (1 + np.exp(-z)), color=BLUE,
                        stroke_width=6)
        self.say("Step 2: the sigmoid squashes z into 0 to 1.",
                 FadeOut(wnote), FadeIn(s2), Write(p_eq), Create(ax),
                 FadeIn(ylab), FadeIn(zlab), Create(curve), run_time=1.5)

        zt = ValueTracker(-5)

        def sig(z):
            return 1 / (1 + np.exp(-z))

        dot = always_redraw(lambda: Dot(ax.c2p(zt.get_value(),
                                               sig(zt.get_value())),
                                        radius=0.1, color=ORANGE))
        drop = always_redraw(lambda: DashedLine(
            ax.c2p(zt.get_value(), 0), ax.c2p(zt.get_value(), sig(zt.get_value())),
            color=ORANGE, stroke_width=2))

        def ro():
            z = zt.get_value()
            return VGroup(
                Text(f"z = {z:+.1f}", font=MONO, font_size=26, color=ORANGE),
                Text(f"p = {sig(z):.2f}", font=MONO, font_size=26,
                     color=ORANGE, weight=BOLD),
            ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)\
             .move_to(LEFT * 4.9 + DOWN * 0.9)
        readout = always_redraw(ro)
        self.add(drop, dot, readout)
        self.say("Very negative z → near 0. Large z → near 1.",
                 zt.animate.set_value(4.5), run_time=2.6)

        half = DashedLine(ax.c2p(-6, 0.5), ax.c2p(6, 0.5), color=NAVY,
                          stroke_width=2.5)
        up = Text("p > 0.5 → Gentoo", font_size=24, color=TEAL, weight=BOLD)\
            .move_to(ax.c2p(4.2, 0.7))
        dn = Text("p < 0.5 → not Gentoo", font_size=24, color=INK_SOFT,
                  weight=BOLD).move_to(ax.c2p(-4.0, 0.36))
        self.say("Above one half → Gentoo. Below → not Gentoo.",
                 Create(half), FadeIn(up), FadeIn(dn),
                 zt.animate.set_value(1.4), run_time=1.2)
        self.takeaway("A weighted score, squashed into a probability — "
                      "fit() picks the weights.")


# =====================================================================
# Asset 23 — the confusion matrix, built from the deck's real predictions.
# Same model as the deck and NB2: three features, 80/20 split with
# random_state=42, LogisticRegression(max_iter=1000) -> 67 test penguins.
# =====================================================================
def deck_test_predictions():
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    df = penguins_df()
    X = df[["flipper_length_mm", "body_mass_g", "bill_length_mm"]]
    y = df["species"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2,
                                              random_state=42)
    model = LogisticRegression(max_iter=1000).fit(X_tr, y_tr)
    return list(y_te), list(model.predict(X_te))


class ConfusionMatrix(Lesson):
    def construct(self):
        truth, pred = deck_test_predictions()
        n = len(truth)
        idx = {sp: i for i, sp in enumerate(SPECIES)}
        counts = np.zeros((3, 3), int)
        for t, p in zip(truth, pred):
            counts[idx[t], idx[p]] += 1
        right = int(np.trace(counts))
        acc = right / n

        self.heading(f"{acc:.0%} correct — but which mistakes?")

        # ---- the empty grid: rows = truth, columns = prediction ---------
        S = 1.42
        g0 = np.array([3.05, -0.4, 0])            # grid centre

        def cell_center(r, c):
            return g0 + np.array([(c - 1) * S, (1 - r) * S, 0])

        cells = VGroup(*[
            Square(side_length=S, stroke_color=GRAY, stroke_width=3,
                   fill_color=WHITE, fill_opacity=1).move_to(cell_center(r, c))
            for r in range(3) for c in range(3)
        ])
        col_lab = VGroup(*[
            VGroup(marker(sp, ORIGIN, 0.09),
                   Text(sp, font_size=22, color=SPECIES_COLOR[sp]))
            .arrange(DOWN, buff=0.08).next_to(cells[c], UP, buff=0.12)
            for c, sp in enumerate(SPECIES)
        ])
        row_lab = VGroup(*[
            VGroup(Text(sp, font_size=22, color=SPECIES_COLOR[sp]),
                   marker(sp, ORIGIN, 0.09))
            .arrange(RIGHT, buff=0.12).next_to(cells[3 * r], LEFT, buff=0.14)
            for r, sp in enumerate(SPECIES)
        ])
        said = Text("what the model said →", font_size=24, color=NAVY,
                    weight=BOLD).next_to(col_lab, UP, buff=0.1)
        really = Text("what it really is ↓", font_size=24, color=NAVY,
                      weight=BOLD).next_to(row_lab, UP, buff=0.18)\
            .align_to(row_lab, RIGHT)

        # ---- the 67 unseen penguins, waiting in a pile -------------------
        rng = np.random.default_rng(7)
        order = list(rng.permutation(n))
        # open with three easy, correct ones — one of each species
        firsts = []
        for sp in SPECIES:
            firsts.append(next(i for i in order
                               if truth[i] == sp and pred[i] == sp
                               and i not in firsts))
        order = firsts + [i for i in order if i not in firsts]

        pile_c = np.array([-5.15, -0.55, 0])
        cols = 7
        pile_pos = {}
        for k, i in enumerate(order):
            r, c = divmod(k, cols)
            pile_pos[i] = pile_c + np.array([(c - 3) * 0.24,
                                             1.15 - r * 0.24, 0])
        dots = {i: marker(truth[i], pile_pos[i], 0.07) for i in order}
        pile = VGroup(*dots.values())
        pile_lab = Text(f"{n} unseen penguins", font_size=24,
                        color=ORANGE, weight=BOLD)\
            .next_to(pile, UP, buff=0.2)

        model = VGroup(
            RoundedRectangle(width=1.5, height=0.8, corner_radius=0.14,
                             stroke_color=NAVY, stroke_width=3,
                             fill_color=PAPER, fill_opacity=1),
            Text("model", font_size=24, weight=BOLD),
        ).move_to(np.array([-2.75, -0.55, 0]))
        model[1].move_to(model[0])

        self.say(f"{n} test penguins the model has never seen.",
                 FadeIn(pile, lag_ratio=0.01), FadeIn(pile_lab),
                 FadeIn(model), run_time=1.0)
        self.say("Rows: what it really is. Columns: what the model said.",
                 FadeIn(cells, lag_ratio=0.05), FadeIn(col_lab), FadeIn(said),
                 FadeIn(row_lab), FadeIn(really), run_time=1.1)

        # ---- slots inside each cell, and a live count per cell ----------
        slot_n = np.zeros((3, 3), int)

        def next_slot(r, c):
            k = slot_n[r, c]
            slot_n[r, c] += 1
            rr, cc = divmod(k, 6)
            return cell_center(r, c) + np.array([(cc - 2.5) * 0.2,
                                                 0.32 - rr * 0.2, 0])

        tally = [[Integer(0, font_size=22, color=INK_SOFT)
                  .move_to(cell_center(r, c) + np.array([0.48, 0.52, 0]))
                  for c in range(3)] for r in range(3)]
        self.add(*[t for row in tally for t in row])
        live = np.zeros((3, 3), int)

        def fly(i):
            r, c = idx[truth[i]], idx[pred[i]]
            live[r, c] += 1
            return dots[i].animate(path_arc=-0.6).move_to(next_slot(r, c))\
                .scale(0.8)

        def tally_anims(before):
            return [ChangeDecimalToValue(tally[r][c], live[r, c])
                    for r in range(3) for c in range(3)
                    if live[r, c] != before[r, c]]

        # the first three: slowly, through the model
        cap = "Each penguin lands in row = truth, column = guess."
        # no reading pause here — the flights below take longer than the read
        self.say(cap, run_time=0.45, extra=-(read_time(cap) - 0.45))
        for i in order[:3]:
            self.play(dots[i].animate.move_to(model.get_center()).scale(1.3),
                      model[0].animate.set_stroke(TEAL), run_time=0.3)
            before = live.copy()
            self.play(fly(i), *tally_anims(before),
                      model[0].animate.set_stroke(NAVY), run_time=0.4)
        # then the rest, faster and faster
        rest = order[3:]
        for chunk in (rest[:10], rest[10:28], rest[28:]):
            before = live.copy()
            self.play(LaggedStart(*[fly(i) for i in chunk], lag_ratio=0.08),
                      *tally_anims(before), run_time=1.0)

        # ---- markers become counts --------------------------------------
        big = VGroup()
        for r in range(3):
            for c in range(3):
                col = NAVY if counts[r, c] else GRAY
                big.add(Text(str(counts[r, c]), font_size=50, color=col,
                             weight=BOLD).move_to(cell_center(r, c)))
        self.play(FadeOut(pile_lab), FadeOut(model),
                  *[FadeOut(d, scale=0.5) for d in dots.values()],
                  *[FadeOut(t) for row in tally for t in row],
                  FadeIn(big, scale=1.3), run_time=0.8)

        # ---- the diagonal ------------------------------------------------
        diag = [cells[3 * k + k] for k in range(3)]
        self.say("The diagonal is where the model was right.",
                 *[d.animate.set_fill(TEAL_WASH).set_stroke(TEAL, 5)
                   for d in diag],
                 *[big[3 * k + k].animate.set_color(TEAL) for k in range(3)],
                 run_time=0.8)
        d = [int(counts[k, k]) for k in range(3)]
        sum_txt = VGroup(
            Text("accuracy", font_size=26, color=INK_SOFT),
            Text(f"({d[0]} + {d[1]} + {d[2]}) ÷ {n}", font_size=30,
                 color=NAVY),
            Text(f"= {right} ÷ {n} = {acc:.0%}", font_size=34, color=TEAL,
                 weight=BOLD),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)\
            .to_edge(LEFT, buff=0.6).shift(UP * 0.75)
        self.say("Accuracy = the diagonal ÷ all penguins.",
                 FadeIn(sum_txt, shift=RIGHT * 0.2, lag_ratio=0.3),
                 run_time=1.0)

        # ---- the mistakes, read in plain English -------------------------
        wrong = [(r, c) for r in range(3) for c in range(3)
                 if r != c and counts[r, c]]

        def plural(k, sp):
            return f"{k} {sp}" + ("s" if k > 1 else "")

        lines = [f"{plural(counts[r, c], SPECIES[r])} → called "
                 f"{'an' if SPECIES[c][0] in 'AEIOU' else 'a'} {SPECIES[c]}"
                 for r, c in wrong]
        mist = VGroup(
            Text("the mistakes", font_size=26, color=ORANGE, weight=BOLD),
            *[Text(s, font_size=25, color=NAVY) for s in lines],
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)\
            .next_to(sum_txt, DOWN, buff=0.5).align_to(sum_txt, LEFT)
        rings = [cells[3 * r + c] for r, c in wrong]
        self.say("Off the diagonal: each cell names one kind of mistake.",
                 *[x.animate.set_fill(ORANGE_WASH).set_stroke(ORANGE, 5)
                   for x in rings],
                 *[big[3 * r + c].animate.set_color(ORANGE) for r, c in wrong],
                 FadeIn(mist, shift=RIGHT * 0.2, lag_ratio=0.3),
                 run_time=1.1)
        self.play(*[Indicate(big[3 * r + c], color=ORANGE, scale_factor=1.35)
                    for r, c in wrong], run_time=0.8)
        self.takeaway("The diagonal is what it got right. "
                      "Every other cell names a mistake.")
