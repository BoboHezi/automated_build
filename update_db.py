#!/usr/bin/python
from os import system as execulte
from dump_argvs import dump
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

	option_str = 'h-help,d-database:,t-table:,k-keys:,v-values:,w-where:,e-equals:'
	opts = dump(sys.argv[1:], option_str)

	# check dump result
	if not opts:
		_exit(1)

	# check help
	if opts.has_key('-h') or opts.has_key('--help'):
		usage()
		_exit(2)

	# check options
	if opts.has_key('-d') or opts.has_key('--database'):
		DATABASE = opts.get('-d') if opts.get('-d') else opts.get('--database')
	if opts.has_key('-t') or opts.has_key('--table'):
		TABLE = opts.get('-t') if opts.get('-t') else opts.get('--table')
	if opts.has_key('-k') or opts.has_key('--keys'):
		keys = opts.get('-k') if opts.get('-k') else opts.get('--keys')
		if keys:
			KEYS = str(keys).split(',')
	if opts.has_key('-v') or opts.has_key('--values'):
		values = opts.get('-v') if opts.get('-v') else opts.get('--values')
		if values:
			VALUES = str(values).split(',')
	if opts.has_key('-w') or opts.has_key('--where'):
		WHERE_KEY = opts.get('-w') if opts.get('-w') else opts.get('--where')
	if opts.has_key('-e') or opts.has_key('--equals'):
		WHERE_VALUE = opts.get('-e') if opts.get('-e') else opts.get('--equals')

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
