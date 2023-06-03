import time
import sqlite3
import sys
from artis_api import ArtisAPI, ViolationType
# Connect to the SQLite database.
conn = sqlite3.connect('readings.db')
c = conn.cursor()
api = ArtisAPI()
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
            if temperature > 30:
                print('Temperature violation!')
                api.report_violation(latest_timestamp, ViolationType.TEMPERATURE, temperature)
            if humidity > 80:
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