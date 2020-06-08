"""data-transformer-app configs."""
from types import MappingProxyType

AQI: 'MappingProxyType[str, dict]' = MappingProxyType({
    # Key == `pm25_high`
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
})

# DataFrame size, number of rows proceeded by one iteration.
# More - high memore usage, low - too long.
CHUNKSIZE = 10 ** 8

# sensors name from 'phenomenon' colum
# sensors value - for user readability
# !!! WARNING !!!: Don't use spaces and commas
SENSORS = MappingProxyType({
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
})

# Path to CSV-file(s) dir from SaveEcoBot
PATH = 'data/original_data'
