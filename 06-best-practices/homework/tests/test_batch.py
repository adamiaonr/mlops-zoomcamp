import pandas as pd

from datetime import datetime
from pandas.testing import assert_frame_equal

import batch

def dt(hour, minute, second=0):
    return datetime(2021, 1, 1, hour, minute, second)

def test_prepare_data():
  input_data = [
    (None, None, dt(1, 2), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, 1, dt(1, 2, 0), dt(1, 2, 50)),
    (1, 1, dt(1, 2, 0), dt(2, 2, 1)),        
  ]
  columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']
  data = pd.DataFrame(input_data, columns=columns)

  actual_res = batch.prepare_data(data, categorical=['PUlocationID', 'DOlocationID'])
  expected_res = pd.DataFrame(
    [
      {
        'PUlocationID' : '-1',
        'DOlocationID' : '-1',
        'pickup_datetime' : dt(1, 2),
        'dropOff_datetime' : dt(1, 10),
        'duration' : 8.0
      },
      {
        'PUlocationID' : '1',
        'DOlocationID' : '1',
        'pickup_datetime' : dt(1, 2),
        'dropOff_datetime' : dt(1, 10),
        'duration' : 8.0
      }
    ]
  )

  assert_frame_equal(actual_res, expected_res)
