"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = ${package}.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import argparse
import logging
import sys

import pandas as pd
import pybtex.errors

from mp_time_split import __version__
from mp_time_split.utils.data import fetch_data
from mp_time_split.utils.split import AVAILABLE_MODES, mp_time_split

pybtex.errors.set_strict_mode(False)

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from ${qual_pkg}.skeleton import fib`,
# when using this Python module as a library.


def fib(n):
    """Fibonacci example function

    Args:
      n (int): integer

    Returns:
      int: n-th Fibonacci number
    """
    assert n > 0
    a, b = 1, 1
    for _i in range(n - 1):
        a, b = b, a + b
    return a


FOLDS = [0, 1, 2, 3, 4]


class MPTimeSplit:
    def __init__(
        self,
        nsites=None,
        elements=None,
        use_theoretical=False,
        mode="TimeSeriesSplit",
    ) -> None:
        if mode not in AVAILABLE_MODES:
            raise NotImplementedError(
                f"mode={mode} not implemented. Use one of {AVAILABLE_MODES}"
            )

        self.nsites = nsites
        self.elements = elements
        self.use_theoretical = use_theoretical
        self.mode = mode

        self.folds = FOLDS

    def fetch_data(self):
        self.data = fetch_data(
            nsites=self.nsites,
            elements=self.elements,
            use_theoretical=self.use_theoretical,
        )

        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("`self.data` is not a `pd.DataFrame`")

        self.trainval_splits, self.test_split = mp_time_split(
            self.data, n_cv_splits=len(FOLDS), mode=self.mode
        )

    def get_train_and_val_data(self, fold, target="energy_above_hull"):
        if fold not in FOLDS:
            raise ValueError(f"fold={fold} should be one of {FOLDS}")
        inputs = self.data.structure
        outputs = getattr(self.data, target)

        # self.y = self.data[]
        train_inputs, val_inputs = [
            inputs.iloc[self.trainval_splits[fold][i]] for i in [0, 1]
        ]
        train_outputs, val_outputs = [
            outputs.iloc[self.trainval_splits[fold][i]] for i in [0, 1]
        ]
        return train_inputs, val_inputs, train_outputs, val_outputs

    def get_test_data(self):
        return self.data.iloc[self.test_split]


# def split(df, n_compounds, n_splits, split_type):
#     if split_type == "TimeSeriesSplit":
#     # TimeSeriesSplit
#         tscv = TimeSeriesSplit(gap=0, n_splits=n_splits + 1)
#         splits = list(tscv.split(df))

#     elif split_type == "TimeSeriesOverflow":
#         all_index = list(range(n_compounds))
#         tscv = TimeSeriesSplit(gap=0, n_splits=n_splits + 1)
#         train_indices = []
#         test_indices = []
#         for tri, _ in tscv.split(df):
#             train_indices.append(tri)
#         # use remainder of data rather than default `test_index`
#             test_indices.append(np.setdiff1d(all_index, tri))

#         splits = list(zip(train_indices, test_indices))

#     elif split_type == "TimeKFold":
#         kf = KFold(n_splits=n_splits + 2)
#         splits = [indices[1] for indices in kf.split(df)]
#         splits.pop(-1)

#         running_index = np.empty(0, dtype=int)
#         train_indices = []
#         test_indices = []
#         all_index = list(range(n_compounds))
#         for s in splits:
#             running_index = np.concatenate((running_index, s))
#             train_indices.append(running_index)
#             test_indices.append(np.setdiff1d(all_index, running_index))

#         splits = list(zip(train_indices, test_indices))

#     for train_index, test_index in splits:
#         print("TRAIN:", train_index, "TEST:", test_index)

# split(df, n_compounds, n_splits, split_type)
# yield train_index, test_index

# for train_index, test_index in kf.split(df):
#     print("TRAIN:", train_index, "TEST:", test_index)

# TODO: test size is too small, maybe swap train and test or do custom implementation
# TODO: test size should be all remaining values probably, so could maybe just use a
# setdiff based on train_index to overwrite the default test_index.

# TimeSeriesSplit


# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Just a Fibonacci demonstration")
    parser.add_argument(
        "--version",
        action="version",
        version=f"$mp_time_split {__version__}",
    )
    parser.add_argument(dest="n", help="n-th Fibonacci number", type=int, metavar="INT")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formatted message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting crazy calculations...")
    print("The {}-th Fibonacci number is {}".format(args.n, fib(args.n)))
    _logger.info("Script ends here")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m mp_time_split.core 42
    #
    run()


# %% Code Graveyard
# doi_results = mpr.doi.search(nsites=nsites, elements=elements, fields=doi_fields)
# https://github.com/materialsproject/api/issues/612
# doi_results = [mpr.doi.get_data_by_id(mid) for mid in material_id]

# dict(material_id=material_id, structure=structure,
# theoretical=theoretical),
# dict(f"{field}"=)

# material_id = []
# structure = []
# theoretical = []


# material_id.append(str(r.material_id))
# structure.append(r.structure)
# theoretical.append(r.theoretical)

# mpr.provenance.search(nsites=nsites, elements=elements)

# download MP entries
# doi_fields = ["doi", "bibtex", "task_id"]


# n_compounds = df.shape[0]

# n_splits = 5
# split_type = "TimeSeriesSplit"