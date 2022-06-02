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
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import pybtex.errors
from emmet.core.provenance import ProvenanceDoc
from mp_api import MPRester
from mp_api.core.client import DEFAULT_API_KEY
from pybtex.database.input import bibtex
from sklearn.model_selection import TimeSeriesSplit
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
# doi_fields = ["doi", "bibtex", "task_id"]
nsites = (1, 4)
elements = ["V"]
use_theoretical = False


def get_discovery_dict(provenance_results: List[ProvenanceDoc]) -> List[dict]:
    """Get a dictionary containing earliest bib info for each MP entry.

    Modified from source:
    "How do I do a time-split of Materials Project entries? e.g. pre-2018 vs. post-2018"
    https://matsci.org/t/42584/4?u=sgbaird, answer by @Joseph_Montoya, Materials Project Alumni

    Parameters
    ----------
    provenance_results : List[ProvenanceDoc]
        List of results from the ``ProvenanceRester`` API (:func:`mp_api.provenance`)

    Returns
    -------
    discovery, List[dict]
        Dictionary containing earliest bib info for each MP entry with keys: ``["year",
        "authors", "num_authors"]``

    Examples
    --------
    >>> with MPRester(api_key) as mpr:
    ...     provenance_results = mpr.provenance.search(nsites=(1, 4), elements=["V"])
    >>> discovery = get_discovery_dict(provenance_results)
    [{'year': 1963, 'authors': ['Raub, E.', 'Fritzsche, W.'], 'num_authors': 2}, {'year': 1925, 'authors': ['Becker, K.', 'Ebert, F.'], 'num_authors': 2}, {'year': 1965, 'authors': ['Giessen, B.C.', 'Grant, N.J.'], 'num_authors': 2}, {'year': 1957, 'authors': ['Philip, T.V.', 'Beck, P.A.'], 'num_authors': 2}, {'year': 1963, 'authors': ['Darby, J.B.jr.'], 'num_authors': 1}, {'year': 1977, 'authors': ['Aksenova, T.V.', 'Kuprina, V.V.', 'Bernard, V.B.', 'Skolozdra, R.V.'], 'num_authors': 4}, {'year': 1964, 'authors': ['Maldonado, A.', 'Schubert, K.'], 'num_authors': 2}, {'year': 1962, 'authors': ['Darby, J.B.jr.', 'Lam, D.J.', 'Norton, L.J.', 'Downey, J.W.'], 'num_authors': 4}, {'year': 1925, 'authors': ['Becker, K.', 'Ebert, F.'], 'num_authors': 2}, {'year': 1959, 'authors': ['Dwight, A.E.'], 'num_authors': 1}] # noqa: E501
    """
    discovery = []
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
            first_report["authors"] = [str(auth) for auth in first_report["authors"]]
            first_report["num_authors"] = len(first_report["authors"])
            discovery.append(first_report)
        else:
            discovery.append(dict(year=None, authors=None, num_authors=None))
    return discovery


