#!/usr/bin/env python
# coding: utf-8

import sys
import os
import pickle
import pandas as pd

def load_model(model_path:str):
  with open(model_path, 'rb') as f_in:
      dv, lr = pickle.load(f_in)  
  return dv, lr

def __extract_year_month(filename) -> tuple[str, str]:
  return filename.split('_')[-1].split('-')[0], filename.split('_')[-1].split('-')[1].replace('.parquet', '')

def read_data(filename):
    df = pd.read_parquet(filename)
    # add a 'ride id' column to uniquely identify a ride
    year, month = __extract_year_month(filename)
    df['ride_id'] = f'{year}/{month}_' + df.index.astype('str')
    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    return df

def prepare_dictionaries(data: pd.DataFrame, categorical:list = ['PUlocationID', 'DOlocationID']):
  data[categorical] = data[categorical].fillna(-1).astype('int').astype('str')
  dicts = data[categorical].to_dict(orient='records')
  return dicts

def save_results(data:pd.DataFrame, predictions, output_file:str):
    df_result = pd.DataFrame(
      {
        'ride_id' : data['ride_id'].values,
        'predicted_duration' : predictions
      }
    )

    df_result.to_parquet(
      output_file,
      engine='pyarrow',
      compression=None,
      index=False
    )

def apply_model(input_file:str, model_path:str, output_file:str):
  df = read_data(input_file)
  dv, lr = load_model(model_path)
  dicts = prepare_dictionaries(df)
  X_val = dv.transform(dicts)

  y_pred = lr.predict(X_val)
  print(f'inference completed (avg. predicted duration: {y_pred.mean()})')

  save_results(df, y_pred, output_file)
  print(f'saved results in file {output_file} ({os.path.getsize(output_file) / 1024**2} MB)...')

def run():
  taxi_type = sys.argv[1]
  year      = int(sys.argv[2])
  month     = int(sys.argv[3])

  # input file (downloaded directly from NYC taxi dataset website)
  input_file = f'https://nyc-tlc.s3.amazonaws.com/trip+data/fhv_tripdata_{year:04d}-{month:02d}.parquet'
  output_file = f'./{taxi_type}/{year:04d}-{month:02d}.parquet'
  model_path = './model.bin'

  apply_model(input_file, model_path, output_file)

if __name__ == "__main__":
  run()
