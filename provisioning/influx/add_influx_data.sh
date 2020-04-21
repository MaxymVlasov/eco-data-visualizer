#!/usr/bin/env bash

# Start influxdb
/entrypoint.sh influxd &


sleep 1

# Import user data
DATA_PATH=/influx-data/
FILES=$(ls "$DATA_PATH" | grep influx)

for file in ${FILES}; do
    echo -e "\nImport data from $file"
    influx -host influxdb -import -path=${DATA_PATH}/${file} -precision=ns
done
