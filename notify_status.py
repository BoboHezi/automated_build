#!/usr/bin/python3
import sys
from os import system as execulte

try:
    import mysql.connector
except Exception as e:
    print(e)
    execulte('pip install mysql-connector')
    import mysql.connector


def select_status(cursor, id):
    sql = ('SELECT compile_status FROM devops_compile WHERE id = \'%s\'' % id)
    cursor.execute(sql)
    result = cursor.fetchall()

    return None if len(result) < 1 else int(result[0][0])


def _exit(code, cursor=None):
    if cursor != None:
        cursor.close()
    print('*' * 15 + 'notify_status end' + '*' * 15)
    exit(code)


HOST = "192.168.48.105"
PORT = 3306
USER = "root"
PASSWORD = "yun764946"
DATABASE = "jeecg-boot242"

if (__name__ == "__main__"):
    print('*' * 15 + 'notify_status start' + '*' * 15)
    if len(sys.argv) <= 2:
        print('notify_status: wrong params')
        _exit(1)

    # get params
    compile_id = sys.argv[1]
    status = sys.argv[2]
    check = True if len(sys.argv) > 3 and sys.argv[3] == 'check' else False

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
    elif str(pre_status) == status:
        print('notify_status: same status')
        _exit(3, cursor)

    if check:
        _exit(0)

    # update
    update_sql = ('UPDATE devops_compile SET compile_status = %s WHERE id = \'%s\'' % (status, compile_id))
    cursor.execute(update_sql)
    dev_ops_db.commit()

    success = cursor.rowcount == 1
    if success:
        print('notify_status: update %s success' % status)
    else:
        print('notify_status: update %s failed' % status)

    _exit(0 if success else 4, cursor)
