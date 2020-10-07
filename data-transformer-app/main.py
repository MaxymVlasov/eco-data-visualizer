#!/usr/bin/env python3
"""
Data-transformer-app.

1. Grub CSV files located in ./data/original_data folder with
    SaveEcoBot structure (device_id,phenomenon,value,logged_at,value_text).
2. Separate CSV files per device_id and sensor type (phenomenon)
    and write result to ./data/csv/*.csv files.
3. Transform data from ./data/csv to InfluxDB format
    and write result to ./data/influx/*.influx files.

Recommended way to run:
    docker build -t data-transformer ./data-transformer-app
    docker run -v $PWD/data/:/app/data/ --rm data-transformer
"""
import csv
import errno
import logging
import sys
import time
from datetime import datetime
from os import listdir

import configs as conf
import pandas as pd

try:
    from typeguard import typechecked  # noqa: WPS433
except ModuleNotFoundError:
    def typechecked(func=None):  # noqa: WPS440
        """Skip runtime type checking on the function arguments."""
        return func
else:
    from types import MappingProxyType  # noqa: WPS433 pylint: disable=unused-import


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logs = logging.StreamHandler(sys.stdout)
logger.addHandler(logs)


#######################################################################
#                          F U N C T I O N S                          #
#######################################################################


@typechecked
def process_chunk_rows(
    dataframe: pd.core.frame.DataFrame,
    filename: str,
    sensor: str,
):
    """Split sensors data to separate file and sort it.

    Args:
        dataframe: (pandas.core.frame.DataFrame) Data chunk from CSV file.
        filename: (str) Filename of processed file.
        sensor: (str) Sensor name what will be proccessed.
    """
    dataframe.loc[
        # Choose only rows where with 'phenomenon' colum == sensor name
        dataframe['phenomenon'] == sensor
    ].sort_values(
        by=['logged_at'],
        # Make valid numbers for data sheets
    ).to_csv(
        # Name file as sensor name
        f'data/csv/{filename}.csv',
        # Save only time and value
        columns=['device_id', 'logged_at', 'value'],
        # Don't wrote doc num colum
        index=False,
        # Don't wrote header name - it writes on each DataFrame Iteration
        header=False,
        # Append data to file
        mode='a',
    )


@typechecked
def remove_duplicate_rows(filename: str, extention: str = '.csv'):
    """Remove duplicate rows from provided file.

    Args:
        filename: (str) Filename of processed file.
        extention (str): File extention. Default to ".csv"
    """
    with open(f'data/csv/{filename}{extention}', 'r+') as csv_file:
        # Get unique rows
        lines = set(csv_file.readlines())
        # Cleanup file
        csv_file.seek(0)
        csv_file.truncate()
        # Write unique rows
        csv_file.writelines(lines)


@typechecked
def write_influx_data(filename: str, collection: set):
    """Append file with data in InfluxDB format.

    Args:
        filename: (str) Filename.
        collection: (set) Data for file append.
    """
    with open(f'data/influx/{filename}.influx', mode='a') as influx_file:
        influx_file.writelines(element for element in collection)


@typechecked
def find_csv_filenames(path_to_dir: str, suffix: str = '.csv'):
    """Find all files with specified extention.

    Args:
        path_to_dir (str): Path to dir where files where to look for files
        suffix (str): File extention. Default to ".csv"
    Returns:
        array
    """
    filenames = listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


@typechecked
def calculate_aqi(aqi: 'MappingProxyType[str, dict]', sensor: str, concentration: float) -> int:
    """Calculate Air Quality Index.

    Calculations based on:
    https://www.airnow.gov/sites/default/files/2018-05/aqi-technical-assistance-document-may2016.pdf

    Args:
        aqi: (MappingProxyType[str, dict]) Nested dictionary with values for AQI calculation.
        sensor: (str) Sensor name for which it will AQI count.
        concentration: (float) Raw data from sensor.

    Returns:
        int: Air Quality Index value.

    """
    for upper_bound, _ in aqi[sensor].items():
        if concentration < float(upper_bound):
            aqi_value = (
                (_['aqi_high'] - _['aqi_low'])
                / (_['pollutant_high'] - _['pollutant_low'])
                * (concentration - _['pollutant_low'])
                + _['aqi_low']
            )
            break

    return round(aqi_value)


