#!/usr/bin/env python3
import time
from datetime import datetime
import pandas as pd
import csv
from os import listdir

def process(df, sensor):
    df.loc[
        # Choose only rows where with 'phenomenon' colum == sensor name
        df['phenomenon'] == sensor
        ].sort_values(
            by=['logged_at']
        # Make valid numbers for data sheets
        ).to_csv(
            # Name file as sensor name
            f'data/csv/{file}-{sensor}.csv',
            # Save only time and value
            columns=['device_id', 'logged_at', 'value'],
            # Don't wrote doc num colum
            index=False,
            # Don't wrote header name - it wrotes on iad DataDrame Iteration
            header=False,
            # Append data to file
            mode='a',
        )

def write_influx_data(sensor, sensor_name_for_user, date, concentration, device_id, aqi=None):
    with open(f'data/influx/{file}-{sensor}.influx', mode='a') as f:
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timetuple()
        date = int(time.mktime(date) * 10 ** 9)

        if aqi:
            f.write(f'{sensor_name_for_user},device_id={device_id},have_aqi=true ' + \
                f'aqi={aqi},concentration={concentration} {date}\n')
        else:
            f.write(f'{sensor_name_for_user},device_id={device_id},have_aqi=false ' + \
                f'concentration={concentration} {date}\n')

def find_csv_filenames(path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]


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
    }
}

# DataFrame size, number of rows proceeded by one iteration.
# More - high memore usage, low - too long.
chunksize = 10 ** 8



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
PATH='data/original_data'
FILES = find_csv_filenames(PATH)

print(f'Found next files: {FILES}')

for file in FILES:

    for sensor in SENSORS:
        print(f'\n{time.strftime("%H:%M:%S")} - Start work on "{SENSORS[sensor]}" sensor data from {file}')

        #
        # Split sensors data to separate file and sort it
        #

        # Cleanup previous data
        open(f'data/csv/{file}-{sensor}.csv', 'w').close()

        for chunk in pd.read_csv(f'{PATH}/{file}', chunksize=chunksize, delimiter=',', dtype=str):
            print(f'{time.strftime("%H:%M:%S")} ----- Proccess chunk rows: {chunksize}')
            process(chunk, sensor)

        # Save uniq rows
        print(f'{time.strftime("%H:%M:%S")} ----- Get unique rows')
        with open(f'data/csv/{file}-{sensor}.csv', 'r') as f:
            lines = set(f.readlines())
        with open(f'data/csv/{file}-{sensor}.csv', 'w') as f:
            f.writelines(lines)


        #
        # Get data for Influx
        #
        print(f'{time.strftime("%H:%M:%S")} ----- Transform data for Database format')

        # Cleanup previous data
        with open(f'data/influx/{file}-{sensor}.influx', 'w') as f:
            f.write("""
# DDL
CREATE DATABASE sensors

# DML
# CONTEXT-DATABASE: sensors

""")


        with open(f'data/csv/{file}-{sensor}.csv', mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                device_id = row[0]
                date = row[1]
                concentration = round(float(row[2]), 1)

                if sensor not in AQI:
                    write_influx_data(sensor, SENSORS[sensor], date, concentration, device_id)
                    continue

                #
                # CALCULATING THE AQI
                #

                for high in AQI[sensor]:
                    if concentration < float(high):
                        d = AQI[sensor][high]
                        break

                aqi = \
                    (d['aqi_high'] - d['aqi_low']) \
                    / (d['pollutant_high'] - d['pollutant_low']) \
                    * (concentration - d['pollutant_low']) \
                    + d['aqi_low']

                aqi = round(aqi)

                write_influx_data(sensor, SENSORS[sensor], date, concentration, device_id, aqi)
