from os import path

import jsonpickle
import jsonpickle.ext.pandas as jsonpickle_pandas
from monty.io import zopen

from mp_time_split.core import MPTimeSplit
from mp_time_split.utils.data import DUMMY_SNAPSHOT_NAME, _get_data_home

jsonpickle_pandas.register_handlers()
# %% dummy data
mpt = MPTimeSplit(nsites=(1, 2), elements=["V"])
dummy_expt_df = mpt.fetch_data()
dummy_data_path = path.join(_get_data_home(), DUMMY_SNAPSHOT_NAME)

with zopen(dummy_data_path, "w") as f:
    f.write(jsonpickle.encode(dummy_expt_df))

# %% full data
mpt = MPTimeSplit(nsites=(1, 52))
expt_df = mpt.fetch_data()
data_path = path.join(_get_data_home(), DUMMY_SNAPSHOT_NAME)
with zopen(dummy_data_path, "w") as f:
    f.write(jsonpickle.encode(dummy_expt_df))
1 + 1


# %% Code Graveyard
# expt_df.to_json()
# store_dataframe_as_json(expt_df, data_path, compression="gz")
# with zopen(data_path, "wb") as f:
#     data = json.dumps(expt_df.to_json()).encode()
#     f.write(data)
