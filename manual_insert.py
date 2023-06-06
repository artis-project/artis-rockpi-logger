
import argparse
import sqlite3
import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--temperature', type=float, required=True)
parser.add_argument('--humidity', type=float, required=True)
args = parser.parse_args()

timestamp = datetime.datetime.now()
conn = sqlite3.connect('readings.db')
c = conn.cursor()
c.execute("INSERT INTO readings (time, timestamp, temperature, humidity) VALUES (?, ?, ?, ?)", (timestamp.strftime('%Y-%m-%d %H:%M:%S'), int(timestamp.timestamp()), args.temperature, args.humidity))
new_id = c.lastrowid
conn.commit()
conn.close()

print(f"New reading added with ID {new_id}")
