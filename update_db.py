#!/usr/bin/python
from os import system as execulte
import sys
import getopt

try:
	import mysql.connector
except Exception as e:
	print(e)
	execulte('pip install mysql-connector')
	import mysql.connector

def usage():
	print(
'''
usage
	-h --help
	-d dabatase
	-t table
	-w where key
	-e where value
	-k keys
	-v valuse
''')
	pass

def _exit(code, cursor=None):
	print('*' * 15 + 'update_db end' + '*' * 15)
	if cursor != None:
		cursor.close()
	exit(code)

HOST = "192.168.1.23"
PORT = 3306
USER = "root"
PASSWORD = "root"

DATABASE = "jeecg-boot242"
TABLE=None
KEYS=None
VALUES=None
WHERE_KEY=None
WHERE_VALUE=None

if ( __name__ == "__main__"):
	# dump options
	print('*' * 15 + 'update_db start' + '*' * 15)
	all_options = ('-d', '--database', '-t', '--table', '-k', '--keys', '-v', '--values', '-w', '--where', '-e', '--equals', '-h', '--help')
	try:
		options, args = getopt.getopt(sys.argv[1:], 'hd:t:k:v:w:e:', ["help","database=","table=","keys=","values=", '--where', '--equals'])
		for opt, arg in options:
			if arg in all_options or opt in ('-h', '--help'):
				usage()
				_exit(1)

			# print('%s, %s' % (opt, arg))
			if opt in ('-d', '--database'):
				DATABASE = arg
			elif opt in ('-t', '--table'):
				TABLE = arg
			elif opt in ('-k', '--keys'):
				KEYS = arg.split(',')
			elif opt in ('-v', '--values'):
				VALUES = arg.split(',')
			elif opt in ('-w', '--where'):
				WHERE_KEY = arg
			elif opt in ('-e', '--equals'):
				WHERE_VALUE = arg
	except Exception as e:
		print('update_db ', e)
		_exit(2)

	# must specify below options
	if not (DATABASE and TABLE and KEYS and VALUES):
		usage()
		_exit(3)
	print('''
	DATABASE:    %s
	TABLE:       %s
	KEYS:        %s
	VALUES:      %s
	WHERE_KEY:   %s
	WHERE_VALUE: %s
	''' % (DATABASE, TABLE, KEYS, VALUES, WHERE_KEY, WHERE_VALUE))

	# KEYS and VALUES must have same length
	if len(KEYS) != len(VALUES):
		print('update_db: KEYS and VALUES must have same length')
		_exit(4)

	# genrate SQL
	update_sql = ('UPDATE %s SET (UPDATES)' % TABLE)
	update=""
	for key, value in zip(KEYS, VALUES):
		update += ("%s='%s', " % (key, value))
	# print(update[0: len(update) - 2])

	update_sql = update_sql.replace('(UPDATES)', update[0: len(update) - 2])
	# print(update_sql + '\n')

	if WHERE_KEY and WHERE_VALUE:
		update_sql += (" WHERE %s = '%s'" % (WHERE_KEY, WHERE_VALUE))

	print('update_db: %s\n' % update_sql)

	# sql connect
	db_connect = mysql.connector.connect(
			host=HOST,
			port=PORT,
			user=USER,
			passwd=PASSWORD,
			database=DATABASE
	)
	cursor = db_connect.cursor()

	# excute
	cursor.execute(update_sql)
	db_connect.commit()

	if cursor.rowcount > 0:
		print('update_db: update success')
	else:
		print('update_db: update failed')

	_exit(0 if cursor.rowcount > 0 else -1)
