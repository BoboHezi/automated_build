#!/usr/bin/python3
import os
import sys
import time
from ftplib import FTP
from os import path, chdir, getcwd
from re import match

import utils

BEFORE_TARGET_FILE = 'ftp://upload.droi.com/202105/PA508DDR_R40D1_MATE_XLJ/verified/R40D1-PA508DDR-MATE-128-XLJ-JX-0508-V1101/R40D1-PA508DDR-MATE-128-XLJ-JX-0508-V1101_signed_verified_target_files.zip'
BEFORE_FTP_USERNAME = 'HRF'
BEFORE_FTP_PASSWD = 'Freeme*@HRF1012'

AFTER_TARGET_FILE = 'ftp://upload.droi.com/202105/PA508DDR_R40D1_MATE_XLJ/verified/R40D1-PA508DDR-MATE-128-XLJ-JX-0527-V1102/R40D1-PA508DDR-MATE-128-XLJ-JX-0527-V1102_signed_verified_target_files.zip'
AFTER_FTP_USERNAME = 'HRF'
AFTER_FTP_PASSWD = 'Freeme*@HRF1012'

SV_PLATFORM_TERRACE = 'SPRD_T310p_xiaolajiao_heruifeng'

PLATFORM_CMD = {
    'MTK_mt6737m': 'build/tools/releasetools/ota_from_target_files -s device/mediatek/build/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6739n': 'build/tools/releasetools/ota_from_target_files -s device/mediatek/build/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6750n': 'build/tools/releasetools/ota_from_target_files -s device/mediatek/build/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6758n': 'build/tools/releasetools/ota_from_target_files -s device/mediatek/build/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6763o': 'build/tools/releasetools/ota_from_target_files -s vendor/mediatek/proprietary/scripts/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6761p': 'build/tools/releasetools/ota_from_target_files --block -i $before $after update.zip',
    'SPRD_T310p': 'build/tools/releasetools/ota_from_target_files --block -i $before $after update.zip',
    'SPRD_T7510p': 'build/tools/releasetools/ota_from_target_files --block -i $before $after update.zip',
    'SPRD_9832m': 'build/tools/releasetools/ota_from_target_files -i $before $after update.zip',
    'SPRD_9850n': 'build/tools/releasetools/ota_from_target_files -i $before $after update.zip',
    'SPRD_9850o': 'build/tools/releasetools/ota_from_target_files -i $before $after update.zip',
    'SPRD_T610r': 'android_out_host/linux-x86/bin/ota_from_target_files -i $before $after update.zip',
    'SPRD_9832r': 'android_out_host/linux-x86/bin/ota_from_target_files -i $before $after update.zip'
}


def _exit(code=0, ftp=None):
    utils.star_log('otadiff end', 60)
    if ftp:
        ftp.quit()
    exit(code)


# dump info from url
def dump_url(ftp_url):
    ftp_url_ptn = '^ftp://([^/|^:]*)(:[\d]*)?/(.*/)?(.*\.zip)'
    matchObj = match(ftp_url_ptn, ftp_url)
    host = matchObj.group(1) if matchObj else None
    port = int(matchObj.group(2)) if matchObj.group(2) else 21 if matchObj else 21
    path = matchObj.group(3) if matchObj.group(3) else None if matchObj else None
    name = matchObj.group(4) if matchObj.group(4) else None if matchObj else None
    path = '/' if utils.isempty(path) else '/%s' % path
    return {'host': host, 'port': port, 'path': path, "name": name}


