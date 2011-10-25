# - * - coding: UTF-8 - * -

from flask import g, redirect, url_for, render_template, session

from ontime import app

@app.route('/log')
@app.route('/log/p.<int:page>')
@app.route('/log/<token>/<result>')
@app.route('/log/<token>/<result>/p.<int:page>')
def list_logs(page=1, token=None, result=''):
    cur = g.db.cursor()
    per_page = app.config['LOGS_PER_PAGE']
    if not token:
        cur.execute("""
            SELECT COUNT(DISTINCT `token`, `result`) c FROM `logs`
            WHERE `user_id`=%s
            """, session['user_id'])
        count = cur.fetchone()['c']
        cur.execute("""
            SELECT HEX(`token`) token, `result`,
                   MAX(`id`) id, COUNT(`id`) count
            FROM `logs` WHERE `user_id`=%s
            GROUP BY `token`, `result`
            ORDER BY `id` DESC LIMIT %s, %s
            """, (session['user_id'], (page - 1) * per_page, per_page))
        logs = []
        cur2 = g.db.cursor()
        for row in cur:
            cur2.execute("""
                SELECT `plan_time`, `exec_time`, `status`
                FROM `logs` WHERE `id`=%s
                """, (row['id'], ))
            row.update(cur2.fetchone())
            logs.append(row)
    else:
        cur.execute("""
            SELECT COUNT(`id`) c FROM `logs`
            WHERE `user_id`=%s AND `token`=UNHEX(%s) AND `result`=%s
            """, (session['user_id'], token, result))
        count = cur.fetchone()['c']
        cur.execute("""
            SELECT `id`, `token`, `status`,
                   `plan_time`, `exec_time`, `result`
            FROM `logs`
            WHERE `user_id`=%s AND `token`=UNHEX(%s) AND `result`=%s
            ORDER BY `exec_time` DESC LIMIT %s, %s
            """, (session['user_id'], token, result,
                (page - 1) * per_page, per_page))
        logs = cur.fetchall()
    return render_template('logs.html', logs=logs, count=count)
