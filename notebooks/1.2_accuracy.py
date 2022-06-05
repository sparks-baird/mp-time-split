import numpy as np
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error

from mp_time_split.core import MPTimeSplit

model = DummyRegressor(strategy="mean")

mpt = MPTimeSplit(target="energy_above_hull")
mpt.load(dummy=False)

maes = []
for fold in mpt.folds:
    train_inputs, val_inputs, train_outputs, val_outputs = mpt.get_train_and_val_data(
        fold
    )
    model.fit(train_inputs, train_outputs)
    predictions = model.predict(val_inputs)
    mae = mean_absolute_error(val_outputs, predictions)
    maes.append(mae)

np.mean(maes)
