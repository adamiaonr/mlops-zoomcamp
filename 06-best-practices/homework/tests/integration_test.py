import pandas as pd

from datetime import datetime

import batch
from test_batch import dt

input_data = [
  (None, None, dt(1, 2), dt(1, 10)),
  (1, 1, dt(1, 2), dt(1, 10)),
  (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
  (1, 1, dt(1, 2, 0), dt(2, 2, 1)),        
]
columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
data = pd.DataFrame(input_data, columns=columns)

input_file = batch.get_input_path(2021, 1)
options = batch.get_s3_options()

data.to_parquet(
    input_file,
    engine='pyarrow',
    compression=None,
    index=False,
    storage_options=batch.get_s3_options()
)
