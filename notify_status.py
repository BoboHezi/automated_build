#!/usr/bin/python
from os import system as execulte
import sys

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
	exit(code)

if ( __name__ == "__main__"):
	if len(sys.argv) <= 2:
		print('\033[31mnotify_status: wrong params\033[0m')
		_exit(1)

	# get params
	compile_id = sys.argv[1]
	status = sys.argv[2]

	# sql connect
	dev_ops_db = mysql.connector.connect(
		host="192.168.1.23",
		user="root",
		passwd="root",
		database="jeecg-boot242"
	)
	cursor = dev_ops_db.cursor()

	# check id
	pre_status = select_status(cursor, compile_id)
	if pre_status == None:
		print('\033[31mnotify_status: wrong id %s\033[0m' % compile_id)
		_exit(2, cursor)
	elif str(pre_status) == status:
		print('\033[31mnotify_status: same status\033[0m')
		_exit(3, cursor)

	# update
	update_sql = ('UPDATE devops_compile SET compile_status = %s WHERE id = \'%s\'' % (status, compile_id))
	cursor.execute(update_sql)
	dev_ops_db.commit()

	success = cursor.rowcount == 1
	if success:
		print('\033[32mnotify_status: update %s success\033[0m' % status)
	else:
		print('\033[31mnotify_status: update %s failed\033[0m' % status)

	_exit(0 if success else 4, cursor)
