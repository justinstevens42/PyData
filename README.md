# PyData San Diego: the Central Limit Theorem in marimo

The notebook for the intro to [marimo](https://marimo.io) at the PyData San Diego meetup: an interactive explorer for the Central Limit Theorem. Pick a distribution, drag the sample size, and watch the averages turn into a bell curve.

## Run it in your browser

Nothing to install:

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/justinstevens42/PyData/blob/main/central_limit_theorem.py)

## Run it on your laptop

With [uv](https://docs.astral.sh/uv/getting-started/installation/):

```sh
git clone https://github.com/justinstevens42/PyData
cd PyData
uv run marimo edit central_limit_theorem.py
```

The first run installs Python (if needed) and the packages pinned in `pyproject.toml` and `uv.lock`.

Without uv:

```sh
pip install marimo matplotlib numpy
marimo edit central_limit_theorem.py
```

## Try this

Choose the `exponential` distribution, then slide the sample size *n* from 1 up to 30. Then scroll down and add your own distribution: it shows up in the dropdown right away.

## Credits

The notebook is adapted from [`probability/18_central_limit_theorem.py`](https://github.com/marimo-team/learn/blob/main/probability/18_central_limit_theorem.py) in [marimo-team/learn](https://github.com/marimo-team/learn), used under the MIT License (see [LICENSE](LICENSE)), which builds on Chris Piech's [Probability for Computer Scientists](https://chrispiech.github.io/probabilityForComputerScientists/en/part4/clt/). The rest of marimo's probability course is in that repo.
