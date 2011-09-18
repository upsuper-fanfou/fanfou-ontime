# - * - coding: UTF-8 - * -

import json

from flask import g

from ontime import app

@app.route('/')
def index():
    return session['user_name']
