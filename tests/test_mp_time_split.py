from mp_time_split.core import MPTimeSplit


def test_get_train_and_val_data():
    mpt = MPTimeSplit(num_sites=(1, 2), elements=["V"])
    mpt.fetch_data()
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
    mpt = MPTimeSplit(num_sites=(1, 2), elements=["V"])
    mpt.fetch_data()
    train_inputs, test_inputs, train_outputs, test_outputs = mpt.get_test_data()
    return train_inputs, test_inputs, train_outputs, test_outputs


if __name__ == "__main__":
    train_inputs, val_inputs, train_outputs, val_outputs = test_get_train_and_val_data()
    train_inputs, test_inputs, train_outputs, test_outputs = test_get_test_data()
    train_inputs
