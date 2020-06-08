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

import pandas as pd

try:
    from typeguard import typechecked
except ModuleNotFoundError:
    def typechecked(func=None):
        """Skip runtime type checking on the function arguments."""
        return func

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

#######################################################################
#                          F U N C T I O N S                          #
#######################################################################


@typechecked
def process(dataframe: pd.core.frame.DataFrame, filename: str, sensor: str):
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
def write_influx_data(
    filename: str,
    sensor_name_for_user: str,
    date,
    concentration: float,
    device_id: str,
    aqi: int = None,
):
    """Append file with data in InfluxDB format.

    Args:
        filename: (str) Filename.
        sensor_name_for_user: (str) Human readable sensor name.
        date: (str) Datetime string in `%Y-%m-%d %H:%M:%S` format.
        concentration: (float) Sensor value at `date`.
        device_id: (str) SaveEcoBot Device ID where this sensor installed.
        aqi: (int) Air Quality Index. Default to None.
    """
    with open(f'data/influx/{filename}.influx', mode='a') as influx_file:
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').timetuple()
        date = int(time.mktime(date) * 10 ** 9)

        if aqi == None:
            influx_file.write(
                f'{sensor_name_for_user},device_id={device_id},have_aqi=false '
                + f'concentration={concentration} {date}\n',
            )
        else:
            influx_file.write(
                f'{sensor_name_for_user},device_id={device_id},have_aqi=true '
                + f'aqi={aqi},concentration={concentration} {date}\n',
            )


@typechecked
def find_csv_filenames(path_to_dir: str, suffix: str = ".csv"):
    """
    Find all files with specified extention

    Args:
        path_to_dir (str): Path to dir where files where to look for files
        suffix (str): File extention. Default to ".csv"
    Returns:
        array
    """
    filenames = listdir(path_to_dir)
    return [filename for filename in filenames if filename.endswith(suffix)]


