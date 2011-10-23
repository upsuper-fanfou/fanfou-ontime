# - * - coding: UTF-8 - * -

from flask import g, redirect, url_for, render_template, session

from ontime import app

@app.route('/log')
@app.route('/log/p.<int:page>')
def list_logs(page=1, result=None):
    cur = g.db.cursor()
    cur.execute("""
        SELECT COUNT(`id`) c FROM `logs`
        WHERE `user_id`=%s
        """, session['user_id'])
    count = cur.fetchone()['c']
    per_page = app.config['LOGS_PER_PAGE']
    cur.execute("""
        SELECT `id`, `status`, `plan_time`, `exec_time`, `result`
        FROM `logs` WHERE `user_id`=%s
        ORDER BY `exec_time` DESC LIMIT %s, %s
        """, (session['user_id'], (page - 1) * per_page, per_page))
    logs = cur.fetchall()
    return render_template('logs.html', logs=logs, count=count)