@typechecked
def transform_date_to_nanoseconds(date) -> int:
    """Get date from string and return it in UNIX nanoseconds format.

    Args:
        date: (str) Datetime string in `%Y-%m-%d %H:%M:%S` format.

    Returns:
        int: Date in UNIX nanoseconds.
    """
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timetuple()  # noqa: WPS323
    date = time.mktime(date) * 10 ** 9

    return int(date)


#######################################################################
#                               M A I N                               #
#######################################################################


@typechecked
def main() -> None:  # pylint: disable=R0914 # noqa: WPS210, WPS213, WPS231
    """Logic."""
    files = find_csv_filenames(conf.PATH)

    if not files:
        logger.error(  # pylint: disable=logging-not-lazy
            'CSV-files not found. Did you add any in `./data/original_data` as it specified in '
            + 'https://github.com/MaxymVlasov/eco-data-visualizer#quick-start ?',
        )
        sys.exit(errno.ENOENT)

    logger.info(f'Found next files: {files}')

    for filename in files:
        for sensor, human_readable_sensor_name in conf.SENSORS.items():

            logs.setFormatter(
                logging.Formatter(
                    '\n{asctime} - {message}', datefmt='%H:%M:%S', style='{',
                ),
            )
            logger.info(
                f'Start work on "{human_readable_sensor_name}" sensor data from {filename}',
            )
            logs.setFormatter(
                logging.Formatter(
                    '{asctime} ----- {message}', datefmt='%H:%M:%S', style='{',
                ),
            )

            sensor_file = f'{filename}-{sensor}'

            #
            # Split sensors data to separate file and sort it
            #

            # Cleanup previous data
            open(f'data/csv/{sensor_file}.csv', 'w').close()  # noqa: WPS515

            pandas_csv = pd.read_csv(
                f'{conf.PATH}/{filename}',
                chunksize=conf.CHUNKSIZE,
                delimiter=',',
                dtype=str,
            )
            for chunk in pandas_csv:
                logger.info(f'Proccess chunk rows: {conf.CHUNKSIZE}')
                process_chunk_rows(chunk, sensor_file, sensor)

            logger.info('Get unique rows')
            remove_duplicate_rows(sensor_file)

            #
            # Get data for Influx
            #
            logger.info('Transform data to Database format')

            # Cleanup previous data
            with open(f'data/influx/{sensor_file}.influx', 'w') as influx_file:
                influx_file.write("""
# DDL
CREATE DATABASE sensors

# DML
# CONTEXT-DATABASE: sensors

""")

            influx_data = set()
            can_calculate_aqi = sensor in conf.AQI

            with open(f'data/csv/{sensor_file}.csv', mode='r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')

                for row in csv_reader:
                    device_id = row[0]
                    date = transform_date_to_nanoseconds(row[1])
                    concentration = round(float(row[2]), 1)

                    if can_calculate_aqi:
                        aqi = calculate_aqi(conf.AQI, sensor, concentration)  # noqa: WPS220

                        influx_data.add(  # noqa: WPS220
                            f'{human_readable_sensor_name},device_id={device_id},have_aqi=true '
                            + f'aqi={aqi},concentration={concentration} {date}\n',
                        )
                    else:
                        influx_data.add(  # noqa: WPS220
                            f'{human_readable_sensor_name},device_id={device_id},have_aqi=false '
                            + f'concentration={concentration} {date}\n',
                        )

            write_influx_data(sensor_file, influx_data)


if __name__ == '__main__':
    # execute only if run as a script
    main()
