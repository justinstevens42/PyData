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

    **Start with the question from the talk:** add up 100 random numbers, each Uniform(0, 1). What does the total look like? The explorer starts there, at *uniform* with $n = 100$. (The total is just $100 \times$ the average, so it has the same shape.)

    Then pick another distribution and drag the slider. The plots update as you go.
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
def _(averages, dist, n, np, one_draw, plt, sims, zoom):
    def _histogram(ax, values, step, color, label=None):
        """Density histogram. Discrete values sit on multiples of `step`, so center one bar on each."""
        if step is None:
            bins = 50
        else:
            k = np.round(values / step)
            stride = max(1, int(np.ceil((k.max() - k.min() + 1) / 150)))  # at most ~150 bars
            bins = (np.arange(k.min(), k.max() + stride + 1, stride) - 0.5) * step
        ax.hist(values, bins=bins, density=True, color=color, label=label)

    _fig, (_left, _right) = plt.subplots(1, 2, figsize=(10, 3.6), layout="constrained")

    _histogram(_left, one_draw, 1 if dist["discrete"] else None, "#bdbdbd")
    _left.set_title(f"One draw: {dist['label']}")
    _left.set_xlim(dist["xlim"])

    # Same x-axis as the left plot, so you can see the averages narrow; or zoom to the CLT's mean ± 4 sd
    _sd = np.sqrt(dist["var"] / n)
    _right_xlim = dist["xlim"]
    if zoom.value:
        _right_xlim = (max(dist["xlim"][0], dist["mean"] - 4 * _sd), min(dist["xlim"][1], dist["mean"] + 4 * _sd))
    _right.set_xlim(_right_xlim)

    _histogram(_right, averages, 1 / n if dist["discrete"] else None, "#e9a3a3", label=f"{sims:,} simulated averages")
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

    **Try this:** choose *exponential*, then slide $n$ from 1 up to 30. Then try *binomial* or *poisson*, starting at $n = 1$: lopsided, discrete bars that still smooth into a bell. Once the averages get narrow, flip on **Zoom in on the averages** to see their shape up close.

    ## How it works

    Each simulation draws $n$ numbers and averages them; this is all the code there is. marimo is reactive: when you change a control above, this cell reruns, and so does every cell that uses its results.
    """)
    return


@app.cell
def _(DISTRIBUTIONS, distribution, np, resample, sample_size, simulations):
    resample.value  # clicking "Draw new samples" reruns this cell
    dist = DISTRIBUTIONS[distribution.value]
    n, sims = sample_size.value, simulations.value

    rng = np.random.default_rng()
    one_draw = dist["sample"](rng, sims)  # single draws, for the left plot
    averages = dist["sample"](rng, (sims, n)).mean(axis=1)  # each row: n draws, averaged
    return averages, dist, n, one_draw, sims


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Add your own distribution

    Each entry says how to draw samples, plus its mean and variance (for the CLT's prediction). Add one below, and it appears in the dropdown. For example, a die roll:

    ```python
    "die roll": dict(
        label="Die roll", mean=3.5, var=35 / 12, discrete=True, xlim=(0.5, 6.5),
        sample=lambda rng, size: rng.integers(1, 7, size),
    ),
    ```
    """)
    return


@app.cell
def _():
    DISTRIBUTIONS = {
        "uniform": dict(
            label="Uniform(0, 1)", mean=1 / 2, var=1 / 12, discrete=False, xlim=(0, 1),
            sample=lambda rng, size: rng.uniform(0, 1, size),
        ),
        "exponential": dict(
            label="Exponential(λ = 1)", mean=1, var=1, discrete=False, xlim=(0, 6),
            sample=lambda rng, size: rng.exponential(1, size),
        ),
        "binomial": dict(
            label="Binomial(10, 0.1)", mean=1, var=0.9, discrete=True, xlim=(-0.5, 5.5),
            sample=lambda rng, size: rng.binomial(10, 0.1, size),
        ),
        "poisson": dict(
            label="Poisson(λ = 2)", mean=2, var=2, discrete=True, xlim=(-0.5, 8.5),
            sample=lambda rng, size: rng.poisson(2, size),
        ),
    }
    return (DISTRIBUTIONS,)


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    return mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    _Adapted from the [Central Limit Theorem notebook](https://github.com/marimo-team/learn/blob/main/probability/18_central_limit_theorem.py) in [marimo-team/learn](https://github.com/marimo-team/learn) (MIT License), which builds on Chris Piech's [Probability for Computer Scientists](https://chrispiech.github.io/probabilityForComputerScientists/en/part4/clt/)._
    """)
    return


if __name__ == "__main__":
    app.run()
