# - * - coding: UTF-8 - * -

import MySQLdb

from flask import Flask, g

app = Flask(__name__)
app.config.from_envvar('ONTIME_SETTINGS')

app.secret_key = app.config['SECRET_KEY']

def connect_db():
    return MySQLdb.connect(
            app.config['DB_HOSTNAME'],
            app.config['DB_USERNAME'],
            app.config['DB_PASSWORD'],
            app.config['DB_DATABASE']
            )

@app.before_request
def before_request():
    g.db = connect_db()
    g.db.autocommit(False)

@app.teardown_request
def teardown_request(exception):
    g.db.close()

import ontime.index
import ontime.auth
