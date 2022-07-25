#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pickle
import typing
import pandas as pd

from pathlib import Path

def prepare_data(data:pd.DataFrame, categorical:list[str]) -> pd.DataFrame:
    data['duration'] = data.dropOff_datetime - data.pickup_datetime
    data['duration'] = data.duration.dt.total_seconds() / 60
    data = data[(data.duration >= 1) & (data.duration <= 60)].copy()
    data[categorical] = data[categorical].fillna(-1).astype('int').astype('str')
    
    return data

def read_data(filename:typing.Union[str, Path], categorical:list[str], options:dict = {}) -> pd.DataFrame:
    df = pd.read_parquet(filename, storage_options=options)

    return prepare_data(df, categorical)

def get_s3_options() -> dict:
  s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')
  if s3_endpoint_url:
    options = {
        'client_kwargs': {
            'endpoint_url': s3_endpoint_url
        }
    }
  else:
    options = {}

  return options

def get_input_path(year:int, month:int) -> str:
  default_pattern = 'https://raw.githubusercontent.com/alexeygrigorev/datasets/master/nyc-tlc/fhv/fhv_tripdata_{year:04d}-{month:02d}.parquet'
  pattern = os.getenv('INPUT_FILE_PATTERN', default_pattern)

  return pattern.format(year=year, month=month)

def get_output_path(year:int, month:int) -> str:
  default_pattern = 's3://nyc-duration-prediction-alexey/taxi_type=fhv/year={year:04d}/month={month:02d}/predictions.parquet'
  pattern = os.getenv('OUTPUT_FILE_PATTERN', default_pattern)

  return pattern.format(year=year, month=month)

def main(year:int, month:int):
  input_file = get_input_path(year, month)
  output_file = get_output_path(year, month)
  
  with open('model.bin', 'rb') as f_in:
      dv, lr = pickle.load(f_in)

  categorical = ['PUlocationID', 'DOlocationID']

  df = read_data(input_file, categorical, get_s3_options())
  df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

  dicts = df[categorical].to_dict(orient='records')
  X_val = dv.transform(dicts)
  y_pred = lr.predict(X_val)

  print('predicted mean duration:', y_pred.mean())

  df_result = pd.DataFrame()
  df_result['ride_id'] = df['ride_id']
  df_result['predicted_duration'] = y_pred

  df_result.to_parquet(output_file, engine='pyarrow', index=False)

if __name__ == '__main__':
  # year and month passed as arguments to the script
  year = int(sys.argv[1])
  month = int(sys.argv[2])

  main(year, month)
