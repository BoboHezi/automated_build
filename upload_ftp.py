#!/usr/bin/python3
import sys
import time
from ftplib import FTP
from os import path

import utils


def _exit(code, ftp=None):
    utils.star_log('upload ftp end', 60)
    if ftp:
        ftp.quit()
    exit(code)


PROJECT_NAME = None
ZIP_FILE = None
FTP_HOST = '192.168.150.30'
FTP_USER = 'hongxiangyuan'
FTP_PWD = 'hongxiangyuan014'


def main(argv):
    utils.star_log('upload ftp start', 60)
    utils.execute('echo "" > ftp_url.txt')
    option_str = 'p-project:,f-file:,h-host:,u-user:,c-code:'
    opts = utils.dump(argv, option_str)

    if not opts:
        print("upload_ftp wrong parameter try '-h or --help' to get more information")
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
        print('upload_ftp must specify project(use -p or --project)\n')
        return 3, None

    # check MTK or SPRD
    PLATFORM = utils.dump_platform()

    if not PLATFORM:
        print('upload_ftp platform check failed\n')
        return 5, None
    print('upload_ftp platform: %s\n' % PLATFORM)

    # find project first
    find_cmd = 'find droi/ -maxdepth 3 -mindepth 3 -type d -name %s' % PROJECT_NAME
    status, project_path = utils.execute(find_cmd)

    if status or not project_path or not path.exists(project_path + '/ProjectConfig.mk'):
        print('upload_ftp %s not found\n' % PROJECT_NAME)
        return 6, None
    print('upload_ftp project: %s found %s\n' % (PROJECT_NAME, project_path))

    # find build config file
    build_config_file = utils.get_option_val('mk', 'readonly BUILD_INFO_FILE').replace('\'', '')
    if utils.isempty(build_config_file) or not path.isfile(build_config_file):
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

    # if zip doesn't exist, try find
    if not path.isfile(ZIP_FILE):
        code, rst = utils.execute('find %s -type f -name "*%s*".zip' % (publish_out, verno_internal))
        if code == 0 and not utils.isempty(rst):
            ZIP_FILE = rst.split('\n')[0]

    if not path.isfile(ZIP_FILE):
        print('upload_ftp check ZIP_FILE: %s failed\n' % ZIP_FILE)
        return 7, None
    print('upload_ftp ZIP_FILE: %s\n' % ZIP_FILE)

    date_str = time.strftime('%Y%m', time.localtime())
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
        return 8, ftp
    print

    # check remote dir & cwd
    try:
        ftp.cwd(upload_path)
    except Exception as e:
        print('upload_ftp cwd failed, try mkd\n')
        try:
            ftp.cwd('~')
            base_dir = ftp.pwd()
            for p in upload_path.split('/'):
                if utils.isempty(p):
                    continue
                base_dir = base_dir + p + '/'
                try:
                    ftp.cwd(base_dir)
                except Exception as e:
                    ftp.mkd(base_dir)
            ftp.cwd(upload_path)
        except Exception as e:
            print('upload_ftp mkd failed\n')
            return 9, ftp
    print('upload_ftp remote dir: %s\n' % ftp.pwd())

    # upload
    print('upload_ftp start upload file\n')
    try:
        ftp.storbinary('STOR ' + path.basename(ZIP_FILE), open(ZIP_FILE, 'rb'), 1024)
    except Exception as e:
        print('upload_ftp upload failed\n')
        return 10, ftp

    file_url = 'ftp://%s@%s%s/%s' % (FTP_USER, FTP_HOST, upload_path, ZIP_FILE.split('/')[-1])
    print('upload success %s' % file_url)
    utils.execute('echo "%s" > ftp_url.txt' % file_url)

    # delete publish package
    utils.removedirs(publish_out)

    # repoclean
    clean_cmd = 'repo forall -c \'echo "$REPO_PATH ($REPO_REMOTE)"; git clean -fd; git reset --hard;\''
    utils.async_command(clean_cmd)
    utils.removedirs('out')

    return 0, ftp


if __name__ == '__main__':
    r, f = main(sys.argv[1:])
    _exit(r, f)
