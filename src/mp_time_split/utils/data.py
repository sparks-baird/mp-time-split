import os
import re
from typing import List, Optional, Tuple, Union

import pandas as pd
import pybtex.errors
from mp_api import MPRester
from mp_api.core.client import DEFAULT_API_KEY
from pybtex.database.input import bibtex
from tqdm import tqdm

pybtex.errors.set_strict_mode(False)

SNAPSHOT_NAME = "mp_time_summary.json"
DUMMY_SNAPSHOT_NAME = "mp_dummy_time_summary.json"


def fetch_data(
    api_key: Union[str, DEFAULT_API_KEY] = DEFAULT_API_KEY,
    fields: Optional[List[str]] = [
        "structure",
        "material_id",
        "theoretical",
        "energy_above_hull",
        "formation_energy_per_atom",
    ],
    num_sites: Optional[Tuple[int, int]] = None,
    elements: Optional[List[str]] = None,
    use_theoretical: bool = False,
    return_both_if_experimental: bool = False,
    one_by_one: bool = False,
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
    num_sites : Tuple[int, int]
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
    >>> num_sites = (1, 52)
    >>> elements = ["V"]
    >>> expt_df = retrieve_data(api_key, num_sites=num_sites, elements=elements)

    >>> df = retrieve_data(
            api_key,
            num_sites=num_sites,
            elements=elements,
            use_theoretical=True
        )

    >>> expt_df, df = retrieve_data(
            api_key,
            num_sites=num_sites,
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
            num_sites=num_sites, elements=elements, fields=fields, **search_kwargs
        )

        if fields is not None:
            field_data = []
            for r in results:
                field_data.append({field: getattr(r, field) for field in fields})
        else:
            field_data = results

        material_id = [str(fd["material_id"]) for fd in field_data]

        # mvc values get distinguished by a negative sign
        index = [
            int(mid.replace("mp-", "").replace("mvc-", "-")) for mid in material_id
        ]
        df = pd.DataFrame(field_data, index=index)
        df = df.sort_index()

        if not use_theoretical:
            # REVIEW: whether to use MPID class or str of MPIDs?
            # if latter, `expt_df.material_id.apply(str).tolist()`
            expt_df = df.query("theoretical == False")
            expt_material_id = expt_df.material_id.tolist()

            if not one_by_one:
                # https://github.com/materialsproject/api/issues/613
                provenance_results = mpr.provenance.search(
                    fields=["references", "material_id"]
                )
                provenance_ids = [fpr.material_id for fpr in provenance_results]
                prov_df = pd.Series(
                    name="provenance", data=provenance_results, index=provenance_ids
                )
                expt_provenance_results = prov_df.loc[expt_material_id]
            else:
                # slow version
                expt_provenance_results = [
                    mpr.provenance.get_data_by_id(mid) for mid in tqdm(expt_material_id)
                ]
            # CrystalSystem not JSON serializable, see
            # https://github.com/materialsproject/api/issues/615
            # expt_df["provenance"] = expt_provenance_results

            # extract earliest ICSD year
            references = [pr.references for pr in expt_provenance_results]
            discovery = _get_discovery_dict(references)
            year = [disc["year"] for disc in discovery]
            # https://stackoverflow.com/a/35387129/13697228
            expt_df = expt_df.assign(
                references=references, discovery=discovery, year=year
            )

            expt_df = expt_df.sort_values(by=["year"])

    if use_theoretical:
        return df
    elif return_both_if_experimental:
        return expt_df, df
    else:
        return expt_df


def _get_discovery_dict(references: List[dict]) -> List[dict]:
    """Get a dictionary containing earliest bib info for each MP entry.

    Modified from source:
    "How do I do a time-split of Materials Project entries? e.g. pre-2018 vs. post-2018"
    https://matsci.org/t/42584/4?u=sgbaird, answer by @Joseph_Montoya, Materials Project Alumni

    Parameters
    ----------
    provenance_results : List[dict]
        List of references results, e.g. taken from from the ``ProvenanceRester`` API
        results (:func:`mp_api.provenance`)

    Returns
    -------
    discovery, List[dict]
        Dictionary containing earliest bib info for each MP entry with keys: ``["year",
        "authors", "num_authors"]``

    Examples
    --------
    >>> with MPRester(api_key) as mpr:
    ...     provenance_results = mpr.provenance.search(num_sites=(1, 4), elements=["V"])
    >>> discovery = get_discovery_dict(provenance_results)
    [{'year': 1963, 'authors': ['Raub, E.', 'Fritzsche, W.'], 'num_authors': 2}, {'year': 1925, 'authors': ['Becker, K.', 'Ebert, F.'], 'num_authors': 2}, {'year': 1965, 'authors': ['Giessen, B.C.', 'Grant, N.J.'], 'num_authors': 2}, {'year': 1957, 'authors': ['Philip, T.V.', 'Beck, P.A.'], 'num_authors': 2}, {'year': 1963, 'authors': ['Darby, J.B.jr.'], 'num_authors': 1}, {'year': 1977, 'authors': ['Aksenova, T.V.', 'Kuprina, V.V.', 'Bernard, V.B.', 'Skolozdra, R.V.'], 'num_authors': 4}, {'year': 1964, 'authors': ['Maldonado, A.', 'Schubert, K.'], 'num_authors': 2}, {'year': 1962, 'authors': ['Darby, J.B.jr.', 'Lam, D.J.', 'Norton, L.J.', 'Downey, J.W.'], 'num_authors': 4}, {'year': 1925, 'authors': ['Becker, K.', 'Ebert, F.'], 'num_authors': 2}, {'year': 1959, 'authors': ['Dwight, A.E.'], 'num_authors': 1}] # noqa: E501
    """
    discovery = []
    for refs in tqdm(references):
        parser = bibtex.Parser()
        refs = "".join(refs)
        refs = parser.parse_string(refs)
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
        data_home = os.environ.get(
            "MP_TIME_DATA", os.path.dirname(os.path.abspath(__file__))
        )

    data_home = os.path.expanduser(data_home)

    return data_home


# def encode_dataframe(df):
#     jsonpickle_pandas.register_handlers()
#     return jsonpickle.encode(df)


# def decode_dataframe_from_string(string):
#     jsonpickle_pandas.register_handlers()
#     return jsonpickle.decode(string, classes=[Structure])


# %% Code graveyard
