#!/usr/bin/python
from commands import getstatusoutput
from ftplib import FTP
from os import path
from os import readlink
import sys
import re
import time
import utils

def execute(cmd):
    rst = getstatusoutput(cmd)
    return rst[0], rst[1]

def _exit(code, ftp = None):
    print('*' * 15 + 'upload ftp end' + '*' * 15)
    if ftp:
        ftp.quit()
    exit(code)

PROJECT_NAME = None
ZIP_FILE     = None
FTP_HOST     = '192.168.150.30'
FTP_USER     = 'hongxiangyuan'
FTP_PWD      = 'hongxiangyuan014'

if __name__ == '__main__':
    print('*' * 15 + 'upload ftp start' + '*' * 15)
    option_str = 'h-help,p-project:,f-file:,i-ip:,u-user:,c-code:'
    opts = utils.dump(sys.argv[1:], option_str)

    if not opts:
        print("upload_ftp wrong parameter try '-h or --help' to get more information")
        _exit(1)
    if opts.has_key('-h') or opts.has_key('--help'):
        _exit(2)
    if opts.has_key('-p') or opts.has_key('--project'):
        PROJECT_NAME = opts.get('-p') if opts.get('-p') else opts.get('--project')
    if opts.has_key('-f') or opts.has_key('--file'):
        ZIP_FILE = opts.get('-f') if opts.get('-f') else opts.get('--file')
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
    ZIP_FILE:     %s
    FTP_HOST:     %s
    FTP_USER:     %s
    FTP_PWD:      %s
    """ % (PROJECT_NAME, ZIP_FILE, FTP_HOST, FTP_USER, FTP_PWD))

    if not PROJECT_NAME:
        print('upload_ftp must specify project(use -p or --project)\n')
        _exit(3)

    # check MTK or SPRD
    manifest = '.repo/manifest.xml'
    if not (path.exists(manifest) and path.islink(manifest)):
        print('upload_ftp %s check failed\n' % manifest)
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
        print('upload_ftp platform check failed\n')
        _exit(5)
    print('upload_ftp platform: %s\n' % PLATFORM)

    # find project first
    find_cmd = 'find droi/ -maxdepth 3 -mindepth 3 -type d -name %s' % PROJECT_NAME
    status, project_path = execute(find_cmd)

    if status or not project_path or not path.exists(project_path + '/ProjectConfig.mk'):
        print('upload_ftp %s not found\n' % PROJECT_NAME)
        _exit(6)
    print('upload_ftp project: %s found %s\n' % (PROJECT_NAME, project_path))

    # find build config file
    build_config_file = utils.get_option_val('mk', 'readonly BUILD_INFO_FILE').replace('\'', '')
    if utils.isempty(build_config_file) or not path.isfile(build_config_file) :
        build_config_file = '%s/ProjectConfig.mk' % project_path
    project_product = utils.get_option_val(build_config_file, 'project' if PLATFORM == 'MTK' else 'product')
    if utils.isempty(project_product) \
        or project_product != (PROJECT_NAME if PLATFORM == 'MTK' else 'full_' + PROJECT_NAME):
        build_config_file = '%s/ProjectConfig.mk' % project_path
    print('upload_ftp build_config_file: %s\n' % build_config_file)

    # find zip file
    publish_out = 'droi/out/%s' % PROJECT_NAME
    verno_internal = utils.get_option_val(build_config_file, 'FREEME_PRODUCT_INFO_SW_VERNO_INTERNAL')

    if utils.isempty(ZIP_FILE) or not path.isfile(ZIP_FILE):
        # input ZIP_FILE wrong, dump by project
        if PLATFORM == 'MTK':
            verno = utils.get_option_val(build_config_file, 'FREEME_PRODUCT_INFO_SW_VERNO')
            if utils.isempty(verno_internal) or verno == verno_internal:
                ZIP_FILE = '%s/%s.zip' % (publish_out, verno)
            else:
                ZIP_FILE = '%s/%s(%s).zip' % (publish_out, verno, verno_internal)
        elif PLATFORM == 'SPRD':
            ZIP_FILE = '%s/bin/%s.zip' % (publish_out, verno_internal)

    if not (path.exists(ZIP_FILE) and path.isfile(ZIP_FILE)):
        print('upload_ftp check ZIP_FILE: %s failed\n' % ZIP_FILE)
        _exit(7)
    print('upload_ftp ZIP_FILE: %s\n' % ZIP_FILE)

    date_str = time.strftime('%Y%m',time.localtime())
    upload_path = '/upload/%s/%s' % (date_str, PROJECT_NAME.upper())
    print('upload_ftp upload_path: %s' % upload_path)

    # ftp connect & login
    ftp = FTP()
    ftp.connect(FTP_HOST, 21, 30)
    try:
        ftp.login(FTP_USER, FTP_PWD)
        print(ftp.getwelcome())
    except Exception as e:
        print('upload_ftp login failed')
        _exit(8, ftp)
    print

    # check remote dir & cwd
    try:
        ftp.cwd(upload_path)
    except Exception as e:
        print('upload_ftp cwd failed, try mkd\n')
        try:
            ftp.mkd(upload_path)
            ftp.cwd(upload_path)
        except Exception as e:
            print('upload_ftp mkd failed\n')
            _exit(9, ftp)
    print('upload_ftp remote dir: %s\n' % ftp.pwd())

    # upload
    print('upload_ftp start upload file\n')
    try:
        ftp.storbinary('STOR ' + path.basename(ZIP_FILE), open(ZIP_FILE, 'rb'), 1024)
    except Exception as e:
        print('upload_ftp upload failed\n')
        _exit(10, ftp)

    file_url = 'ftp://%s@%s%s/%s' % (FTP_USER, FTP_HOST, upload_path, ZIP_FILE.split('/')[-1])
    print('upload success %s' % file_url)

    _exit(0, ftp)
