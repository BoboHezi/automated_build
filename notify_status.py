#!/usr/bin/python3
import os
import sys
import codecs
from os import system as execulte

import utils

try:
    import mysql.connector
except Exception as e:
    print(e)
    execulte('pip install mysql-connector')
    import mysql.connector

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def select_status(cursor, id):
    sql = ('SELECT compile_status FROM devops_compile WHERE id = \'%s\'' % id)
    cursor.execute(sql)
    result = cursor.fetchall()

    return None if len(result) < 1 else int(result[0][0])


def _exit(code, cursor=None):
    if cursor != None:
        cursor.close()
    utils.star_log('notify_status end', 60)
    exit(code)


HOST = "192.168.1.23"
PORT = 3306
USER = "root"
PASSWORD = "root"
DATABASE = "jeecg-boot242"

STATUS_CODE = {
    'queue_up': -1,
    'success': 0,
    'initial': 1,
    'connecting': 2,
    'check_fail': 3,
    'project_not_found': 4,
    'compiling': 5,
    'build_failed': 6,
    'task_stopped': 7,
    'code_not_found': 8,
    'cp_failed': 9,
    'upload_failed': 10,
    'sv_failed': 11,
}

SET_STATUS_URL = 'http://192.168.48.2:8082/jeecg-boot/compile/devopsCompile/setStatusJenkins'


if __name__ == "__main__":
    utils.star_log('notify_status start', 60)
    if len(sys.argv) <= 2:
        print('notify_status: wrong params')
        _exit(1)

    # get params
    compile_id = sys.argv[1]
    status = sys.argv[2]
    check = True if len(sys.argv) > 3 and sys.argv[3] == 'check' else False

    if status not in STATUS_CODE:
        print('wrong status')
        _exit(1)
    code = STATUS_CODE[status]

    # sql connect
    dev_ops_db = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        passwd=PASSWORD,
        database=DATABASE
    )
    cursor = dev_ops_db.cursor()

    # check id
    pre_status = select_status(cursor, compile_id)
    if pre_status is None:
        print('notify_status: wrong id %s' % compile_id)
        _exit(2, cursor)
    elif pre_status == code:
        print('notify_status: same status')
        _exit(3, cursor)

    if check:
        _exit(0)

    # update by http
    devops_token = os.getenv('DEVOPS_TOKEN')
    print('notify_status: devops_token: %s' % devops_token)
    if not utils.isempty(devops_token):
        url = SET_STATUS_URL + ('?id=%s&status=%s' % (compile_id, code))
        headers = {
            'X-Access-Token': devops_token
        }
        http_code, response = utils.get(url, None, headers=headers)
        if http_code == 200:
            try:
                code = response['code']
                success = response['success']
                if code == 200 and success:
                    print('notify_status: update "%s" success' % status)
                    _exit(0)
            except Exception as e:
                print('notify_status: Exception %s' % e)
        else:
            print('notify_status: http_code: %s, response:\n%s' % (http_code, response))

    # update
    update_sql = ('UPDATE devops_compile SET compile_status = %s WHERE id = \'%s\'' % (code, compile_id))
    cursor.execute(update_sql)
    dev_ops_db.commit()

    success = cursor.rowcount == 1
    print('notify_status: update "%s" %s' % (status, 'success' if success else 'failed'))

    _exit(0 if success else 4, cursor)
