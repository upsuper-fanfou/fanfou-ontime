# - * - coding: UTF-8 - * -

import os
import math
import signal

from flask import request, session, g, \
        flash, redirect, url_for, render_template
from datetime import datetime, timedelta

from ontime import app

PER_PAGE = app.config['PLANS_PER_PAGE']

@app.route('/plan')
@app.route('/plan/p.<int:page>')
def list_plans(page=1):
    if page < 1:
        return redirect(url_for('list_plans'))
    cur = g.db.cursor()
    user_id = session['user_id']
    cur.execute("""
        SELECT COUNT(`id`) c FROM `plans` WHERE `user_id`=%s
        """, (user_id, ))
    count = cur.fetchone()['c']
    cur.execute("""
        SELECT `id`, `status`, `time`, `period`, `priority`, `timeout`
        FROM `plans` WHERE `user_id`=%s
        ORDER BY `time`, `priority`, `timeout`
        LIMIT %s, %s
        """, (session['user_id'], PER_PAGE * (page - 1), PER_PAGE))
    plans = cur.fetchall()
    return render_template('plans.html', plans=plans, count=count)

def redirect_to_plans(time):
    cur = g.db.cursor()
    cur.execute("""
        SELECT COUNT(*) c FROM `plans`
        WHERE `user_id`=%s AND `time`<=%s
        """, (session['user_id'], time))
    count = float(cur.fetchone()['c'])
    page = math.ceil(count / PER_PAGE)
    return redirect(url_for('list_plans', page=page))

def is_authed(cur, plan_id):
    cur.execute("""
        SELECT `time` FROM `plans`
        WHERE `id`=%s AND `user_id`=%s
        FOR UPDATE
        """, (plan_id, session['user_id']))
    row = cur.fetchone()
    return bool(row)

def notify_daemon():
    pid_file = open(app.config['PID_FILE'], 'r')
    pid = int(pid_file.read())
    pid_file.close()
    os.kill(pid, signal.SIGUSR1)

@app.route('/plan/new', methods=['GET', 'POST'])
def new_plan():
    if request.method == 'GET':
        return render_template('new_plan.html');
    cur = g.db.cursor()
    status = request.form['status']
    date = request.form['date']
    time = request.form['time']
    time = datetime.strptime('%s %s' % (date, time), '%Y-%m-%d %H:%M')
    timezone = int(request.form['timezone'])
    time -= timedelta(minutes=timezone)
    period = int(request.form['period'])
    priority = int(request.form['priority'])
    if priority < -10:
        priority = -10
    elif priority > 10:
        priority = 10
    timeout = int(request.form['timeout'])

    if status:
        cur.execute("""
            INSERT INTO `plans`
            (`user_id`, `status`, `time`, `period`, `priority`, `timeout`)
            VALUE (%s, %s, %s, %s, %s, %s)
            """, (session['user_id'], status,
                time, period, priority, timeout))
        g.db.commit()
        notify_daemon()
        flash('添加成功', 'success')

    return redirect_to_plans(time)

@app.route('/plan/delete', methods=['POST'])
def delete_plan():
    plan_id = int(request.form['id'])
    cur = g.db.cursor()
    if not is_authed(cur, plan_id):
        return redirect(url_for('list_plans'))

    cur.execute("""
        SELECT `time` FROM `plans`
        WHERE `id`=%s FOR UPDATE
        """, (plan_id, ))
    time = cur.fetchone()['time']
    cur.execute("DELETE FROM `plans` WHERE `id`=%s", (plan_id, ))
    g.db.commit()
    
    flash('删除成功', 'success')
    return redirect_to_plans(time)

@app.route('/plan/edit', methods=['POST'])
def edit_plan():
    plan_id = int(request.form['id'])
    cur = g.db.cursor()
    if not is_authed(cur, plan_id):
        return redirect(url_for('list_plans'))

    status = request.form['status']
    time = request.form['time']
    time = datetime.strptime(time, '%Y-%m-%d %H:%M')
    period = int(request.form['period'])
    priority = int(request.form['priority'])
    if priority < -10:
        priority = -10
    elif priority > 10:
        priority = 10
    timeout = int(request.form['timeout'])

    cur.execute("""
        REPLACE INTO `plans`
        (`id`, `user_id`, `status`, `time`, `period`, `priority`, `timeout`)
        VALUE (%s, %s, %s, %s, %s, %s, %s)
        """, (plan_id, session['user_id'], status,
            time, period, priority, timeout))
    g.db.commit()
    notify_daemon()

    flash('修改成功', 'success')
    return redirect_to_plans(time)
