#!/usr/bin/python
# - * - coding: UTF-8 - * -

import os
import sys
import json
import Queue
import signal
import MySQLdb
import threading

import oauth2 as oauth

from os import path
from math import floor
from urllib import urlencode
from datetime import datetime, timedelta
from collections import namedtuple

from config import *

Plan = namedtuple('Plan',
        ['id', 'user_id', 'status', 'time',
            'period', 'priority', 'timeout',
            'token', 'secret'])

def connect_db():
    db = MySQLdb.connect(DB_HOSTNAME,
            DB_USERNAME, DB_PASSWORD, DB_DATABASE,
            charset='utf8')
    db.autocommit(False)
    return db

def refresh_queue():
    print 'refreshing...'
    refresh_cond.acquire()
    refresh_cond.notify()
    refresh_cond.release()

class FeedingThread(threading.Thread):
    def __init__(self):
        self._db = connect_db()
        super(FeedingThread, self).__init__()
    
    def run(self):
        refresh_cond.acquire()
        while self.mainloop():
            pass
        refresh_cond.release()
    
    def mainloop(self):
        print 'waked'
        if not running:
            return False
        # 将即将发送的计划推入队列
        cur = self._db.cursor()
        now = datetime.utcnow()
        cur.execute("""
            SELECT `id`, p.`user_id`, `status`, `time`,
                `period`, `priority`, `timeout`, 
                `token`, `secret`
            FROM `plans` p
            LEFT JOIN `users` u ON u.`user_id`=p.`user_id`
            WHERE `time`<=%s AND `in_queue`=0
            FOR UPDATE
            """, (now, ))
        for row in cur:
            plan = Plan(*row)
            plan_queue.put((plan.priority, plan.time, plan.timeout, plan))
        cur.execute("""
            UPDATE `plans`
            SET `in_queue`=1
            WHERE `time`<=%s AND `in_queue`=0
            """, (now, ))
        self._db.commit()
        # 获取下一次唤醒的时间
        cur.execute("""
            SELECT `time` FROM `plans`
            WHERE `time`>%s AND `in_queue`=0
            LIMIT 1
            """, (now, ))
        plan = cur.fetchone()
        # 等待被唤醒
        if not plan:
            refresh_cond.wait()
        else:
            next_time = plan[0]
            sleep_time = (next_time - datetime.utcnow()).total_seconds()
            refresh_cond.wait(sleep_time)
        return True

class SendingThread(threading.Thread):
    def __init__(self):
        self._client = oauth.Client(consumer)
        super(SendingThread, self).__init__()

    def run(self):
        while self.mainloop():
            pass

    def mainloop(self):
        plan = plan_queue.get()
        if not plan:
            return False
        priority, time, timeout, plan = plan
        status = plan.status
        now = datetime.utcnow()
        exec_time = now
        # 判断是否已超时
        if time + timedelta(minutes=timeout) < now:
            result = 'timeout'
        else:
            print 'sending...'
            token = oauth.Token(plan.token, plan.secret)
            self._client.token = token
            # 发送
            resp, content = self._client.request(
                    'http://api.fanfou.com/statuses/update.json',
                    'POST', urlencode({'status': status.encode('utf8')})
                    )
            self._client.token = None
            # 测试返回结果
            result = 'other'
            if resp.status == 200:
                try:
                    content = json.loads(content)
                except ValueError:
                    pass
                else:
                    create_time = datetime.strptime(content['created_at'],
                            '%a %b %d %H:%M:%S +0000 %Y')
                    exec_time = create_time
                    result = 'success'
            elif resp.status == 202:
                result = 'accepted'
            elif resp.status == 401:
                result = 'unauthorized'
        result_queue.put((plan.id, result, exec_time, status))
        return True

class WritingThread(threading.Thread):
    def __init__(self):
        self._db = connect_db()
        super(WritingThread, self).__init__()

    def run(self):
        while self.mainloop():
            pass

    def mainloop(self):
        result = result_queue.get()
        if not result:
            return False
        plan_id, result, time, status = result
        cur = self._db.cursor()
        # 读取计划信息
        cur.execute("""
            SELECT `id`, `user_id`, `status`, `time`,
                `period`, `priority`, `timeout`, 0, 0
            FROM `plans` WHERE `id`=%s
            FOR UPDATE
            """, (plan_id, ))
        plan = Plan(*cur.fetchone())
        # 添加发送记录
        print 'writing...'
        cur.execute("""
            INSERT INTO `logs`
            (`user_id`, `status`, `plan_time`, `exec_time`, `result`)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (plan.user_id, status, plan.time, time, result))
        # 判断是否为周期计划
        if not plan.period:
            cur.execute("DELETE FROM `plans` WHERE `id`=%s", (plan_id, ))
        else:
            period = timedelta(minutes=plan.period)
            # 计算下一次执行时间
            delta = datetime.utcnow() - plan.time
            if delta > period:
                delta = delta.total_seconds() / period.total_seconds()
                delta = int(floor(delta) + 1)
                next_time = plan.time + timedelta(minutes=plan.period * delta)
            else:
                next_time = plan.time + period
            # 更新发送计划
            cur.execute("""
                UPDATE `plans`
                SET `time`=%s, `in_queue`=0
                WHERE `id`=%s
                """, (next_time, plan.id))
        # 完成修改
        self._db.commit()
        refresh_queue()
        return True

def signal_handler(signum, frame):
    if signum == signal.SIGUSR1:
        refresh_queue()
    elif signum == signal.SIGTERM:
        sys.exit()

def clean_plans_flag():
    db = connect_db()
    cur = db.cursor()
    cur.execute("""
        UPDATE `plans` SET `in_queue`=0
        WHERE `in_queue`=1
        """)
    db.commit()
    db.close()

if __name__ == '__main__':
    if path.exists(PID_FILE):
        print 'Fanfou-ontime daemon has already been running'
        exit(1)
    # 创建 pidfile
    pid_file = open(PID_FILE, 'w')
    pid_file.write(str(os.getpid()))
    pid_file.close()
    # 初始化数据
    consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    # 创建队列和条件锁
    plan_queue = Queue.PriorityQueue()
    result_queue = Queue.Queue()
    refresh_cond = threading.Condition()
    # 设置信号处理
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    # 清理数据库中的数据
    clean_plans_flag()
    # 初始化线程
    feeding_thread = FeedingThread()
    writing_thread = WritingThread()
    sending_threads = []
    for i in range(THREAD_AMOUNT):
        sending_threads.append(SendingThread())
    # 开始运行
    running = True
    threads = sending_threads + [feeding_thread, writing_thread]
    for thread in threads:
        thread.start()
    # 等待
    while True:
        try:
            signal.pause()
        except SystemExit, e:
            break
    # 消除运行标签并等待线程结束
    print 'exiting...'
    running = False
    refresh_queue()
    for i in range(THREAD_AMOUNT):
        plan_queue.put(None)
    result_queue.put(None)
    for thread in threads:
        thread.join()
    # 结束
    clean_plans_flag()
    os.unlink(PID_FILE)
    raise e
