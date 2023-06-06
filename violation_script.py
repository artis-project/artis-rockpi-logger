#!/usr/bin/python
import time
import sqlite3
import sys
from artis_api import ArtisAPI, ViolationType
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--temperature-threshold', type=int, required=False, default=30)
parser.add_argument('--humidity-threshold', type=int, required=False, default=80)
parser.add_argument('--artwork-id', type=int, required=True)
args = parser.parse_args()

TEMPERATURE_THRESHOLD = args.temperature_threshold
HUMIDITY_THRESHOLD = args.humidity_threshold
ARTWORK_ID = args.artwork_id
# Connect to the SQLite database.
conn = sqlite3.connect('readings.db')
c = conn.cursor()
api = ArtisAPI(ARTWORK_ID)
# Keep track of the last timestamp that we saw.
last_timestamp = None

# Loop forever.
try:
    while True:
    # Get the latest timestamp from the database.
        c.execute('SELECT MAX(timestamp) FROM readings')
        result = c.fetchone()
        latest_timestamp = result[0]

        # If the latest timestamp is different from the last one we saw,
        # then there must be a new entry in the database.
        if latest_timestamp != last_timestamp:
            print('New entry added to database!')
            # get newest temperature and humidity
            c.execute('SELECT temperature, humidity FROM readings WHERE timestamp = ?', (latest_timestamp,))
            result = c.fetchone()
            temperature = result[0]
            humidity = result[1]
            # check if temperature is too high
            if temperature > TEMPERATURE_THRESHOLD:
                print('Temperature violation!')
                api.report_violation(latest_timestamp, ViolationType.TEMPERATURE, temperature)
            if humidity > HUMIDITY_THRESHOLD:
                print('Humidity violation!')
                api.report_violation(latest_timestamp, ViolationType.HUMIDITY, humidity)


        # Update the last timestamp that we saw.
        last_timestamp = latest_timestamp

        # Wait for a few seconds before checking again.
        time.sleep(5)
except KeyboardInterrupt:
    print('\nExiting...')
    conn.close()
    sys.exit(0)