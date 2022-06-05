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
from hashlib import md5
from os import environ, path
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd
import pybtex.errors
from matminer.utils.io import load_dataframe_from_json

from mp_time_split import __version__
from mp_time_split.utils.data import DUMMY_SNAPSHOT_NAME, SNAPSHOT_NAME
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
dummy_checksum_frozen = "6bf42266bd71477a06b24153d4ff7889"
full_checksum_frozen = "57da7fa4d96ffbbc0dd359b1b7423f31"


def get_data_home(data_home=None):
    """
    Selects the home directory to look for datasets, if the specified home
    directory doesn't exist the directory structure is built

    Modified from source:
    https://github.com/hackingmaterials/matminer/blob/76a529b769055c729d62f11a419d319d8e2f838e/matminer/datasets/utils.py#L26-L43 # noqa:E501

    Args:
        data_home (str): folder to look in, if None a default is selected

    Returns (str)
    """

    # If user doesn't specify a dataset directory: first check for env var,
    # then default to the "matminer/datasets/" package folder
    if data_home is None:
        data_home = environ.get(
            "MP_TIME_DATA", path.join(path.dirname(path.abspath(__file__)), "utils")
        )

    data_home = path.expanduser(data_home)

    return data_home


class MPTimeSplit:
    def __init__(
        self,
        num_sites=None,
        elements=None,
        use_theoretical=False,
        mode="TimeSeriesSplit",
        target="energy_above_hull",
    ) -> None:
        if mode not in AVAILABLE_MODES:
            raise NotImplementedError(
                f"mode={mode} not implemented. Use one of {AVAILABLE_MODES}"
            )

        self.num_sites = num_sites
        self.elements = elements
        self.use_theoretical = use_theoretical
        self.mode = mode
        self.folds = FOLDS

        self.target = target

    def fetch_data(self, one_by_one=False):
        try:
            from mp_time_split.utils.api import fetch_data
        except ImportError as e:
            print(e)
            print(
                "Failed to import `fetch_data()`. Try `pip install mp_time_split[api]` or `pip install mp-api` to install the optional `mp-api` dependency. Note that this requires Python >=3.8"  # noqa: E501
            )

        self.data = fetch_data(
            num_sites=self.num_sites,
            elements=self.elements,
            use_theoretical=self.use_theoretical,
            one_by_one=one_by_one,
        )
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("`self.data` is not a `pd.DataFrame`")

        self.trainval_splits, self.test_split = mp_time_split(
            self.data, n_cv_splits=len(FOLDS), mode=self.mode
        )
        self.inputs = self.data.structure
        self.outputs = getattr(self.data, self.target)
        return self.data

    def load(self, url=None, checksum=None, dummy=False, force_download=False):
        name = SNAPSHOT_NAME if not dummy else DUMMY_SNAPSHOT_NAME
        name = name + ".gz"
        data_path = path.join(get_data_home(), name)

        is_on_disk = Path(data_path).is_file()

        if force_download or not is_on_disk:
            if dummy and url is None and checksum is None:
                # dummy data from figshare for testing
                url = "https://figshare.com/ndownloader/files/35592005"
                checksum_frozen = dummy_checksum_frozen
            elif not dummy and url is None and checksum is None:
                # full dataset from figshare for production
                url = "https://figshare.com/ndownloader/files/35592011"
                checksum_frozen = full_checksum_frozen
            elif url is None:
                raise ValueError(
                    f"url should not be None at this point. url: {url}, type: {type(url)}"  # noqa: E501
                )
            else:
                checksum_frozen = None

            urlretrieve(url, data_path)
        else:
            checksum_frozen = None

        checksum = md5(Path(data_path).read_bytes()).hexdigest()

        if checksum_frozen is not None and checksum != checksum_frozen:
            raise ValueError(
                f"checksum from {url} ({checksum}) does not match what was expected {checksum_frozen})"  # noqa: E501
            )

        expt_df = load_dataframe_from_json(data_path)
        self.data = expt_df
        self.trainval_splits, self.test_split = mp_time_split(
            self.data, n_cv_splits=len(FOLDS), mode=self.mode
        )
        self.inputs = self.data.structure
        self.outputs = getattr(self.data, self.target)

        return self.data

    def get_train_and_val_data(self, fold):
        if self.data is None:
            raise NameError("`fetch_data()` must be run first.")
        if fold not in FOLDS:
            raise ValueError(f"fold={fold} should be one of {FOLDS}")

        # self.y = self.data[]
        train_inputs, val_inputs = [
            self.inputs.iloc[tvs] for tvs in self.trainval_splits[fold]
        ]
        train_outputs, val_outputs = [
            self.outputs.iloc[tvs] for tvs in self.trainval_splits[fold]
        ]
        return train_inputs, val_inputs, train_outputs, val_outputs

    def get_test_data(self):
        if self.data is None:
            raise NameError("`fetch_data()` must be run first.")

        train_inputs, test_inputs = [self.inputs.iloc[ts] for ts in self.test_split]
        train_outputs, test_outputs = [self.outputs.iloc[ts] for ts in self.test_split]

        return train_inputs, test_inputs, train_outputs, test_outputs


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

# load_dataframe_from_json(data_path)
# with zopen(data_path, "rb") as f:
#     self.data = pd.DataFrame.read_json(json.load(f))

# with zopen(data_path, "r") as f:
#     expt_df = jsonpickle.decode(f.read())

# with urlopen("test.com/csv?date=2019-07-17") as f:
#     jsonl = f.read().decode('utf-8')
# data_home = environ.get("MP_TIME_DATA", path.dirname(path.abspath(__file__)))

# with open(data_path, "r") as f:
#     expt_df = jsonpickle.decode(f.read())
