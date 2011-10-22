# - * - coding: UTF-8 - * -

import MySQLdb
import MySQLdb.cursors

from flask import Flask, g

app = Flask(__name__)
app.config.from_envvar('ONTIME_SETTINGS')

app.secret_key = app.config['SECRET_KEY']

def connect_db():
    return MySQLdb.connect(
            app.config['DB_HOSTNAME'],
            app.config['DB_USERNAME'],
            app.config['DB_PASSWORD'],
            app.config['DB_DATABASE'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor
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
import ontime.plans
import ontime.logs
