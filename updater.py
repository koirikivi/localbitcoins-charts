from __future__ import print_function
from datetime import datetime
import sqlite3
import time
import requests


CONNECTION = sqlite3.connect("database.db")
INTERVAL = 30
EQUATIONS = [
    ("localbitcoins_sell_usd",
     "https://localbitcoins.com/equation/localbitcoins_sell_usd"),
    ("localbitcoins_buy_usd",
     "https://localbitcoins.com/equation/localbitcoins_buy_usd"),
    ("localbitcoins_24h_avg_usd",
     "https://localbitcoins.com/equation/localbitcoins_24h_avg_usd"),
]


def log(*objects):
    print(*objects)


def create_schema():
    cursor = CONNECTION.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS
    records (name text, value real, timestamp datetime)
    """)
    CONNECTION.commit()


def insert_record(name, value, timestamp=None):
    cursor = CONNECTION.cursor()
    if not timestamp:
        timestamp = datetime.now()
    cursor.execute("INSERT INTO records VALUES (?, ?, ?)",
                   (name, value, timestamp))
    CONNECTION.commit()


def main():
    log("Starting updater.py")
    log("Creating schema if it doesn't exist...")
    create_schema()
    log("Entering main loop")
    while True:
        timestamp = datetime.now()
        log("New iteration at", timestamp)
        for name, url in EQUATIONS:
            response = requests.get(url)
            if response.status_code != 200:
                log("ERROR", response.status_code, url)
                continue
            value = response.text
            log("INSERT", name, value, timestamp)
            insert_record(name, value, timestamp);
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
