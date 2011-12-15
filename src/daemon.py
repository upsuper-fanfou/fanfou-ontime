#!/usr/bin/python
# - * - coding: UTF-8 - * -

import os
import sys
import json
import Queue
import signal
import logging
import MySQLdb
import threading

import oauth2 as oauth

from os import path
from math import floor
from heapq import heappush, heappop
from urllib import urlencode
from datetime import datetime, timedelta
from collections import namedtuple, defaultdict

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
    logging.debug('Refreshing feeding queue')
    if refresh_cond.acquire(blocking=False):
        refresh_cond.notify()
        refresh_cond.release()
    else:
        feeding_thread.raise_notify()

def try_loop(func, try_func=None):
    count = 0
    errors = {}
    while True:
        try:
            if not func():
                break
        except Exception, e:
            count += 1
            err_args = e.args
            if err_args in errors:
                times = errors[err_args] + 1
                errors[err_args] = times
                if not (times & (times - 1)):
                    logging.warning(repr(e) + ', %d times' % (times))
            else:
                logging.warning(repr(e))
                errors[err_args] = 1
            if try_func:
                try:
                    try_func()
                except:
                    pass

class FeedingThread(threading.Thread):
    def __init__(self):
        self._connect_db()
        self._limit_list = defaultdict(lambda: [datetime.utcnow(), 0])
        self._wait_list = []
        self._raised = False
        super(FeedingThread, self).__init__(name="f")

    def raise_notify(self):
        self._raised = True

    def _connect_db(self):
        self._db = connect_db()
    
    def run(self):
        refresh_cond.acquire()
        try_loop(self.mainloop, self._connect_db)
        refresh_cond.release()

    def _add_to_queue(self, plan, limit):
        enqueue = True
        utcnow = datetime.utcnow()
        if limit and (not plan.timeout or \
                plan.time + timedelta(minutes=plan.timeout) > utcnow):
            num, span = [int(i) for i in limit.split('/')]
            span = timedelta(minutes=span)
            list_item = self._limit_list[plan.user_id]
            if utcnow - list_item[0] >= span:
                list_item[0] = utcnow
                list_item[1] = 0
            list_item[1] += 1
            if list_item[1] > num:
                enqueue = False
                delay_to = list_item[0] + span
        if enqueue:
            plan_queue.put((plan.priority, plan.time, plan.timeout, plan))
        else:
            heappush(self._wait_list, (delay_to,
                (plan.priority, plan.time, plan.timeout), plan, limit))
    
    def mainloop(self):
        logging.debug('FeedingThread is waked')
        if not running:
            return False
        now = datetime.utcnow()
        # 将延迟的项目推入队列
        while self._wait_list and self._wait_list[0][0] <= now:
            delay_to, for_order, plan, limit = heappop(self._wait_list)
            self._add_to_queue(plan, limit)
        # 将即将发送的计划推入队列
        cur = self._db.cursor()
        cur.execute("""
            SELECT `id`, p.`user_id`, `status`, `time`,
                `period`, `priority`, `timeout`, 
                `token`, `secret`, `limit`
            FROM `plans` p
            LEFT JOIN `users` u ON u.`user_id`=p.`user_id`
            WHERE `time`<=%s AND `in_queue`=0
            FOR UPDATE
            """, (now, ))
        for row in cur:
            limit = row[-1]
            plan = Plan(*row[:-1])
            self._add_to_queue(plan, limit)
        cur.execute("""
            UPDATE `plans`
            SET `in_queue`=1
            WHERE `time`<=%s AND `in_queue`=0
            """, (now, ))
        self._db.commit()
        # 计算下一个未入队计划的时间
        utcnow = datetime.utcnow()
        cur.execute("""
            SELECT `time` FROM `plans`
            WHERE `time`>%s AND `in_queue`=0
            LIMIT 1
            """, (now, ))
        plan = cur.fetchone()
        if not plan:
            sleep_time = None
        else:
            sleep_time = (plan[0] - utcnow).total_seconds()
        # 计算延时队列中项目的等待时间
        if self._wait_list:
            next_time = self._wait_list[0][0]
            next_time = (next_time - utcnow).total_seconds()
            if not sleep_time or sleep_time > next_time:
                sleep_time = next_time
        # 等待被唤醒
        if self._raised:
            self._raised = False
        else:
            refresh_cond.wait(sleep_time)
        return True

