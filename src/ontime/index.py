# - * - coding: UTF-8 - * -

from flask import g, redirect, url_for, session

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
