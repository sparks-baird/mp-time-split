from os import path

from matminer.utils.io import load_dataframe_from_json

from mp_time_split.core import MPTimeSplit
from mp_time_split.utils.data import DUMMY_SNAPSHOT_NAME, get_data_home

dummy_data_path = path.join(get_data_home(), DUMMY_SNAPSHOT_NAME)

num_sites = (1, 2)
elements = ["V"]


# def test_data_snapshot():
#     dummy_expt_df_check = load_dataframe_from_json(dummy_data_path)
#     mpt = MPTimeSplit(num_sites=(1, 2), elements=["V"])
#     dummy_expt_df = mpt.fetch_data()
#     dummy_match = dummy_expt_df.compare(dummy_expt_df_check)
#     if not dummy_match.empty:
#         raise ValueError(
#             f"dummy_expt_df and dummy_expt_df_check unmatched: {dummy_match}"
#         )


def test_data_snapshot_one_by_one():
    dummy_expt_df_check = load_dataframe_from_json(dummy_data_path)
    mpt = MPTimeSplit(num_sites=num_sites, elements=elements)
    dummy_expt_df = mpt.fetch_data(one_by_one=True)
    dummy_match = dummy_expt_df.compare(dummy_expt_df_check)
    if not dummy_match.empty:
        raise ValueError(
            f"dummy_expt_df and dummy_expt_df_check unmatched: {dummy_match}"
        )


def test_get_train_and_val_data():
    mpt = MPTimeSplit(num_sites=num_sites, elements=elements)
    mpt.fetch_data(one_by_one=True)
    train_inputs = []
    val_inputs = []
    train_outputs = []
    val_outputs = []
    for fold in mpt.folds:
        train_input, val_input, train_output, val_output = mpt.get_train_and_val_data(
            fold
        )
        train_inputs.append(train_input)
        val_inputs.append(val_input)
        train_outputs.append(train_output)
        val_outputs.append(val_output)
    return train_inputs, val_inputs, train_outputs, val_outputs


def test_get_test_data():
    mpt = MPTimeSplit(num_sites=num_sites, elements=elements)
    mpt.fetch_data(one_by_one=True)
    train_inputs, test_inputs, train_outputs, test_outputs = mpt.get_test_data()
    return train_inputs, test_inputs, train_outputs, test_outputs


def test_load():
    mpt = MPTimeSplit(num_sites=num_sites, elements=elements)
    data = mpt.load(dummy=True)
    return data


if __name__ == "__main__":
    # test_data_snapshot()
    test_data_snapshot_one_by_one()
    data = test_load()
    train_inputs, val_inputs, train_outputs, val_outputs = test_get_train_and_val_data()
    train_inputs, test_inputs, train_outputs, test_outputs = test_get_test_data()
    data
