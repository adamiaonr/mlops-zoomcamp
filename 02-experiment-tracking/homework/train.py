import argparse
import os
import pickle
import mlflow

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


def run(data_path):

    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_valid, y_valid = load_pickle(os.path.join(data_path, "valid.pkl"))

    rf = RandomForestRegressor(max_depth=10, random_state=0)

    # start an mlflow experiment run run : what does mlflow keep track of?
    with mlflow.start_run():
      # this enables automatic logging of experiment data
      mlflow.autolog()
      rf.fit(X_train, y_train)
      y_pred = rf.predict(X_valid)

      rmse = mean_squared_error(y_valid, y_pred, squared=False)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_path",
        default="./output",
        help="the location where the processed NYC taxi trip data was saved."
    )
    args = parser.parse_args()

    # set uri of backend used to save ml experiment data
    #mlflow.set_tracking_uri("sqlite:///../../data/mlflow/mlflow.db")
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    # set name of experiment (if non-existent in backend, mlflow creates it)
    mlflow.set_experiment("homework_2_experiment")

    run(args.data_path)
