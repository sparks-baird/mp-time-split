from mp_time_split.core import MPTimeSplit

mpt = MPTimeSplit(target="energy_above_hull")
mpt.load(dummy=False)

for fold in mpt.folds:
    train_inputs, val_inputs, train_outputs, val_outputs = mpt.get_train_and_val_data(
        fold
    )

1 + 1
