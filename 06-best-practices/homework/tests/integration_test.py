import os
import sys
import pandas as pd

from datetime import datetime
from deepdiff import DeepDiff
from pathlib import Path


def dt(year, month, hour, minute, second=0):
    return datetime(year, month, 1, hour, minute, second)


def get_mockup_data(year:int, month:int) -> pd.DataFrame:
  input_data = [
    (None, None, dt(year, month, 1, 2), dt(year, month, 1, 10)),
    (1, 1, dt(year, month, 1, 2), dt(year, month, 1, 10)),
    (1, 1, dt(year, month, 1, 2, 0), dt(year, month, 1, 2, 50)),
    (1, 1, dt(year, month, 1, 2, 0), dt(year, month, 2, 2, 1)),        
  ]
  columns = ['PUlocationID', 'DOlocationID', 'pickup_datetime', 'dropOff_datetime']

  return pd.DataFrame(input_data, columns=columns)


def main(year:int, month:int):
  # create mockup data
  data = get_mockup_data(year, month)

  # extract s3 endpoint from env variable
  s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
  if s3_endpoint_url:
    s3_options = {
      'client_kwargs': {
          'endpoint_url': s3_endpoint_url
      }
    }
  else:
    s3_options = {}

  # save mockup data to s3 {year} {month}
  s3_filename = os.getenv('INPUT_FILE_PATTERN')
  data.to_parquet(
      s3_filename.format(year=year, month=month),
      engine='pyarrow',
      compression=None,
      index=False,
      storage_options=s3_options
  )

  # call batch.py script : this should write to s3
  os.system(f'pipenv run python ../batch.py {year} {month}')

  # read output from s3
  output_file = os.getenv('OUTPUT_FILE_PATTERN')
  actual_data = pd.read_parquet(
    output_file.format(year=year, month=month),
    storage_options=s3_options)

  # print sum of predicted duration
  print(f"sum of predicted durations : {actual_data['predicted_duration'].sum()}")

  # we expect 2 records
  assert len(actual_data) == 2

  # expected data
  expected_data = [
    {'ride_id': '2021/01_0', 'predicted_duration': 23.052084934930427}, 
    {'ride_id': '2021/01_1', 'predicted_duration': 46.23661189747671}
  ]
  diff = DeepDiff(actual_data.to_dict(orient = 'records'), expected_data, significant_digits=1)
  print(f"actual vs. expected data diff.: {diff}")
  assert not diff


if __name__ == '__main__':
  # year and month passed as arguments to the script
  year = int(sys.argv[1])
  month = int(sys.argv[2])

  main(year, month)
