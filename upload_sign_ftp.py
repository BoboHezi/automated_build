#!/usr/bin/python3
import sys
import time
import upload_ftp
from ftplib import FTP
from os import path
from re import search

import utils


def _exit(code, ftp=None):
    utils.star_log('upload signed ftp end', 60)
    if ftp:
        ftp.quit()
    exit(code)


PROJECT_NAME = None
ZIP_FILE = None
FTP_HOST = '192.168.150.30'
FTP_USER = 'hongxiangyuan'
FTP_PWD = 'hongxiangyuan014'


def main(argv):
    utils.star_log('upload signed ftp start', 60)
    option_str = 'p-project:,f-file:,h-host:,u-user:,c-code:'
    opts = utils.dump(argv, option_str)

    if not opts:
        print("upload_sign_ftp wrong parameter try '-h or --help' to get more information")
        return 1, None
    global PROJECT_NAME, ZIP_FILE, FTP_HOST, FTP_USER, FTP_PWD
    if '-p' in opts or '--project' in opts:
        PROJECT_NAME = opts.get('-p') if opts.get('-p') else opts.get('--project')
    if '-f' in opts or '--file' in opts:
        ZIP_FILE = opts.get('-f') if opts.get('-f') else opts.get('--file')
    if '-h' in opts or '--host' in opts:
        ftp_host = opts.get('-h') if opts.get('-h') else opts.get('--host')
        FTP_HOST = ftp_host if ftp_host else FTP_HOST
    if '-u' in opts or '--user' in opts:
        ftp_user = opts.get('-u') if opts.get('-u') else opts.get('--user')
        FTP_USER = ftp_user if ftp_user else FTP_USER
    if '-c' in opts or '--code' in opts:
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
        print('upload_sign_ftp must specify project(use -p or --project)\n')
        return 3, None

    # check MTK or SPRD
    PLATFORM = utils.dump_platform()

    if not PLATFORM:
        print('upload_sign_ftp platform check failed\n')
        return 5, None
    print('upload_sign_ftp platform: %s\n' % PLATFORM)

    # find project first
    find_cmd = 'find droi/ -maxdepth 3 -mindepth 3 -type d -name %s' % PROJECT_NAME
    status, project_path = utils.execute(find_cmd)

    if status or not project_path or not path.exists(project_path + '/ProjectConfig.mk'):
        print('upload_sign_ftp %s not found\n' % PROJECT_NAME)
        return 6, None
    print('upload_sign_ftp project: %s found %s\n' % (PROJECT_NAME, project_path))

    # find build config file
    build_config_file = utils.get_option_val('mk', 'readonly BUILD_INFO_FILE').replace('\'', '')
    if utils.isempty(build_config_file) or not path.isfile(build_config_file):
        build_config_file = '%s/ProjectConfig.mk' % project_path
    project_product = utils.get_option_val(build_config_file, 'product')
    if utils.isempty(project_product):
        project_product = utils.get_option_val(build_config_file, 'project')
    if not utils.isempty(project_product) and project_product.startswith('full_'):
        project_product = project_product[5:]
    if utils.isempty(project_product) or project_product != PROJECT_NAME:
        build_config_file = '%s/ProjectConfig.mk' % project_path
    print('upload_sign_ftp build_config_file: %s\n' % build_config_file)

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
        # remove str after [space]
        if ' ' in ZIP_FILE:
            ZIP_FILE = '%s.zip' % ZIP_FILE.split(' ')[0]

    # if zip doesn't exist, try find
    if not path.isfile(ZIP_FILE):
        code, rst = utils.execute('find %s -type f -name "*%s*".zip' % (publish_out, verno_internal))
        if code == 0 and not utils.isempty(rst):
            ZIP_FILE = rst.split('\n')[0]

    if not path.isfile(ZIP_FILE):
        print('upload_sign_ftp check ZIP_FILE: %s failed\n' % ZIP_FILE)
        return 7, None
    print('upload_sign_ftp ZIP_FILE: %s\n' % ZIP_FILE)

    date_str = time.strftime('%Y%m', time.localtime())
    upload_path = '/upload/%s/%s' % (date_str, PROJECT_NAME.upper())
    print('upload_sign_ftp upload_path: %s' % upload_path)

    # upload by upload_ftp.py
    argv = ['-h', FTP_HOST, '-u', FTP_USER, '-c', FTP_PWD, '-l', ZIP_FILE, '-r', upload_path]
    rst, ftp = upload_ftp.main(argv)
    if rst is not 0:
        return rst, ftp

    file_url = 'ftp://%s@%s%s/%s' % (FTP_USER, FTP_HOST, upload_path, ZIP_FILE.split('/')[-1])
    print('upload_sign_ftp upload success %s' % file_url)
    utils.place_config(build_config_file, 'IMP_FTP_URL', file_url)

    # delete publish package
    utils.removedirs(publish_out)

    # remove out if necessary
    # c, t = utils.execute('df $PWD')
    # if c == 0 and not utils.isempty(t):
    #     match = search('[ ]+([0-9]+)[ ]+([0-9]+)[ ]+([0-9]+)[ ]+[^ ]*[ ]([^ ]*)', t)
    #     if match and match.group(3):
    #         available = int(match.group(3))
    #         if available < 200 * 1024 * 1024:
    #             print('upload_sign_ftp df: %s' % t.split('\n')[1])
    #             utils.async_command('[ -d out ] && rm -rf out')

    return 0, None


if __name__ == '__main__':
    r, f = main(sys.argv[1:])
    _exit(r, f)
