#!/usr/bin/python3
import sys
from os import system as execulte

import utils
from utils import dump

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
            -m model
                update or insert
        ''')
    pass


def _exit(code, cursor=None):
    utils.star_log('update_db end', 60)
    if cursor != None:
        cursor.close()
    exit(code)


DATABASE = utils.DB_DATABASE
TABLE = None
KEYS = None
VALUES = None
WHERE_KEY = None
WHERE_VALUE = None
MODEL = 'update'


def main(argv):
    # dump options
    utils.star_log('update_db start', 60)

    option_str = 'h-help,d-database:,t-table:,k-keys:,v-values:,w-where:,e-equals:,m-model:'
    opts = dump(argv, option_str)

    # check dump result
    if not opts:
        return 1, None

    # check help
    if '-h' in opts or '--help' in opts:
        usage()
        return 2, None

    global DATABASE, TABLE, KEYS, VALUES, WHERE_KEY, WHERE_VALUE, MODEL
    # check options
    if '-d' in opts or '--database' in opts:
        DATABASE = opts.get('-d') if opts.get('-d') else opts.get('--database')
    if '-t' in opts or '--table' in opts:
        TABLE = opts.get('-t') if opts.get('-t') else opts.get('--table')
    if '-k' in opts or '--keys' in opts:
        keys = opts.get('-k') if opts.get('-k') else opts.get('--keys')
        if keys:
            KEYS = str(keys).split(',')
    if '-v' in opts or '--values' in opts:
        values = opts.get('-v') if opts.get('-v') else opts.get('--values')
        if values:
            VALUES = str(values).split(',')
    if '-w' in opts or '--where' in opts:
        WHERE_KEY = opts.get('-w') if opts.get('-w') else opts.get('--where')
    if '-e' in opts or '--equals' in opts:
        WHERE_VALUE = opts.get('-e') if opts.get('-e') else opts.get('--equals')
    if '-m' in opts or '--model' in opts:
        MODEL = opts.get('-m') if opts.get('-m') else opts.get('--model')

    # must specify below options
    if not (DATABASE and TABLE and KEYS and VALUES):
        usage()
        return 3, None
    print('''
        DATABASE:    %s
        TABLE:       %s
        KEYS:        %s
        VALUES:      %s
        WHERE_KEY:   %s
        WHERE_VALUE: %s
        MODEL:       %s
        ''' % (DATABASE, TABLE, KEYS, VALUES, WHERE_KEY, WHERE_VALUE, MODEL))

    # KEYS and VALUES must have same length
    if len(KEYS) != len(VALUES):
        print('update_db: KEYS and VALUES must have same length')
        return 4, None

    if MODEL == 'update':
        prefix = 'UPDATE'
    elif MODEL == 'insert':
        prefix = 'INSERT INTO'

    # genrate SQL
    sql = ('%s %s SET (UPDATES)' % (prefix, TABLE))
    update = ""
    for key, value in zip(KEYS, VALUES):
        update += ("%s='%s', " % (key, value))
    # print(update[0: len(update) - 2])

    sql = sql.replace('(UPDATES)', update[0: len(update) - 2])
    # print(sql + '\n')

    if WHERE_KEY and WHERE_VALUE:
        sql += (" WHERE %s = '%s'" % (WHERE_KEY, WHERE_VALUE))

    print('update_db: %s\n' % sql)

    # sql connect
    db_connect = mysql.connector.connect(
        host=utils.DB_HOST,
        port=utils.DB_PORT,
        user=utils.DB_USER,
        passwd=utils.DB_PASSWORD,
        database=DATABASE
    )
    cursor = db_connect.cursor()

    # excute
    cursor.execute(sql)
    db_connect.commit()

    if cursor.rowcount > 0:
        print('update_db: update success')
    else:
        print('update_db: update failed')

    return 0 if cursor.rowcount > 0 else 5, None


if __name__ == "__main__":
    r, c = main(sys.argv[1:])
    _exit(r, c)
