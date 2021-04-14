#!/usr/bin/python
from commands import getstatusoutput
from dump_argvs import dump
from ftplib import FTP
from os import path
from os import readlink
import sys
import re
import time

def execute(cmd):
    rst = getstatusoutput(cmd)
    return rst[0], rst[1]

def get_option_val(fpath, key):
    if not path.exists(fpath):
        return

    file = open(fpath, 'r')
    str = file.read()
    file.close()
    lines = str.splitlines()
    for line in lines:
        if not line.lstrip().startswith('#'):
            match = re.match('^(%s)(\s*)=(\s*)(.*)' % key, line)
            if match:
                # print('value: %s' % match.group(4))
                return match.group(4)
    return

def _exit(code, ftp = None):
    print('*' * 15 + 'upload ftp end' + '*' * 15)
    if ftp:
        ftp.quit()
    exit(code)

PROJECT_NAME = None
FTP_HOST     = '192.168.150.30'
FTP_USER     = 'hongxiangyuan'
FTP_PWD      = 'hongxiangyuan014'

if __name__ == '__main__':
    option_str = 'h-help,p-project:,i-ip:,u-user:,c-code:'
    opts = dump(sys.argv[1:], option_str)

    print('*' * 15 + 'upload ftp start' + '*' * 15)
    if not opts:
        print("wrong parameter try '-h or --help' to get more information")
        _exit(1)
    if opts.has_key('-h') or opts.has_key('--help'):
        _exit(2)
    if opts.has_key('-p') or opts.has_key('--project'):
        PROJECT_NAME = opts.get('-p') if opts.get('-p') else opts.get('--project')
    if opts.has_key('-h') or opts.has_key('--host'):
        ftp_host = opts.get('-h') if opts.get('-h') else opts.get('--host')
        FTP_HOST = ftp_host if ftp_host else FTP_HOST
    if opts.has_key('-u') or opts.has_key('--user'):
        ftp_user = opts.get('-u') if opts.get('-u') else opts.get('--user')
        FTP_USER = ftp_user if ftp_user else FTP_USER
    if opts.has_key('-c') or opts.has_key('--code'):
        ftp_pwd = opts.get('-c') if opts.get('-c') else opts.get('--code')
        FTP_PWD = ftp_pwd if ftp_pwd else FTP_PWD

    print(
    """
    PROJECT_NAME: %s
    FTP_HOST:     %s
    FTP_USER:     %s
    FTP_PWD:      %s
    """ % (PROJECT_NAME, FTP_HOST, FTP_USER, FTP_PWD))

    if not PROJECT_NAME:
        print('must specify project(use -p or --project)\n')
        _exit(3)

    # check MTK or SPRD
    manifest = '.repo/manifest.xml'
    if not (path.exists(manifest) and path.islink(manifest)):
        print('%s check failed\n' % manifest)
        _exit(4)
    source = readlink(manifest)
    PLATFORM = None
    if 'SPRD' in source:
        PLATFORM = 'SPRD'
    elif 'MTK' in source:
        PLATFORM = 'MTK'
    elif path.exists('vendor/sprd'):
        PLATFORM = 'SPRD'
    elif path.exists('vendor/mediatek'):
        PLATFORM = 'MTK'

    if not PLATFORM:
        print('platform check failed\n')
        _exit(5)
    print('platform: %s\n' % PLATFORM)

    # find project first
    find_cmd = 'find droi/ -maxdepth 3 -mindepth 3 -type d -name %s' % PROJECT_NAME
    status, project_path = execute(find_cmd)

    if status or not project_path or not path.exists(project_path + '/ProjectConfig.mk'):
        print('%s not found\n' % PROJECT_NAME)
        _exit(6)
    print('project: %s found %s\n' % (PROJECT_NAME, project_path))

    # find build config file
    build_config_file = get_option_val('mk', 'readonly BUILD_INFO_FILE').replace('\'', '')
    if not (build_config_file and len(build_config_file)
        and path.exists(build_config_file) and path.isfile(build_config_file)):
        build_config_file = '%s/ProjectConfig.mk' % project_path
    print('build_config_file: %s\n' % build_config_file)

    # find zip file
    publish_out = 'droi/out/%s' % PROJECT_NAME
    verno_internal = get_option_val(build_config_file, 'FREEME_PRODUCT_INFO_SW_VERNO_INTERNAL')

    zip_file = None
    if PLATFORM == 'MTK':
        verno = get_option_val(build_config_file, 'FREEME_PRODUCT_INFO_SW_VERNO')
        if (not verno_internal or not len(verno_internal)) or verno == verno_internal:
            zip_file = '%s/%s.zip' % (publish_out, verno)
        else:
            zip_file = '%s/%s(%s).zip' % (publish_out, verno, verno_internal)
    elif PLATFORM == 'SPRD':
        zip_file = '%s/bin/%s-UNSIGN.zip' % (publish_out, verno_internal)

    if not (path.exists(zip_file) and path.isfile(zip_file)):
        print('check zip_file: %s failed\n' % zip_file)
        _exit(7)
    print('zip_file: %s\n' % zip_file)

    date_str = time.strftime('%Y%m',time.localtime())
    upload_path = '/upload/%s/%s' % (date_str, PROJECT_NAME.upper())
    print('upload_path: %s' % upload_path)

    # ftp connect & login
    ftp = FTP()
    ftp.connect(FTP_HOST, 21, 30)
    try:
        ftp.login(FTP_USER, FTP_PWD)
        print(ftp.getwelcome())
    except Exception as e:
        print('login failed')
        _exit(8, ftp)
    print

    # check remote dir & cwd
    try:
        ftp.cwd(upload_path)
    except Exception as e:
        print('cwd failed, try mkd\n')
        try:
            ftp.mkd(upload_path)
            ftp.cwd(upload_path)
        except Exception as e:
            print('mkd failed\n')
            _exit(9, ftp)
    print('remote dir: %s\n' % ftp.pwd())

    # upload
    print('start upload file\n')
    try:
        ftp.storbinary('STOR ' + path.basename(zip_file), open(zip_file, 'rb'), 1024)
    except Exception as e:
        print('upload failed\n')
        _exit(10, ftp)
    print('upload success\n')

    ftp.quit()
