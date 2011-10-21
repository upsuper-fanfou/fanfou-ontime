# - * - coding: UTF-8 - * -

from os import path
from flask import g, redirect, url_for, session, send_from_directory

from ontime import app

@app.route('/')
def index():
    cur = g.db.cursor()
    cur.execute("""
        SELECT `id` FROM `plans`
        WHERE `user_id`=%s LIMIT 1
        """, (session['user_id'], ))
    if not cur.fetchone():
        return redirect(url_for('new_plan'))
    else:
        return redirect(url_for('list_plans'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')
