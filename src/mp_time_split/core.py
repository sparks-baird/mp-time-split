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
import re
import sys
from typing import List

import pandas as pd
import pybtex.errors
from mp_api import MPRester
from mp_api.core.client import DEFAULT_API_KEY
from pybtex.database.input import bibtex
from tqdm import tqdm

from mp_time_split import __version__

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


# download MP entries
api_key = DEFAULT_API_KEY
fields = ["structure", "material_id", "theoretical"]
doi_fields = ["doi", "bibtex", "task_id"]
nsites = (1, 2)
elements = ["V"]
use_theoretical = False
with MPRester(api_key) as mpr:
    results = mpr.summary.search(nsites=nsites, elements=elements, fields=fields)

    material_id = []
    structure = []
    theoretical = []

    for r in results:
        material_id.append(str(r.material_id))
        structure.append(r.structure)
        theoretical.append(r.theoretical)

    index = [int(mid.replace("mp-", "")) for mid in material_id]
    df = pd.DataFrame(
        dict(material_id=material_id, structure=structure, theoretical=theoretical),
        index=index,
    )

    if not use_theoretical:
        expt_df = df.query("theoretical == False")
        expt_material_id = expt_df.material_id.tolist()
        # mpr.provenance.search(nsites=nsites, elements=elements)
        # https://github.com/materialsproject/api/issues/613
        provenance_results = [
            mpr.provenance.get_data_by_id(mid) for mid in tqdm(expt_material_id)
        ]

        # extract earliest ICSD year
        discovery: List[dict] = []
        for pr in tqdm(provenance_results):
            parser = bibtex.Parser()
            references = "".join(pr.references)
            refs = parser.parse_string(references)
            entries = refs.entries
            entries_by_year = [
                (int(entry.fields["year"]), entry)
                for _, entry in entries.items()
                if "year" in entry.fields and re.match(r"\d{4}", entry.fields["year"])
            ]
            if entries_by_year:
                entries_by_year = sorted(entries_by_year, key=lambda x: x[0])
                first_report = {
                    "year": entries_by_year[0][0],
                    "authors": entries_by_year[0][1].persons["author"],
                }
                first_report["authors"] = [
                    str(auth) for auth in first_report["authors"]
                ]
                first_report["num_authors"] = len(first_report["authors"])
                discovery.append(first_report)
            else:
                discovery.append(dict(year=None, authors=None, num_authors=None))

        year = [disc["year"] for disc in discovery]

        expt_df["discovery"] = discovery
        expt_df["year"] = year


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