@typechecked
def main() -> None:
    """Logic."""
    AQI = {
        # Key == pm25_high
        'pm25': {
            '12.0': {
                'aqi_high': 50,
                'aqi_low': 0,
                'pollutant_high': 12.0,
                'pollutant_low': 0.0,
            },
            '35.4': {
                'aqi_high': 100,
                'aqi_low': 51,
                'pollutant_high': 35.4,
                'pollutant_low': 12.1,
            },
            '55.4': {
                'aqi_high': 150,
                'aqi_low': 101,
                'pollutant_high': 55.4,
                'pollutant_low': 35.5,
            },
            '150.4': {
                'aqi_high': 200,
                'aqi_low': 151,
                'pollutant_high': 150.4,
                'pollutant_low': 55.5,
            },
            '250.4': {
                'aqi_high': 300,
                'aqi_low': 201,
                'pollutant_high': 250.4,
                'pollutant_low': 150.5,
            },
            '350.4': {
                'aqi_high': 400,
                'aqi_low': 301,
                'pollutant_high': 350.4,
                'pollutant_low': 250.5,
            },
            '500.4': {
                'aqi_high': 500,
                'aqi_low': 401,
                'pollutant_high': 500.4,
                'pollutant_low': 350.5,
            },
        },
        'pm10': {
            '54': {
                'aqi_high': 50,
                'aqi_low': 0,
                'pollutant_high': 54,
                'pollutant_low': 0,
            },
            '154': {
                'aqi_high': 100,
                'aqi_low': 51,
                'pollutant_high': 154,
                'pollutant_low': 55,
            },
            '254': {
                'aqi_high': 150,
                'aqi_low': 101,
                'pollutant_high': 254,
                'pollutant_low': 155,
            },
            '354': {
                'aqi_high': 200,
                'aqi_low': 151,
                'pollutant_high': 354,
                'pollutant_low': 255,
            },
            '424': {
                'aqi_high': 300,
                'aqi_low': 201,
                'pollutant_high': 424,
                'pollutant_low': 355,
            },
            '504': {
                'aqi_high': 301,
                'aqi_low': 400,
                'pollutant_high': 504,
                'pollutant_low': 425,
            },
            '604': {
                'aqi_high': 500,
                'aqi_low': 401,
                'pollutant_high': 604,
                'pollutant_low': 505,
            },
        },
    }

    # DataFrame size, number of rows proceeded by one iteration.
    # More - high memore usage, low - too long.
    CHUNKSIZE = 10 ** 8

    # sensors name from 'phenomenon' colum
    # sensors value - for user readability
    #!!! WARNING !!!: Don't use spaces and commas
    SENSORS = {
        'pm10': 'PM10_mcg/m³',
        'pm25': 'PM2.5_mcg/m³',
        'heca_humidity': 'HECA_relative_humidity_%',
        'humidity': 'Relative_humidity_%',
        'min_micro': 'min_micro',
        'max_micro': 'max_micro',
        'pressure': 'Atmospheric_pressure_mmHg',
        'signal': 'Wi-Fi_signal_dBm',
        'temperature': 'Temperature_C°',
        'heca_temperature': 'HECA_temperature_C°',
    }

    # SaveEcoBot CSV file
    PATH = 'data/original_data'
    FILES = find_csv_filenames(PATH)

    if not FILES:
        logger.error(
            'CSV-files not found. Did you add any in `./data/original_data` as it specified in\n'
            + 'https://github.com/MaxymVlasov/eco-data-visualizer#quick-start ?',
        )
        sys.exit(errno.ENOENT)

    logger.info(f'Found next files: {FILES}')

    for file in FILES:

        for sensor in SENSORS:
            sensor_file = f'{file}-{sensor}'
            logger.info(
                f'\n{time.strftime("%H:%M:%S")} - ' +
                f'Start work on "{SENSORS[sensor]}" sensor data from {file}',
            )

            #
            # Split sensors data to separate file and sort it
            #

            # Cleanup previous data
            open(f'data/csv/{sensor_file}.csv', 'w').close()

            for chunk in pd.read_csv(f'{PATH}/{file}', chunksize=CHUNKSIZE, delimiter=',', dtype=str):
                logger.info(f'{time.strftime("%H:%M:%S")} ----- Proccess chunk rows: {CHUNKSIZE}')
                process(chunk, sensor_file, sensor)

            # Save uniq rows
            logger.info(f'{time.strftime("%H:%M:%S")} ----- Get unique rows')
            with open(f'data/csv/{sensor_file}.csv', 'r') as csv_file:
                lines = set(csv_file.readlines())
            with open(f'data/csv/{sensor_file}.csv', 'w') as csv_file:
                csv_file.writelines(lines)

            #
            # Get data for Influx
            #
            logger.info(f'{time.strftime("%H:%M:%S")} ----- Transform data for Database format')

            # Cleanup previous data
            with open(f'data/influx/{sensor_file}.influx', 'w') as influx_file:
                influx_file.write("""
# DDL
CREATE DATABASE sensors

# DML
# CONTEXT-DATABASE: sensors

""")

            with open(f'data/csv/{sensor_file}.csv', mode='r') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')

                for row in csv_reader:
                    device_id = row[0]
                    date = row[1]
                    concentration = round(float(row[2]), 1)

                    if sensor not in AQI:
                        write_influx_data(
                            sensor_file,
                            SENSORS[sensor],
                            date,
                            concentration,
                            device_id,
                        )
                        continue

                    #
                    # CALCULATING THE AQI
                    #

                    for high in AQI[sensor]:
                        if concentration < float(high):
                            _ = AQI[sensor][high]
                            break

                    aqi = (
                        (_['aqi_high'] - _['aqi_low'])
                        / (_['pollutant_high'] - _['pollutant_low'])
                        * (concentration - _['pollutant_low'])
                        + _['aqi_low']
                    )

                    aqi = round(aqi)

                    write_influx_data(
                        sensor_file,
                        SENSORS[sensor],
                        date,
                        concentration,
                        device_id,
                        aqi,
                    )


if __name__ == '__main__':
    # execute only if run as a script
    main()