def retrieve_data(
    api_key: Union[str, DEFAULT_API_KEY] = DEFAULT_API_KEY,
    fields: Optional[List[str]] = ["structure", "material_id", "theoretical"],
    nsites: Optional[Tuple[int, int]] = None,
    elements: Optional[List[str]] = None,
    use_theoretical: bool = False,
    return_both_if_experimental: bool = False,
    **search_kwargs,
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame]]:
    """Retrieve MP data sorted by MPID (theoretical+exptl) or pub year (exptl).

    See `*How do I do a time-split of Materials Project entries? e.g. pre-2018 vs.
    post-2018* <https://matsci.org/t/42584>`_

    Output ``DataFrame``-s will contain all specified `fields` unless ``fields is
    None``, in which case all :func:`MPRester().summary.available_fields` will be
    returned. If return experimental data, the additional fields of ``provenance``,
    ``discovery`` and ``year`` corresponding to
    :func:`emmet.core.provenance.ProvenanceDoc`, a dictionary containing earliest year
    and author information, and the earliest year, respectively, will also be returned.

    Parameters
    ----------
    api_key : Union[str, DEFAULT_API_KEY]
        :func:`mp_api` API Key. On Windows, can set as an environment variable via:
        ``setx MP_API_KEY="abc123def456"``. By default:
        :func:`mp_api.core.client.DEFAULT_API_KEY`
        See also:
         https://github.com/materialsproject/api/issues/566#issuecomment-1087941474
    fields : Optional[List[str]]
        fields (List[str]): List of fields to project. When searching, it is better to
        only ask for the specific fields of interest to reduce the time taken to
        retrieve the documents. See the :func:`MPRester().summary.available_fields`
        property to see a list of fields to choose from. By default:
        ``["structure", "material_id", "theoretical"]``.
    nsites : Tuple[int, int]
        Tuple of min and max number of sites used as filtering criteria, e.g. ``(1,
        52)`` meaning at least ``1`` and no more than ``52`` sites. If ``None`` then no
        compounds with any number of sites are allowed. By default None.
    elements : List[str]
        List of element symbols, e.g. ``["Ni", "Fe"]``. If ``None`` then all elements
        are allowed. By default None.
    use_theoretical : bool, optional
        Whether to include both theoretical and experimental compounds or to filter down
        to only experimentally-verified compounds, by default False
    return_both_if_experimental : bool, optional
        Whether to return both the full DataFrame containing theoretical+experimental
        (`df`) and the experimental-only DataFrame (`expt_df`) or only `expt_df`, by
        default False. This is only applicable if `use_theoretical` is False.
    search_kwargs : dict, optional
        kwargs: Supported search terms, e.g. nelements_max=3 for the "materials" search
        API. Consult the specific API route for valid search terms,
        i.e. :func:`MPRester().summary.available_fields`

    Returns
    -------
    df : pd.DataFrame
        if `use_theoretical` then returns a DataFrame containing both theoretical and
        experimental compounds.
    expt_df, df : Tuple[pd.DataFrame, pd.DataFrame]
        if not `use_theoretical` and `return_both_if_experimental, then returns two
        :func:`pd.DataFrame`-s containing theoretical+experimental and
        experimental-only.
    expt_df : pd.DataFrame
        if not `use_theoretical` and not `return_both_if_experimental`, then returns a
        :func:`pd.DataFrame` containing the experimental-only compounds.

    Examples
    --------
    >>> api_key = "abc123def456"
    >>> nsites = (1, 52)
    >>> elements = ["V"]
    >>> expt_df = retrieve_data(api_key, nsites=nsites, elements=elements)

    >>> df = retrieve_data(
            api_key,
            nsites=nsites,
            elements=elements,
            use_theoretical=True
        )

    >>> expt_df, df = retrieve_data(
            api_key,
            nsites=nsites,
            elements=elements,
            use_theoretical=False,
            return_both_if_experimental
        )
    """
    if fields is not None:
        if "material_id" not in fields:
            fields.append("material_id")
        if not use_theoretical and "theoretical" not in fields:
            fields.append("theoretical")

    with MPRester(api_key) as mpr:
        results = mpr.summary.search(
            nsites=nsites, elements=elements, fields=fields, **search_kwargs
        )

        if fields is not None:
            field_data = []
            for r in results:
                field_data.append({field: getattr(r, field) for field in fields})
        else:
            field_data = results

        material_id = [fd["material_id"] for fd in field_data]

        index = [int(mid.replace("mp-", "")) for mid in material_id]
        df = pd.DataFrame(field_data, index=index)
        df = df.sort_index()

        if not use_theoretical:
            expt_df = df.query("theoretical == False")
            expt_material_id = expt_df.material_id.tolist()
            # mpr.provenance.search(task_ids=expt_material_id)
            # https://github.com/materialsproject/api/issues/613
            provenance_results = [
                mpr.provenance.get_data_by_id(mid) for mid in tqdm(expt_material_id)
            ]
            expt_df["provenance"] = provenance_results

            # extract earliest ICSD year
            discovery = get_discovery_dict(provenance_results)
            year = [disc["year"] for disc in discovery]
            expt_df["discovery"] = discovery
            expt_df["year"] = year

            expt_df = expt_df.sort_values(by=["year"])

    if use_theoretical:
        return df
    elif return_both_if_experimental:
        return expt_df, df
    else:
        return expt_df


df = retrieve_data(nsites=nsites, elements=elements, use_theoretical=use_theoretical)

assert isinstance(df, pd.DataFrame), "`df` is not a `pd.DataFrame`"
tscv = TimeSeriesSplit(gap=0, n_splits=5, test_size=int(np.floor(0.8 * df.shape[0])))
for train_index, test_index in tscv.split(df):
    print("TRAIN:", train_index, "TEST:", test_index)

# TODO: test size is too small, make swap train and test or do custom implementation
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
