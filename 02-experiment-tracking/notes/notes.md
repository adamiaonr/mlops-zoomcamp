# 02 : Experiment Tracking Notes

These instructions show how to run an MLflow server from any directory in your system. The advantages are:

1. You're not forced to run MLflow server in the same folder as you run the actual code for training, testing, etc.
2. The data from different experiments - both backend store data (parameters, tags, metrics, etc.) and artifacts - is kept in a common location, allowing you to browse through different experiments in the MLflow UI.

## Setup common location for MLflow metadata

Open a terminal and run the following command.

```
export MLFLOW_PATH="${HOME}/mlflow_data"
```

In order to make the environment variable 'permanent', you can append the same command to your `~/.bashrc` file.

```
# adding env variable for mlflow db location
export MLFLOW_PATH="${HOME}/mlflow_data"
```

The above will set the `MLFLOW_PATH` variable whenever you open the terminal or whenever you run the command below:

```
$ source ~/.bashrc
```

## Start MLflow server

Start an MLflow server anywhere, passing the `MLFLOW_PATH` as the prefix for the backend and artifact stores, e.g.:

```
$ mlflow server --backend-store-uri sqlite:///$MLFLOW_PATH/mlflow.db --default-artifact-root $MLFLOW_PATH/artifacts
```

## Why does this work?

When a new experiment is **created** via the `mlflow.set_experiment()` call in your code, it will use the default artifact store location of the MLflow server (i.e., the one which we've specified via the `--default-artifact-root` option).
This is mentioned in the MLflow documentation [[1]](https://www.mlflow.org/docs/latest/tracking.html#artifact-stores):

> Use --default-artifact-root (defaults to local ./mlruns directory) to configure default location to server’s artifact store. **This will be used as artifact location for newly-created experiments that do not specify one. Once you create an experiment, --default-artifact-root is no longer relevant to that experiment.**

## References

[[1]](https://www.mlflow.org/docs/latest/tracking.html#artifact-stores) MLflow Tracking, Storage, Artifact store
