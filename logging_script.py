#!/usr/bin/python
# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import sys

import Rockfruit_DHT
import sqlite3
import datetime

# Parse command line parameters.
sensor_args = {
    "11": Rockfruit_DHT.DHT11,
    "22": Rockfruit_DHT.DHT22,
    "2302": Rockfruit_DHT.AM2302,
}
if len(sys.argv) == 3 and sys.argv[1] in sensor_args:
    sensor = sensor_args[sys.argv[1]]
    pin = sys.argv[2]
else:
    print("Usage: sudo ./Adafruit_DHT.py [11|22|2302] <GPIO pin number>")
    print(
        "Example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO pin #4"
    )
    sys.exit(1)

# Connect to the SQLite database.
conn = sqlite3.connect("readings.db")
c = conn.cursor()
c.execute(
    """CREATE TABLE IF NOT EXISTS readings
             (time STRING, timestamp INTEGER, temperature REAL, humidity REAL, elapsed_time REAL)"""
)
# Try to grab a sensor reading.  Use the read_retry method which will retry up
# to 15 times to get a sensor reading (waiting 2 seconds between each retry).
try:
    while True:
        start_time = datetime.datetime.now()
        humidity, temperature = Rockfruit_DHT.read_retry(sensor, pin, retries=15)
        timestamp = datetime.datetime.now()
        # Un-comment the line below to convert the temperature to Fahrenheit.
        # temperature = temperature * 9/5.0 + 32

        # Note that sometimes you won't get a reading and
        # the results will be null (because Linux can't
        # guarantee the timing of calls to read the sensor).
        # If this happens try again!
        if humidity is not None and temperature is not None:
            end_time = datetime.datetime.now()
            print("Temp={0:0.1f}*  Humidity={1:0.1f}%".format(temperature, humidity))
            elapsed_time = end_time - start_time
            print(f"elapsed time: {elapsed_time.total_seconds()} seconds")
            c.execute(
            "INSERT INTO readings VALUES (?, ?, ?, ?, ?)",
                (
                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    int(timestamp.timestamp()),
                    temperature,
                    humidity,
                    elapsed_time.total_seconds(),
                ),
            )
            conn.commit()
        else:
            print(f"{int(timestamp.timestamp())} failed to get a reading...")
        

except KeyboardInterrupt:
    print("\nExiting...")
    conn.close()
    sys.exit(0)
