# %pip install pyxtal
from mp_time_split.core import MPTimeSplit
from mp_time_split.utils.gen import DummyGenerator

mpt = MPTimeSplit(target="energy_above_hull")
mpt.load(dummy=True)

for fold in mpt.folds:
    train_inputs, val_inputs, train_outputs, val_outputs = mpt.get_train_and_val_data(
        fold
    )
    dg = DummyGenerator()
    dg.fit(train_inputs)
    generated_structures = dg.gen(n=100)
    # compare generated_structures and val_inputs
    # some_code_here

1 + 1
