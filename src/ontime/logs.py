# - * - coding: UTF-8 - * -

from flask import g, redirect, url_for, render_template, session

from ontime import app

RESULT_SUCCESS = 0
RESULT_UNAUTHORIZED = 1
RESULT_TIMEOUT = 2
RESULT_OTHER = -1

@app.route('/log')
@app.route('/log/p.<int:page>')
@app.route('/log/result.<result>')
@app.route('/log/result.<result>/p.<int:page>')
def list_logs(page=1, result=None):
    cond = ''
    if result is not None:
        if result not in result_str:
            return redirect(url_for('list_logs'))
        else:
            cond = 'AND result=%d' % (result_str[result], )
    cur = g.db.cursor()
    per_page = app.config['LOGS_PER_PAGE']
    cur.execute("""
        SELECT `id`, `status`, `plan_time`, `exec_time`, `result`
        FROM `logs` WHERE `user_id`=%%s %s LIMIT %d, %d
        """ % (cond, (page - 1) * per_page, per_page),
        session['user_id'])
    logs = cur.fetchall()
    return render_template('logs.html', logs=logs)

result_str = { }
for key, value in globals().items():
    if key.startswith('RESULT_'):
        result_str[key[7:].lower()] = value
