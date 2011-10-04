# - * - coding: UTF-8 - * -

from flask import redirect, url_for

from ontime import app

@app.route('/')
def index():
    return redirect(url_for('list_plans'))
