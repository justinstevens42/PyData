# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "matplotlib==3.10.8",
#     "numpy==2.4.3",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="Central Limit Theorem Explorer")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Central Limit Theorem Explorer

    Average $n$ independent draws from almost **any** distribution, and the average is approximately normal:

    $$\overline{X} = \frac{X_1 + \cdots + X_n}{n} \approx \mathcal{N}\left(\mu, \frac{\sigma^2}{n}\right).$$

    **How the explorer works:**

    1. Draw $n$ values from the distribution you pick. (The left plot shows that distribution.)
    2. Compute their mean.
    3. Repeat steps 1 and 2 *Simulations* times, and plot all of those means as a histogram (the right plot).

    The CLT predicts the shape of that histogram: the dashed bell curve $\mathcal{N}(\mu, \sigma^2/n)$. A bigger $n$ is what makes the means bell-shaped and narrower; more simulations only make the histogram smoother.

    Add up 100 random numbers, each Uniform(0, 1). What does the total look like? The explorer starts there, at *uniform* with $n = 100$. (The total is just $100 \times$ the mean, so it has the same shape.) Then pick another distribution and drag the slider. The plots update as you go.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The distributions, in brief

    - **Uniform:** every value between 0 and 1 is equally likely, so its plot is flat. It's the easy case.
    - **Exponential:** the waiting time until something happens. Mostly small values, with a long tail to the right.
    - **Lognormal:** values that come from multiplying many random factors, like incomes, or money that grows or shrinks by a random percentage each year. Mostly modest, with rare huge outliers.
    - **Two humps:** a mix of two groups, so there are two peaks. It looks weird, but it's symmetric, so its averages turn normal quickly.
    - **Binomial:** how many successes you get in a fixed number of yes/no tries. Here, how many of 10 visitors buy, when each buys with a 10% chance.
    - **Poisson:** how many rare events happen in a fixed window. Here, emails in an hour, when 2 arrive per hour on average. It's the flip side of *exponential*: for events arriving at random, exponential is the gap between them, and Poisson is the count in a window.

    The more lopsided the distribution, the bigger $n$ has to be before its averages look normal. Lognormal needs the biggest $n$, and uniform the smallest.
    """)
    return


@app.cell(hide_code=True)
def _(DISTRIBUTIONS, mo):
    distribution = mo.ui.dropdown(options=list(DISTRIBUTIONS), value="uniform", label="Distribution")
    sample_size = mo.ui.slider(start=1, stop=100, step=1, value=100, show_value=True, label="Sample size $n$")
    simulations = mo.ui.slider(start=500, stop=20_000, step=500, value=5_000, show_value=True, label="Simulations")
    resample = mo.ui.button(value=0, on_click=lambda count: count + 1, label="Draw new samples")
    zoom = mo.ui.switch(value=False, label="Zoom in on the averages")

    mo.hstack([distribution, sample_size, simulations, resample, zoom], justify="space-around", align="center", wrap=True)
    return distribution, resample, sample_size, simulations, zoom


@app.cell(hide_code=True)
def _(averages, dist, n, np, plt, sims, zoom):
    def _histogram(ax, values, step, color, xlim, label=None):
        """Density histogram. Discrete values sit on multiples of `step`, so center one bar on each."""
        if step is None:
            # 50 bars across the on-screen part of the data, so a long tail (lognormal) doesn't make them coarse.
            # Weights keep the heights a true density even though off-screen values are left out.
            bins = np.linspace(max(values.min(), xlim[0]), min(values.max(), xlim[1]), 51)
            weights = np.full(len(values), 1 / (len(values) * (bins[1] - bins[0])))
            ax.hist(values, bins=bins, weights=weights, color=color, label=label)
        else:
            k = np.round(values / step)
            stride = max(1, int(np.ceil((k.max() - k.min() + 1) / 150)))  # at most ~150 bars
            bins = (np.arange(k.min(), k.max() + stride + 1, stride) - 0.5) * step
            ax.hist(values, bins=bins, density=True, color=color, label=label)

    _fig, (_left, _right) = plt.subplots(1, 2, figsize=(10, 3.6), layout="constrained")

    # Left: the exact distribution (not a sample), so it only changes when you pick another one
    if dist["discrete"]:
        _k = np.arange(int(np.ceil(dist["xlim"][0])), int(np.floor(dist["xlim"][1])) + 1)
        _left.bar(_k, dist["density"](_k), width=1, color="#bdbdbd", edgecolor="white", linewidth=1)
    else:
        _xs = np.linspace(*dist["xlim"], 500)
        with np.errstate(divide="ignore", invalid="ignore"):  # e.g. lognormal at x = 0
            _pdf = np.nan_to_num(dist["density"](_xs))
        _left.fill_between(_xs, _pdf, color="#bdbdbd", linewidth=0)
    _left.set_title(f"Original distribution: {dist['label']}")
    _left.set_xlim(dist["xlim"])

    # Same x-axis as the left plot, so you can see the averages narrow; or zoom to the CLT's mean ± 4 sd
    _sd = np.sqrt(dist["var"] / n)
    _right_xlim = dist["xlim"]
    if zoom.value:
        _right_xlim = (max(dist["xlim"][0], dist["mean"] - 4 * _sd), min(dist["xlim"][1], dist["mean"] + 4 * _sd))
    _right.set_xlim(_right_xlim)

    _histogram(_right, averages, 1 / n if dist["discrete"] else None, "#e9a3a3", _right_xlim, label=f"{sims:,} simulated averages")
    _x = np.linspace(*_right_xlim, 500)
    _normal = np.exp(-0.5 * ((_x - dist["mean"]) / _sd) ** 2) / (_sd * np.sqrt(2 * np.pi))
    _right.plot(_x, _normal, color="#333333", linestyle="--", linewidth=2, label=r"CLT prediction $\mathcal{N}(\mu, \sigma^2/n)$")
    _right.set_title(f"Average of n = {n} draw{'' if n == 1 else 's'}")

    for _ax in (_left, _right):
        _ax.axvline(dist["mean"], color="#cccccc", linewidth=1, zorder=0)
        _ax.set_yticks([])
        _ax.spines[["top", "right", "left"]].set_visible(False)
    _fig.legend(loc="outside lower right", ncol=2, frameon=False)
    _fig
    return


@app.cell(hide_code=True)
def _(averages, dist, mo, n, np):
    _mean, _sd = averages.mean(), averages.std()
    _skew = np.mean(((averages - _mean) / _sd) ** 3) if _sd > 0 else 0.0

    mo.hstack(
        [
            mo.stat(f"{_mean:.3f}", label="Mean of the averages", caption=f"CLT predicts μ = {dist['mean']:.3f}", bordered=True),
            mo.stat(f"{_sd:.3f}", label="Spread (standard deviation)", caption=f"CLT predicts σ/√n = {np.sqrt(dist['var'] / n):.3f}", bordered=True),
            mo.stat(f"{_skew:+.2f}", label="Skewness", caption="A bell curve has 0", bordered=True),
        ],
        justify="center",
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## What to notice

    - **Shape:** even a lopsided distribution, like *exponential*, gives averages that look like a bell curve once $n$ is large enough.
    - **Center:** the averages stay centered on the mean $\mu$ (the gray line).
    - **Spread:** the averages narrow like $\sigma / \sqrt{n}$. Quadruple $n$, and the spread halves.

    **Try this:**

    - *Exponential*: slide $n$ from 1 up to 30.
    - *Two humps*: two peaks, and the averages still form one bell. (At $n = 2$, count the humps.)
    - *Lognormal*: still visibly lopsided at $n = 30$, so "30 is enough" is only a rule of thumb.
    - *Binomial* or *poisson* at $n = 1$: lopsided, discrete bars that still smooth into a bell.

    Once the averages get narrow, flip on **Zoom in on the averages** to see their shape up close.

    ## How it works

    The cell below is the whole simulation. It draws a grid of values with *Simulations* rows and $n$ columns, so each row is one sample of $n$ draws, then takes the mean of each row. marimo is reactive: when you change a control above, this cell reruns, and so does every cell that uses its results.
    """)
    return


