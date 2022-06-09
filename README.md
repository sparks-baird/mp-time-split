[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![ReadTheDocs](https://readthedocs.org/projects/mp-time-split/badge/?version=latest)](https://mp-time-split.readthedocs.io/en/stable/)
[![PyPI-Server](https://img.shields.io/pypi/v/mp-time-split.svg)](https://pypi.org/project/mp-time-split/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/mp_time_split.svg)](https://anaconda.org/conda-forge/mp_time_split)
[![Coverage Status](https://coveralls.io/repos/github/sparks-baird/mp-time-split/badge.svg?branch=main)](https://coveralls.io/github/sparks-baird/mp-time-split?branch=main)
![Lines of code](https://img.shields.io/tokei/lines/github/sparks-baird/mp-time-split)
<!-- These are examples of badges you might also want to add to your README. Update the URLs accordingly.
[![Built Status](https://api.cirrus-ci.com/github/<USER>/mp-time-split.svg?branch=main)](https://cirrus-ci.com/github/<USER>/mp-time-split)
[![Monthly Downloads](https://pepy.tech/badge/mp-time-split/month)](https://pepy.tech/project/mp-time-split)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/mp-time-split)
-->

# mp-time-split

> Use Materials Project time-splits for generative modeling benchmarking.

While methods for cross-validating accuracy of materials informatics models is well
estabilished (see for example [Matbench](https://matbench.materialsproject.org/)),
evaluating the performance of generative models such as
[FTCP](https://github.com/PV-Lab/FTCP) or
[imatgen](https://github.com/kaist-amsg/imatgen), and [many
others](https://github.com/stars/sgbaird/lists/materials-generative-models) is less
straightforward. Recently, [Xie et al.](http://arxiv.org/abs/2110.06197) introduced new
benchmark datasets and metrics in [CDVAE](https://github.com/txie-93/cdvae) for several
state-of-the-art algorithms. This repository acts as a supplement to CDVAE benchmarks,
delivering [a new benchmark dataset](https://figshare.com/articles/dataset/Materials_Project_Time_Split_Data/19991516) (`Materials_Project_Time_Split_52` or **MPTS-52**) with time-based (5 $\times$ train/val)
+train/test splits suitable for cross-validated hyperparameter optimization and
subsequent benchmarking via the test split. **MPTS-52** is most comparable to **MP-20**
from [Xie et al.](http://arxiv.org/abs/2110.06197), with the difference that up to 52
atoms are allowed and possibly a difference in the unique elements, as no elemental
filtering was applied (e.g. removal of radioactive elements).

## Quick Start
### Installation
```bash
conda env create -n mp-time-split -c conda-forge mp_time_split
conda activate mp-time-split
```

### Example
```python
from mp_time_split.core import MPTimeSplit

mpt = MPTimeSplit(target="energy_above_hull")
mpt.load(dummy=False)

for fold in mpt.folds:
    train_inputs, val_inputs, train_outputs, val_outputs = mpt.get_train_and_val_data(
        fold
    )

final_train_inputs, test_inputs, final_train_outputs, test_outputs = mpt.get_test_data()
```

### Output
```python
print(train_inputs.iloc[0], train_outputs)
```

<table>
<tr>
<th> `train_inputs.iloc[0]` </th>
<th> `train_outputs` </th>
</tr>
<tr>
<td>

```python
Structure Summary
Lattice
    abc : 2.591619125942699 2.591619125942699 2.591619125942699
 angles : 109.47122063449069 109.47122063449069 109.47122063449069
 volume : 13.399593956465264
      A : -1.496272 1.496272 1.496272
      B : 1.496272 -1.496272 1.496272
      C : 1.496272 1.496272 -1.496272
PeriodicSite: V (0.0000, 0.0000, 0.0000) [0.0000, 0.0000, 0.0000]
```

</td>
<td>

```python
146      0.000000
925      0.190105
1282     0.087952
1335     0.022710
12778    0.003738
2540     0.000000
316      0.000000
```

</td>
</tr>
</table>

For additional examples, see the [notebooks](notebooks) directory.

## Installation

### Anaconda
Create an environment named (`-n`) `mp-time-split` with the Anaconda package `mp_time_split` intalled from the `conda-forge` channel (`-c`).
```bash
conda env create -n mp-time-split -c conda-forge mp_time_split
```

### PyPI
Optionally create and activate a conda environment (recommended to use an isolated environment of some kind):
```bash
conda env create -n mp-time-split python==3.9.* # 3.7.* or 3.8.* also OK
conda activate mp-time-split
```
Install the `mp-time-split` package from PyPI.
```bash
pip install mp-time-split
```

### `environment.yml`
In order to set up the necessary environment:

1. review and uncomment what you need in `environment.yml` and create an environment `mp-time-split` with the help of [conda]:
   ```
   conda env create -f environment.yml
   ```
2. activate the new environment with:
   ```
   conda activate mp-time-split
   ```

### Local Installation
> **_NOTE:_**  The conda environment will have mp-time-split installed in editable mode.
> Some changes, e.g. in `setup.cfg`, might require you to run `pip install -e .` again.


Optional and needed only once after `git clone`:

3. install several [pre-commit] git hooks with:
   ```bash
   pre-commit install
   # You might also want to run `pre-commit autoupdate`
   ```
   and checkout the configuration under `.pre-commit-config.yaml`.
   The `-n, --no-verify` flag of `git commit` can be used to deactivate pre-commit hooks temporarily.

4. install [nbstripout] git hooks to remove the output cells of committed notebooks with:
   ```bash
   nbstripout --install --attributes notebooks/.gitattributes
   ```
   This is useful to avoid large diffs due to plots in your notebooks.
   A simple `nbstripout --uninstall` will revert these changes.


Then take a look into the `scripts` and `notebooks` folders.

<!-- ## Dependency Management & Reproducibility

1. Always keep your abstract (unpinned) dependencies updated in `environment.yml` and eventually
   in `setup.cfg` if you want to ship and install your package via `pip` later on.
2. Create concrete dependencies as `environment.lock.yml` for the exact reproduction of your
   environment with:
   ```bash
   conda env export -n mp-time-split -f environment.lock.yml
   ```
   For multi-OS development, consider using `--no-builds` during the export.
3. Update your current environment with respect to a new `environment.lock.yml` using:
   ```bash
   conda env update -f environment.lock.yml --prune
   ``` -->

## Project Organization

```
├── AUTHORS.md              <- List of developers and maintainers.
├── CHANGELOG.md            <- Changelog to keep track of new features and fixes.
├── CONTRIBUTING.md         <- Guidelines for contributing to this project.
├── Dockerfile              <- Build a docker container with `docker build .`.
├── LICENSE.txt             <- License as chosen on the command-line.
├── README.md               <- The top-level README for developers.
├── configs                 <- Directory for configurations of model & application.
├── data
│   ├── external            <- Data from third party sources.
│   ├── interim             <- Intermediate data that has been transformed.
│   ├── processed           <- The final, canonical data sets for modeling.
│   └── raw                 <- The original, immutable data dump.
├── docs                    <- Directory for Sphinx documentation in rst or md.
├── environment.yml         <- The conda environment file for reproducibility.
├── models                  <- Trained and serialized models, model predictions,
│                              or model summaries.
├── notebooks               <- Jupyter notebooks. Naming convention is a number (for
│                              ordering), the creator's initials and a description,
│                              e.g. `1.0-fw-initial-data-exploration`.
├── pyproject.toml          <- Build configuration. Don't change! Use `pip install -e .`
│                              to install for development or to build `tox -e build`.
├── references              <- Data dictionaries, manuals, and all other materials.
├── reports                 <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures             <- Generated plots and figures for reports.
├── scripts                 <- Analysis and production scripts which import the
│                              actual PYTHON_PKG, e.g. train_model.
├── setup.cfg               <- Declarative configuration of your project.
├── setup.py                <- [DEPRECATED] Use `python setup.py develop` to install for
│                              development or `python setup.py bdist_wheel` to build.
├── src
│   └── mp_time_split       <- Actual Python package where the main functionality goes.
├── tests                   <- Unit tests which can be run with `pytest`.
├── .coveragerc             <- Configuration for coverage reports of unit tests.
├── .isort.cfg              <- Configuration for git hook that sorts imports.
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks.
```

<!-- pyscaffold-notes -->

## Note

This project has been set up using [PyScaffold] 4.2.2 and the [dsproject extension] 0.7.post1.dev8+g43a905e.

[conda]: https://docs.conda.io/
[pre-commit]: https://pre-commit.com/
[Jupyter]: https://jupyter.org/
[nbstripout]: https://github.com/kynan/nbstripout
[Google style]: http://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[PyScaffold]: https://pyscaffold.org/
[dsproject extension]: https://github.com/pyscaffold/pyscaffoldext-dsproject

To create the same starting point for this repository, as of 2022-06-01 on Windows you will need the development versions of PyScaffold and extensions, however this will not be necessary once certain bugfixes have been introduced in the next stable releases:
```bash
pip install git+https://github.com/pyscaffold/pyscaffold.git git+https://github.com/pyscaffold/pyscaffoldext-dsproject.git git+https://github.com/pyscaffold/pyscaffoldext-markdown.git
```

The following `pyscaffold` command creates a starting point for this repository:
```bash
putup xtal2png --github-actions --markdown --dsproj
```
Alternatively, you can edit a file interactively and update and uncomment relevant lines, which saves some of the additional setup:
```bash
putup --interactive xtal2png
```
