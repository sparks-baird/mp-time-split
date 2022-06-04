from os import path

import jsonpickle
import jsonpickle.ext.pandas as jsonpickle_pandas

from mp_time_split.core import MPTimeSplit
from mp_time_split.utils.data import DUMMY_SNAPSHOT_NAME, _get_data_home

jsonpickle_pandas.register_handlers()
# https://stackoverflow.com/a/4359298/13697228
# jsonpickle.set_encoder_options("json", sort_keys=True, indent=4)
# %% dummy data
mpt = MPTimeSplit(num_sites=(1, 2), elements=["V"])
dummy_expt_df = mpt.fetch_data()
dummy_data_path = path.join(_get_data_home(), DUMMY_SNAPSHOT_NAME)

with open(dummy_data_path, "w") as f:
    f.write(jsonpickle.encode(dummy_expt_df))

with open(dummy_data_path, "r") as f:
    dummy_expt_df_check = jsonpickle.decode(f.read())

# %% full data
mpt = MPTimeSplit(num_sites=(1, 52))
expt_df = mpt.fetch_data()
data_path = path.join(_get_data_home(), DUMMY_SNAPSHOT_NAME)
with open(dummy_data_path, "w") as f:
    f.write(jsonpickle.encode(dummy_expt_df))
1 + 1


# %% Code Graveyard
# expt_df.to_json()
# store_dataframe_as_json(expt_df, data_path, compression="gz")
# with zopen(data_path, "wb") as f:
#     data = json.dumps(expt_df.to_json()).encode()
#     f.write(data)
