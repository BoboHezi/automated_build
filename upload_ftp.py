#!/usr/bin/python3
import sys
import time
from ftplib import FTP
from os import listdir
from os import path
from os import sep
from re import search

import utils

FTP_HOST = 'ftp.droi.com'
FTP_USER = 'FreemeImp'
FTP_PWD = 'FImp0102ya'
LOCAL_PATH = None
REMOTE_PATH = None


def _exit(code, ftp=None):
    utils.star_log('upload ftp end', 60)
    if ftp:
        ftp.quit()
    exit(code)


def mkdir(dir, ftp):
    if utils.isempty(dir) or not ftp:
        return

    mk_dir = ''
    for item in dir.split('/'):
        if utils.isempty(item):
            if utils.isempty(mk_dir):
                mk_dir += item + '/'
            continue
        mk_dir += item + '/'
        try:
            ftp.mkd(mk_dir)
        except Exception as e:
            pass

    origin_path = ftp.pwd()
    rst = True
    try:
        ftp.cwd(dir)
    except Exception as e:
        rst = False
    finally:
        ftp.cwd(origin_path)
        return rst


# upload recursion
def upload_file(file, ftp):
    rst = 0
    if not (path.exists(file)):
        return 1

    if path.isdir(file):
        file = file[0:-1] if file.endswith(sep) else file
        origin_path = ftp.pwd()
        next_path = origin_path + '/' + file.split(sep)[-1]

        # mkd
        result = mkdir(next_path, ftp)
        if result:
            ftp.cwd(next_path)
        else:
            print('upload_ftp cwd failed: %s\n' % e)
            return 1
        print('remote in %s' % ftp.pwd())
        for i in listdir(file):
            rst += upload_file('%s/%s' % (file, i), ftp)
        # cwd to origin
        ftp.cwd(origin_path)
        print('remote in %s' % ftp.pwd())
    elif path.isfile(file):
        print('upload %s' % file)
        # upload
        try:
            ftp.storbinary('STOR ' + path.basename(file), open(file, 'rb'), 1024)
        except Exception as e:
            print('upload_ftp upload failed: %s\n' % e)
            return 1
    return rst


def main(argv):
    utils.star_log('upload ftp start', 60)
    option_str = 'h-host:,u-user:,c-code:,l-local:,r-remote:'
    opts = utils.dump(argv, option_str)

    if not opts:
        print("upload_ftp wrong parameter try '-h or --help' to get more information")
        return 1, None
    global FTP_HOST, FTP_USER, FTP_PWD, LOCAL_PATH, REMOTE_PATH
    if '-h' in opts or '--host' in opts:
        FTP_HOST = opts.get('-h') if opts.get('-h') else opts.get('--host')
    if '-u' in opts or '--user' in opts:
        FTP_USER = opts.get('-u') if opts.get('-u') else opts.get('--user')
    if '-c' in opts or '--code' in opts:
        FTP_PWD = opts.get('-c') if opts.get('-c') else opts.get('--code')
    if '-l' in opts or '--local' in opts:
        LOCAL_PATH = opts.get('-l') if opts.get('-l') else opts.get('--local')
    if '-r' in opts or '--remote' in opts:
        REMOTE_PATH = opts.get('-r') if opts.get('-r') else opts.get('--remote')

    print(
        """
        FTP_HOST:      %s
        FTP_USER:      %s
        FTP_PWD:       %s
        LOCAL_PATH:    %s
        REMOTE_PATH:   %s
        """ % (FTP_HOST, FTP_USER, FTP_PWD, LOCAL_PATH, REMOTE_PATH))

    if not (FTP_HOST and FTP_USER and FTP_PWD and LOCAL_PATH):
        print('upload_ftp wrong paramter!\n')
        return 2, None

    if not path.exists(LOCAL_PATH):
        print('upload_ftp %s not exists!\n' % LOCAL_PATH)
        return 3, None

    port_obj = search(':([\d]+)', FTP_HOST)
    port = int(port_obj.group(1)) if port_obj else 21
    FTP_HOST = FTP_HOST[0:len(FTP_HOST)-len(port_obj.group())] if port_obj else FTP_HOST

    # ftp connect & login
    ftp = FTP()
    ftp.connect(FTP_HOST, port, 30)
    try:
        ftp.login(FTP_USER, FTP_PWD)
        print(ftp.getwelcome() + '\n')
    except Exception as e:
        print('upload_ftp login failed: %s\n' % e)
        return 4, ftp

    # cwd
    if not utils.isempty(REMOTE_PATH):
        if not REMOTE_PATH.startswith('/'):
            REMOTE_PATH = '/' + REMOTE_PATH
        try:
            ftp.cwd(REMOTE_PATH)
        except Exception as e:
            print('upload_ftp cwd failed: %s, try mkd\n' % e)
            result = mkdir(REMOTE_PATH, ftp)
            if result:
                ftp.cwd(REMOTE_PATH)
            else:
                return 5, ftp
    print('upload_ftp remote dir: %s\n' % ftp.pwd())

    # upload recursion
    rst = upload_file(LOCAL_PATH, ftp)
    print('upload_ftp upload %s!\n' % ('success' if rst is 0 else 'failed'))
    if rst is 0:
        remote_url = 'ftp://%s@%s' % (FTP_USER, FTP_HOST)
        if port != 21:
            remote_url += ':%s' % port
        if not utils.isempty(REMOTE_PATH):
            remote_url += REMOTE_PATH
        end_path = LOCAL_PATH[0:-1] if LOCAL_PATH.endswith(sep) else LOCAL_PATH
        remote_url += '/%s' % end_path.split(sep)[-1]
        remote_url = remote_url.replace('//', '/')
        print('upload_ftp url: %s\n' % remote_url)

    return rst, ftp


if __name__ == '__main__':
    r, f = main(sys.argv[1:])
    _exit(r, f)