# download before & after target file
def download():
    before_ftp = dump_url(BEFORE_TARGET_FILE)
    after_ftp = dump_url(AFTER_TARGET_FILE)

    # before ftp connect & login
    ftp = FTP()
    ftp.connect(before_ftp['host'], before_ftp['port'], 30)
    try:
        ftp.login(BEFORE_FTP_USERNAME, BEFORE_FTP_PASSWD)
        print('\notadiff %s login success' % before_ftp['host'])
    except Exception as e:
        print('\notadiff %s login failed: %s' % (BEFORE_FTP_USERNAME, e))
        return None, None

    # download before target file
    try:
        ftp.cwd(before_ftp['path'])
        before_local_file = open(before_ftp['name'], "wb")
        print('\notadiff %s downloading...' % before_ftp['name'])
        ftp.retrbinary('RETR %s' % before_ftp['name'], before_local_file.write)
        print('\notadiff %s download success' % before_ftp['name'])
    except Exception as e:
        print('\notadiff download failed: %s\n' % e)
        ftp.quit()
        return None, None
    finally:
        before_local_file.close()

    # after ftp connect & login
    if before_ftp['host'] != after_ftp['host'] or before_ftp['port'] != after_ftp[
        'port'] or BEFORE_FTP_USERNAME != AFTER_FTP_USERNAME or BEFORE_FTP_PASSWD != AFTER_FTP_PASSWD:
        ftp.quit()
        ftp.connect(after_ftp['host'], after_ftp['port'], 30)
        try:
            ftp.login(AFTER_FTP_USERNAME, AFTER_FTP_PASSWD)
            print('\notadiff %s login success' % after_ftp['host'])
        except Exception as e:
            print('\notadiff %s login failed: %s' % (AFTER_FTP_USERNAME, e))
            return None, None

    # download after target file
    try:
        ftp.cwd(after_ftp['path'])
        print('\notadiff %s downloading...' % after_ftp['name'])
        after_local_file = open(after_ftp['name'], "wb")
        ftp.retrbinary('RETR %s' % after_ftp['name'], after_local_file.write)
        print('\notadiff %s download success' % after_ftp['name'])
    except Exception as e:
        print('\notadiff %s download failed: %s\n' % (after_ftp['name'], e))
        return None, None
    finally:
        after_local_file.close()
        ftp.quit()
    return path.abspath(before_local_file.name), path.abspath(after_local_file.name)


def upload_package():
    before_ftp = dump_url(BEFORE_TARGET_FILE)
    after_ftp = dump_url(AFTER_TARGET_FILE)

    # after ftp connect & login
    ftp = FTP()
    ftp.connect(after_ftp['host'], after_ftp['port'], 30)
    try:
        ftp.login(AFTER_FTP_USERNAME, AFTER_FTP_PASSWD)
        print('\notadiff %s login success' % after_ftp['host'])
    except Exception as e:
        print('\notadiff %s login failed: %s' % (BEFORE_FTP_USERNAME, e))
        return None

    before_verno = before_ftp['name'][0: before_ftp['name'].find('_signed_verified_target_files.zip')]
    after_verno = after_ftp['name'][0: after_ftp['name'].find('_signed_verified_target_files.zip')]
    upload_path = '%s%s--%s' % (after_ftp['path'], before_verno, after_verno)
    # mkd and enter
    try:
        if upload_path not in ftp.nlst(after_ftp['path']):
            ftp.mkd(upload_path)
        ftp.cwd(upload_path)
        print('\notadiff now in %s' % upload_path)
    except Exception as e:
        print('\notadiff mkd failed: %s' % e)
        ftp.quit()
        return None

    # upload
    try:
        time_mark = time.strftime('%m_%d_%H_%M', time.localtime())
        package_zip = '%s_%s' % (time_mark, 'package.zip')
        update_zip = '%s_%s' % (time_mark, 'update.zip')
        ftp.storbinary('STOR ' + path.basename(package_zip), open('package.zip', 'rb'), 1024)
        ftp.storbinary('STOR ' + path.basename(update_zip), open('update.zip', 'rb'), 1024)
        print('\notadiff upload success')
        return 'ftp://%s@%s%s/%s' % (AFTER_FTP_USERNAME, after_ftp['host'], upload_path, package_zip)
    except Exception as e:
        print('\notadiff upload failed: %s' % e)
        return None


