import json
import sqlite3
from flask import Flask, request, g, render_template

DEBUG = True
DATABASE = "database.db"

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config["DATABASE"])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()


@app.route("/")
def foo():
    cur = g.db.execute("""
    SELECT name, value, timestamp FROM records ORDER BY timestamp DESC LIMIT 20
    """)
    d = {}
    for name, value, timestamp in cur.fetchall():
        if name not in d:
            d[name] = {"data": [], "labels": []}
        d[name]["data"].append(value)
        d[name]["labels"].append(timestamp)
    return render_template("charts.html", record_data=json.dumps(d))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1337)
