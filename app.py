from dateutil.parser import parse as parse_datetime
import calendar
import json
import sqlite3
from flask import Flask, render_template

DEBUG = False
DATABASE = "database.db"
HOST = "0.0.0.0"
PORT = 1337

app = Flask(__name__)
app.config.from_object(__name__)
try:
    app.config.from_envvar("CHARTS_SETTINGS")
except RuntimeError:
    pass


def connect_db():
    return sqlite3.connect(app.config["DATABASE"])


def jstimestamp(time):
    return calendar.timegm(time.utctimetuple()) * 1000


def get_records(average_interval=5*60, after=60*60*24):
    db = connect_db()
    cur = db.execute("""
        SELECT name,
               AVG(value) value,
               DATETIME((strftime('%s', timestamp) / ?) * ?, 'unixepoch') timestamp
        FROM records
        WHERE timestamp > datetime('now', ?)
        GROUP BY name, timestamp
        ORDER BY name ASC, timestamp ASC
        """, (average_interval, average_interval, "-%s seconds" % after))
    return cur.fetchall()


def get_chartjs_data(records):
    d = {}
    for name, value, timestamp in records:
        if name not in d:
            d[name] = {"data": [], "labels": []}
        d[name]["data"].append(value)
        d[name]["labels"].append(parse_datetime(timestamp).strftime("%H:%M"))
    return d


def get_flotcharts_data(records):
    d = {}
    for name, value, timestamp in records:
        if name not in d:
            d[name] = []
        time = parse_datetime(timestamp)
        d[name].append([jstimestamp(time), value])
    return d


@app.route("/")
def foo():
    records = get_records(average_interval=15 * 60)
    chartjs_data = get_chartjs_data(records)
    flotcharts_data = get_flotcharts_data(records)

    return render_template("charts.html",
                            chartjs_data=json.dumps(chartjs_data),
                            flotcharts_data=json.dumps(flotcharts_data))


if __name__ == "__main__":
    app.run(host=app.config["HOST"], port=app.config["PORT"])
