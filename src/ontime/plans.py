# - * - coding: UTF-8 - * -

import math

from flask import request, session, g, \
        flash, redirect, url_for, render_template
from datetime import datetime

from ontime import app

PER_PAGE = app.config['PLANS_PER_PAGE']

@app.route('/plan')
@app.route('/plan/p.<int:page>')
def list_plans(page=1):
    cur = g.db.cursor()
    cur.execute("""
        SELECT `id`, `status`, `time`, `period`, `priority`, `timeout`
        FROM `plans` WHERE `user_id`=%s
        ORDER BY `time`, `priority`, `timeout`
        LIMIT %d, %d
        """, (session['user_id'], PER_PAGE * (page - 1), PER_PAGE))
    plans = cur.fetchall()
    return render_template('plans.html', plans=plans)

def redirect_to_plans(time):
    cur = g.db.commit()
    cur.execute("""
        SELECT COUNT(*) FROM `plans`
        WHERE `user_id`=%s AND `time`<=%s
        """, (session['user_id'], time))
    count = float(cur.fetchone()[0])
    page = math.ceil(count / PER_PAGE)
    return redirect(url_for('list_plans', page=page))

def check_auth(cur, id):
    cur.execute("""
        SELECT `time` FROM `plans`
        WHERE `id`=%d AND `user_id`=%s
        FOR UPDATE
        """, (plan_id, session['user_id']))
    row = cur.fetchone()
    if not row:
        return redirect(url_for('list_plans'))

@app.route('/plan/new', methods=['POST'])
def new_plan():
    cur = g.db.cursor()
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
        INSERT INTO `plans`
        (`user_id`, `status`, `time`, `period`, `priority`, `timeout`)
        VALUE (%s, %s, %s, %d, %d, %d)
        """, (session['user_id'], status,
            time, period, priority, timeout))
    g.db.commit()
    # TODO to notify daemon

    flash('添加成功', 'success')
    redirect_to_plans(time)

@app.route('/plan/<int:plan_id>/delete', methods=['POST'])
def delete_plan(plan_id):
    cur = g.db.cursor()
    check_auth(cur, plan_id)

    cur.execute("DELETE FROM `plans` WHERE `id`=%d", (plan_id, ))
    g.db.commit()
    
    flash('删除成功', 'success')
    redirect_to_plans(time)

@app.route('/plan/<int:plan_id>/edit', methods=['POST'])
def edit_plan(plan_id):
    cur = g.db.cursor()
    check_auth(cur, plan_id)

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
        VALUE (%d, %s, %s, %s, %d, %d, %d)
        """, (plan_id, session['user_id'], status,
            time, period, priority, timeout))
    g.db.commit()
    # TODO to notify daemon

    flash('修改成功', 'success')
    redirect_to_plans(time)