if __name__ == '__main__':
    utils.star_log('otadiff start', 60)
    option_str = ''
    option_str += 'f-bfile:'  # BEFORE_TARGET_FILE
    option_str += ',u-buser:'  # BEFORE_FTP_USERNAME
    option_str += ',p-bpasswd:'  # BEFORE_FTP_PASSWD
    option_str += ',i-afile:'  # AFTER_TARGET_FILE
    option_str += ',s-auser:'  # AFTER_FTP_USERNAME
    option_str += ',a-apasswd:'  # AFTER_FTP_PASSWD
    option_str += ',t-terrace:'  # SV_PLATFORM_TERRACE

    opts = utils.dump(sys.argv[1:], option_str)

    if not opts:
        print("otadiff wrong parameter try '-h or --help' to get more information")
        _exit(1)

    # dump argv
    if '-f' in opts or '--bfile' in opts:
        BEFORE_TARGET_FILE = opts.get('-f') if opts.get('-f') else opts.get('--bfile')
    if '-u' in opts or '--buser' in opts:
        BEFORE_FTP_USERNAME = opts.get('-u') if opts.get('-u') else opts.get('--buser')
    if '-p' in opts or '--bpasswd' in opts:
        BEFORE_FTP_PASSWD = opts.get('-p') if opts.get('-p') else opts.get('--bpasswd')
    if '-i' in opts or '--afile' in opts:
        AFTER_TARGET_FILE = opts.get('-i') if opts.get('-i') else opts.get('--afile')
    if '-s' in opts or '--auser' in opts:
        AFTER_FTP_USERNAME = opts.get('-s') if opts.get('-s') else opts.get('--auser')
    if '-a' in opts or '--apasswd' in opts:
        AFTER_FTP_PASSWD = opts.get('-a') if opts.get('-a') else opts.get('--apasswd')
    if '-t' in opts or '--terrace' in opts:
        SV_PLATFORM_TERRACE = opts.get('-t') if opts.get('-t') else opts.get('--terrace')

    print(
        """
        BEFORE_TARGET_FILE:    %s
        BEFORE_FTP_USERNAME:   %s
        BEFORE_FTP_PASSWD:     %s
        AFTER_TARGET_FILE:     %s
        AFTER_FTP_USERNAME:    %s
        AFTER_FTP_PASSWD:      %s
        SV_PLATFORM_TERRACE:   %s
        """ % (BEFORE_TARGET_FILE, BEFORE_FTP_USERNAME, BEFORE_FTP_PASSWD, AFTER_TARGET_FILE, AFTER_FTP_USERNAME,
               AFTER_FTP_PASSWD, SV_PLATFORM_TERRACE))

    if utils.isempty(BEFORE_TARGET_FILE) or utils.isempty(BEFORE_FTP_USERNAME) or utils.isempty(BEFORE_FTP_PASSWD) or \
            utils.isempty(AFTER_TARGET_FILE) or utils.isempty(AFTER_FTP_USERNAME) or \
            utils.isempty(AFTER_FTP_PASSWD) or utils.isempty(SV_PLATFORM_TERRACE) or \
            not BEFORE_TARGET_FILE.endswith('_signed_verified_target_files.zip') or \
            not AFTER_TARGET_FILE.endswith('_signed_verified_target_files.zip'):
        print("otadiff wrong parameter")
        _exit(1)

    # download target files
    before, after = download()
    if utils.isempty(before) or utils.isempty(after):
        print('\notadiff download failed.')
        _exit(2)

    # enter platform
    ary = SV_PLATFORM_TERRACE.split('_')
    platform = '%s_%s' % (ary[0], ary[1]) if ary and len(ary) > 1 else None
    print('\notadiff platform: %s' % platform)
    if not (platform and (path.isdir(platform) or path.islink(platform))):
        print('\notadiff folder platform: %s not found!' % platform)
        _exit(3)
    chdir(platform)
    print('\notadiff now in %s' % getcwd())

    # found cmd
    cmd = PLATFORM_CMD[platform] if platform in PLATFORM_CMD else None
    if utils.isempty(cmd):
        print('\notadiff folder cmd not found!')
        _exit(4)

    # remove package.zip & update.zip
    utils.removedirs('package.zip')
    utils.removedirs('update.zip')

    # execute
    cmd = cmd.replace('$before', before, 1).replace('$after', after, 1)
    print('\notadiff cmd: %s\n' % cmd)
    utils.star_log('make ota start', 60)
    process, rst = utils.async_command(cmd)
    # rst, msg = utils.execute(cmd)
    utils.star_log('make ota end', 60)
    if rst != 0:
        print('\notadiff ota cmd failed' % cmd)
        _exit(5)

    if path.isfile('package.zip') and path.isfile('update.zip'):
        package_zip_stat = os.stat('package.zip')
        update_zip_stat = os.stat('update.zip')
        current_time = time.time()

        print('''
        otadiff package.zip modify time: %s
        otadiff update.zip modify time:  %s
        otadiff current_time:            %s
        ''' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(package_zip_stat.st_mtime)),
               time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(update_zip_stat.st_mtime)),
               time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))))

        if current_time - package_zip_stat.st_mtime < 60 and current_time - update_zip_stat.st_mtime < 60:
            package_zip_url = upload_package()
            print('\notadiff %s' % package_zip_url)
