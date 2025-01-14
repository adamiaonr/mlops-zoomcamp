import pickle
import datetime
import pandas as pd

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from pathlib import Path

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from xgboost import train

from prefect import task, flow, get_run_logger
from prefect.deployments import DeploymentSpec
from prefect.orion.schemas.schedules import CronSchedule
from prefect.flow_runners import SubprocessFlowRunner

DATASET_PATH = "../data/fhv/fhv_tripdata_{year}-{month}.parquet"

def dump_pickle(obj, filename):
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)

@task
def get_paths(date:str) -> Path:
  logger = get_run_logger()

  # if date is None, take today's date
  if not date:
    date = datetime.date.today()
  else:
    date = parse(date)

  # calculate train and validation date
  train_date = date - relativedelta(months = 2)
  val_date = date - relativedelta(months = 1)
  
  # use dates to generate train and validation paths
  train_path = Path(DATASET_PATH.format(year = train_date.year, month = '{:02d}'.format(train_date.month)))
  val_path = Path(DATASET_PATH.format(year = val_date.year, month = '{:02d}'.format(val_date.month)))

  logger.info(f"{date} :\n\ttrain path: {train_path}\n\tvalidation path : {val_path}")

  return train_path, val_path

@task
def read_data(path):
    df = pd.read_parquet(path)
    return df

@task
def prepare_features(df, categorical, train=True):
    logger = get_run_logger()

    df['duration'] = df.dropOff_datetime - df.pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    mean_duration = df.duration.mean()
    if train:
        logger.info(f"The mean duration of training is {mean_duration}")
    else:
        logger.info(f"The mean duration of training is {mean_duration}")
    
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    return df

@task
def train_model(df, categorical):
    logger = get_run_logger()

    train_dicts = df[categorical].to_dict(orient='records')
    dv = DictVectorizer()
    X_train = dv.fit_transform(train_dicts) 
    y_train = df.duration.values

    logger.info(f"The shape of X_train is {X_train.shape}")
    logger.info(f"The DictVectorizer has {len(dv.feature_names_)} features")

    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_train)
    mse = mean_squared_error(y_train, y_pred, squared=False)
    logger.info(f"The MSE of training is: {mse}")
    return lr, dv

@task
def run_model(df, categorical, dv, lr):
    logger = get_run_logger()
    
    val_dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(val_dicts) 
    y_pred = lr.predict(X_val)
    y_val = df.duration.values

    mse = mean_squared_error(y_val, y_pred, squared=False)
    logger.info(f"The MSE of validation is: {mse}")
    return

@flow
def main(date:str = None):

    train_path, val_path = get_paths(date).result()

    categorical = ['PUlocationID', 'DOlocationID']

    df_train = read_data(train_path)
    df_train_processed = prepare_features(df_train, categorical)

    df_val = read_data(val_path)
    df_val_processed = prepare_features(df_val, categorical, False)

    # train the model
    lr, dv = train_model(df_train_processed, categorical).result()

    # save lr and dv
    dump_pickle(lr, f"./models/model-{date}.bin")
    dump_pickle(dv, f"./models/dv-{date}.b")

    run_model(df_val_processed, categorical, dv, lr)

DeploymentSpec(
    flow=main,
    name="homework-03",
    schedule=CronSchedule(
        cron="0 9 15 * *",
        timezone="Europe/Lisbon"),
    flow_runner=SubprocessFlowRunner(),
    tags = ['mlops-zoomcamp']
)

if __name__ == '__main__':
  main(date = "2021-08-15")