@app.cell
def _(DISTRIBUTIONS, distribution, np, resample, sample_size, simulations):
    resample.value  # clicking "Draw new samples" reruns this cell
    dist = DISTRIBUTIONS[distribution.value]
    n, sims = sample_size.value, simulations.value

    rng = np.random.default_rng()
    averages = dist["sample"](rng, (sims, n)).mean(axis=1)  # each row: n draws, averaged
    return averages, dist, n, sims


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Add your own distribution

    Each entry says how to draw samples (`sample`), what the distribution looks like for the left plot (`density`: the probability density, or for a discrete distribution, the probability of each whole number), and its mean and variance for the CLT's prediction. Add one below, and it appears in the dropdown. For example, a die roll:

    ```python
    "die roll": dict(
        label="Die roll", mean=3.5, var=35 / 12, discrete=True, xlim=(0.5, 6.5),
        sample=lambda rng, size: rng.integers(1, 7, size),
        density=lambda k: np.full(len(k), 1 / 6),
    ),
    ```
    """)
    return


@app.cell
def _(math, np):
    # density: the probability density at x for continuous distributions; for discrete ones,
    # the probability of each whole number k
    DISTRIBUTIONS = {
        "uniform": dict(
            label="Uniform(0, 1)", mean=1 / 2, var=1 / 12, discrete=False, xlim=(0, 1),
            sample=lambda rng, size: rng.uniform(0, 1, size),
            density=lambda x: np.where((x >= 0) & (x <= 1), 1.0, 0.0),
        ),
        "exponential": dict(
            label="Exponential(λ = 1)", mean=1, var=1, discrete=False, xlim=(0, 6),
            sample=lambda rng, size: rng.exponential(1, size),
            density=lambda x: np.exp(-x),
        ),
        "lognormal": dict(
            label="Lognormal(0, 1)", mean=np.exp(1 / 2), var=(np.e - 1) * np.e, discrete=False, xlim=(0, 8),
            sample=lambda rng, size: rng.lognormal(0, 1, size),
            density=lambda x: np.exp(-np.log(x) ** 2 / 2) / (x * np.sqrt(2 * np.pi)),
        ),
        "two humps": dict(  # half the draws near -2, half near +2, each with standard deviation 0.5
            label="Two humps (peaks at ±2)", mean=0, var=4.25, discrete=False, xlim=(-4, 4),
            sample=lambda rng, size: rng.normal(rng.choice([-2.0, 2.0], size=size), 0.5),
            density=lambda x: (np.exp(-2 * (x + 2) ** 2) + np.exp(-2 * (x - 2) ** 2)) / np.sqrt(2 * np.pi),
        ),
        "binomial": dict(
            label="Binomial(10, 0.1)", mean=1, var=0.9, discrete=True, xlim=(-0.5, 5.5),
            sample=lambda rng, size: rng.binomial(10, 0.1, size),
            density=lambda k: np.array([math.comb(10, int(i)) for i in k]) * 0.1**k * 0.9 ** (10 - k),
        ),
        "poisson": dict(
            label="Poisson(λ = 2)", mean=2, var=2, discrete=True, xlim=(-0.5, 8.5),
            sample=lambda rng, size: rng.poisson(2, size),
            density=lambda k: np.exp(-2) * 2.0**k / np.array([math.factorial(int(i)) for i in k]),
        ),
    }
    return (DISTRIBUTIONS,)


@app.cell
def _():
    import math

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    return math, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    _Adapted from the [Central Limit Theorem notebook](https://github.com/marimo-team/learn/blob/main/probability/18_central_limit_theorem.py) in [marimo-team/learn](https://github.com/marimo-team/learn) (MIT License), which builds on Chris Piech's [Probability for Computer Scientists](https://chrispiech.github.io/probabilityForComputerScientists/en/part4/clt/)._
    """)
    return


if __name__ == "__main__":
    app.run()