class SendingThread(threading.Thread):
    def __init__(self, num):
        self._create_client()
        super(SendingThread, self).__init__(name='s%d' % (num, ))

    def _create_client(self):
        self._client = oauth.Client(consumer, timeout=10)

    def run(self):
        try_loop(self.mainloop, self._create_client)

    def mainloop(self):
        plan = plan_queue.get()
        try:
            return self._process_plan(plan)
        except:
            plan_queue.put(plan)
            raise

    def _process_plan(self, plan):
        if not plan:
            return False
        priority, time, timeout, plan = plan
        status = plan.status
        now = datetime.utcnow()
        exec_time = now
        # 判断是否已超时
        if timeout and time + timedelta(minutes=timeout) < now:
            result = 'timeout'
        else:
            logging.debug('Posting status')
            token = oauth.Token(plan.token, plan.secret)
            self._client.token = token
            # 发送
            try:
                resp, content = self._client.request(
                        'http://api.fanfou.com/statuses/update.json',
                        'POST', urlencode({'status': status.encode('utf8')})
                        )
            except:
                result_queue.put((plan, 'other', exec_time, status))
                return True
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
        result_queue.put((plan, result, exec_time, status))
        return True

class WritingThread(threading.Thread):
    def __init__(self):
        self._connect_db()
        super(WritingThread, self).__init__(name="w")

    def _connect_db(self):
        self._db = connect_db()

    def run(self):
        try_loop(self.mainloop, self._connect_db)

    def mainloop(self):
        result = result_queue.get()
        err_items = set()
        try:
            return self._process_result(result)
        except:
            if id(result) not in err_items:
                result_queue.put(result)
                err_items.add(id(result))
            raise

    def _process_result(self, result):
        if not result:
            return False
        plan, result, time, status = result
        cur = self._db.cursor()
        # 添加发送记录
        logging.debug('Writing Log')
        cur.execute("""
            INSERT INTO `logs`
            (`user_id`, `status`, `token`, `plan_time`, `exec_time`, `result`)
            VALUES (%s, %s, UNHEX(MD5(%s)), %s, %s, %s)
            """,
            (plan.user_id, status, plan.status, plan.time, time, result))
        # 判断是否为周期计划
        if not plan.period:
            cur.execute("DELETE FROM `plans` WHERE `id`=%s", (plan.id, ))
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
    elif signum == signal.SIGTERM or signum == signal.SIGINT:
        logging.debug('Exit signal')
        sys.exit()
    elif DEBUG and signum == signal.SIGTRAP:
        try:
            execfile('debug.py')
        except Exception, e:
            print e

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
    config_file = os.environ['ONTIME_SETTINGS']
    # 读取配置文件
    execfile(config_file)
    # 放弃管理员权限
    if os.getuid() == 0:
        if GROUP:
            import grp
            gid = grp.getgrnam(GROUP)[2]
            os.setgid(gid)
        if USER:
            import pwd
            uid = pwd.getpwnam(USER)[2]
            os.setuid(uid)
    # 设置记录信息
    FORMAT = '%(asctime)s %(threadName)s/%(levelname)s: %(message)s'
    if DEBUG:
        logging.basicConfig(format=FORMAT,
                level=logging.DEBUG)
    else:
        logging.basicConfig(filename=LOG_FILE, format=FORMAT,
                level=logging.INFO)
    # 判断 pidfile
    if path.exists(PID_FILE):
        exists = True
        pid_file = open(PID_FILE, 'r')
        pid = int(pid_file.read())
        pid_file.close()
        try:
            os.kill(pid, signal.SIGUSR1)
        except OSError, e:
            if e.errno == 3:
                os.unlink(PID_FILE)
                exists = False
        if exists:
            print 'Fanfou-ontime daemon has already been running'
            exit(1)
    # 创建 pidfile
    pid_file = open(PID_FILE, 'w')
    pid_file.write(str(os.getpid()))
    pid_file.close()
    # 初始化数据
    logging.info('Start')
    consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    # 创建队列和条件锁
    plan_queue = Queue.PriorityQueue()
    result_queue = Queue.Queue()
    refresh_cond = threading.Condition()
    # 设置信号处理
    signal.signal(signal.SIGUSR1, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    if DEBUG:
        signal.signal(signal.SIGTRAP, signal_handler)
    # 清理数据库中的数据
    clean_plans_flag()
    # 初始化线程
    feeding_thread = FeedingThread()
    writing_thread = WritingThread()
    sending_threads = []
    for i in range(THREAD_AMOUNT):
        sending_threads.append(SendingThread(i))
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
    logging.info('Exiting daemon')
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
    logging.info('Exit complete')
    raise e
