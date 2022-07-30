#!/usr/bin/env bash

# setup script variables
YEAR=2021
MONTH=1

# cd to script's dir
cd "$(dirname "$0")"

# setup environment variables
export MODEL_LOCATION="$( cd .. && pwd )"
export S3_ENDPOINT_URL="http://localhost:4566"
export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
# - 'bogus' aws access keys to access localstack s3 bucket
export AWS_ACCESS_KEY_ID=foobar
export AWS_SECRET_ACCESS_KEY=foobar

# start localstack
cd ..
docker-compose up localstack --remove-orphans -d
sleep 3

# cd to tests/ folder again
cd tests

# create s3 bucket on localstack
aws --endpoint-url=http://localhost:4566 s3 mb s3://nyc-duration

# run integration test for {YEAR, MONTH}
pipenv run python integration_test.py $YEAR $MONTH

# cleanup
cd ..
docker-compose down

exit 0
