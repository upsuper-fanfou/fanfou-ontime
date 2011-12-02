# - * - coding: UTF-8 - * -

from flask import g

from ontime import app

@app.route('/stat')
def stat():
    cur = g.db.cursor()
    cur.execute("""
            SELECT COUNT(`id`) data FROM `logs` WHERE `result`='success'
            UNION ALL
            SELECT COUNT(`id`) FROM `logs` WHERE `result`='accepted'
            UNION ALL
            SELECT COUNT(`id`) FROM `logs` WHERE `result`='timeout'
            UNION ALL
            SELECT COUNT(`id`) FROM `logs` WHERE `result`='unauthorized'
            UNION ALL
            SELECT COUNT(`id`) FROM `logs` WHERE `result`='other'
            UNION ALL
            SELECT (
                SELECT `exec_time` FROM `logs`
                ORDER BY `exec_time` DESC LIMIT 1
                )
            UNION ALL
            SELECT COUNT(`id`) FROM `plans`
            UNION ALL
            SELECT COUNT(`user_id`) FROM `users`
            """)
    data = zip([
        'success', 'accepted', 'timeout', 'unauthorized', 'other',
        'last_exec', 'plans', 'users'
        ], [row['data'] for row in cur])
    output = ['%s:%s' % (k, v) for k, v in data]
    return '<pre>\n' + '\n'.join(output) + '\n</pre>'
