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

DEVOPS_OTA_TASK_ID = None

PLATFORM_CMD = {
    'MTK_mt6737m': 'build/tools/releasetools/ota_from_target_files -s device/mediatek/build/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6737n': 'build/tools/releasetools/ota_from_target_files -s device/mediatek/build/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6739n': 'build/tools/releasetools/ota_from_target_files -s device/mediatek/build/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6750n': 'build/tools/releasetools/ota_from_target_files -s device/mediatek/build/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6758n': 'build/tools/releasetools/ota_from_target_files -s device/mediatek/build/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6739o': 'build/tools/releasetools/ota_from_target_files -s vendor/mediatek/proprietary/scripts/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6750o': 'build/tools/releasetools/ota_from_target_files -s vendor/mediatek/proprietary/scripts/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6753o': 'build/tools/releasetools/ota_from_target_files -s vendor/mediatek/proprietary/scripts/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6763o': 'build/tools/releasetools/ota_from_target_files -s vendor/mediatek/proprietary/scripts/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6771o': 'build/tools/releasetools/ota_from_target_files -s vendor/mediatek/proprietary/scripts/releasetools/mt_ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6757p': 'build/tools/releasetools/ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6761p': 'build/tools/releasetools/ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6763p': 'build/tools/releasetools/ota_from_target_files --block -i $before $after update.zip',
    'MTK_mt6771p': 'build/tools/releasetools/ota_from_target_files --block -i $before $after update.zip',
    'SPRD_T310p': 'build/tools/releasetools/ota_from_target_files --block -i $before $after update.zip',
    'SPRD_T7510p': 'build/tools/releasetools/ota_from_target_files --block -i $before $after update.zip',
    'SPRD_7731m': 'build/tools/releasetools/ota_from_target_files -i $before $after update.zip',
    'SPRD_9830l': 'build/tools/releasetools/ota_from_target_files -i $before $after update.zip',
    'SPRD_9832m': 'build/tools/releasetools/ota_from_target_files -i $before $after update.zip',
    'SPRD_9850n': 'build/tools/releasetools/ota_from_target_files -i $before $after update.zip',
    'SPRD_9850o': 'build/tools/releasetools/ota_from_target_files -i $before $after update.zip',
    'SPRD_9863p': 'build/tools/releasetools/ota_from_target_files --block -i $before $after update.zip',
    'SPRD_T610r': 'android_out_host/linux-x86/bin/ota_from_target_files -i $before $after update.zip',
    'SPRD_9832r': 'android_out_host/linux-x86/bin/ota_from_target_files -i $before $after update.zip'
}

BEFORE_FTP = None
AFTER_FTP = None
OTA_URL = None


def _exit(code=0, ftp=None):
    http_notify(DEVOPS_OTA_TASK_ID, code, '' if code else OTA_URL)
    utils.star_log('otadiff end', 60)
    if ftp:
        ftp.quit()
    exit(code)


def http_notify(id, status, otaDir):
    token = os.getenv('DEVOPS_TOKEN')
    build_url = os.getenv('BUILD_URL')
    if not utils.isempty(token):
        url = '%s%s?id=%s&status=%s&otaDir=%s&otaLogUrl=%s' % \
              (utils.DEVOPS_HTTP_URL, utils.OTA_STATUS_PATH, id, status, otaDir, '%sconsole' % build_url)
        print('\notadiff url: %s' % url)
        headers = {
            'X-Access-Token': token
        }
        http_code, response = utils.get(url, None, headers=headers)
        if http_code == 200:
            try:
                code = response['code']
                success = response['success']
                if code == 200 and success:
                    print('otadiff: update "%s" success' % status)
            except Exception as e:
                print('otadiff: Exception %s' % e)
        else:
            print('otadiff: http_code: %s, response:\n%s' % (http_code, response))


# dump info from url
def dump_url(ftp_url):
    ftp_url_ptn = '^ftp://([^/|^:]*)(:[\d]+)?/(.*/)?(.*\.zip)'
    matchObj = match(ftp_url_ptn, ftp_url)
    if matchObj:
        host = matchObj.group(1) if matchObj.group(1) else None
        if host and '@' in host:
            host = host.split('@')[1]
        port = int(matchObj.group(2)[1:]) if matchObj.group(2) and len(matchObj.group(2)) > 1 else 21
        path = matchObj.group(3) if matchObj.group(3) else None
        path = '/' if utils.isempty(path) else '/%s' % path
        name = matchObj.group(4) if matchObj.group(4) else None
        return {'host': host, 'port': port, 'path': path, "name": name}


# download before & after target file
def download():
    # before ftp connect & login
    ftp = FTP()
    ftp.connect(BEFORE_FTP['host'], BEFORE_FTP['port'], 30)
    try:
        ftp.login(BEFORE_FTP_USERNAME, BEFORE_FTP_PASSWD)
        print('\notadiff %s login success' % BEFORE_FTP['host'])
    except Exception as e:
        print('\notadiff %s login failed: %s' % (BEFORE_FTP_USERNAME, e))
        return None, None

    # download before target file
    try:
        before_local_file = open(BEFORE_FTP['name'], "wb")
        ftp.cwd(BEFORE_FTP['path'])
        print('\notadiff %s downloading...' % BEFORE_FTP['name'])
        ftp.retrbinary('RETR %s' % BEFORE_FTP['name'], before_local_file.write)
        print('\notadiff %s download success' % BEFORE_FTP['name'])
    except Exception as e:
        print('\notadiff download failed: %s\n' % e)
        ftp.quit()
        return None, None
    finally:
        before_local_file.close()

    # after ftp connect & login
    if BEFORE_FTP['host'] != AFTER_FTP['host'] or BEFORE_FTP['port'] != AFTER_FTP[
        'port'] or BEFORE_FTP_USERNAME != AFTER_FTP_USERNAME or BEFORE_FTP_PASSWD != AFTER_FTP_PASSWD:
        ftp.quit()
        ftp.connect(AFTER_FTP['host'], AFTER_FTP['port'], 30)
        try:
            ftp.login(AFTER_FTP_USERNAME, AFTER_FTP_PASSWD)
            print('\notadiff %s login success' % AFTER_FTP['host'])
        except Exception as e:
            print('\notadiff %s login failed: %s' % (AFTER_FTP_USERNAME, e))
            return None, None

    # download after target file
    try:
        after_local_file = open(AFTER_FTP['name'], "wb")
        ftp.cwd(AFTER_FTP['path'])
        print('\notadiff %s downloading...' % AFTER_FTP['name'])
        ftp.retrbinary('RETR %s' % AFTER_FTP['name'], after_local_file.write)
        print('\notadiff %s download success' % AFTER_FTP['name'])
    except Exception as e:
        print('\notadiff %s download failed: %s\n' % (AFTER_FTP['name'], e))
        return None, None
    finally:
        after_local_file.close()
        ftp.quit()
    return path.abspath(before_local_file.name), path.abspath(after_local_file.name)


def upload_package():
    # after ftp connect & login
    ftp = FTP()
    ftp.connect(AFTER_FTP['host'], AFTER_FTP['port'], 30)
    try:
        ftp.login(AFTER_FTP_USERNAME, AFTER_FTP_PASSWD)
        print('\notadiff %s login success' % AFTER_FTP['host'])
    except Exception as e:
        print('\notadiff %s login failed: %s' % (BEFORE_FTP_USERNAME, e))
        return None

    suf_index = BEFORE_FTP['name'].find('_signed_verified_target_files.zip')
    suf_index = suf_index if suf_index != -1 else BEFORE_FTP['name'].find('_signed_target_files.zip')
    suf_index = suf_index if suf_index != -1 else BEFORE_FTP['name'].find('_target_files.zip')
    suf_index = suf_index if suf_index != -1 else len(BEFORE_FTP['name'])
    before_verno = BEFORE_FTP['name'][0: suf_index]
    suf_index = AFTER_FTP['name'].find('_signed_verified_target_files.zip')
    suf_index = suf_index if suf_index != -1 else AFTER_FTP['name'].find('_signed_target_files.zip')
    suf_index = suf_index if suf_index != -1 else AFTER_FTP['name'].find('_target_files.zip')
    suf_index = suf_index if suf_index != -1 else len(AFTER_FTP['name'])
    after_verno = AFTER_FTP['name'][0: suf_index]
    upload_path = '%s%s--%s' % (AFTER_FTP['path'], before_verno, after_verno)
    # mkd and enter
    try:
        ftp.cwd(upload_path)
    except Exception as e:
        print('\notadiff cwd failed: %s, try mkd\n' % e)
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
        return 'ftp://%s@%s%s/%s' % (AFTER_FTP_USERNAME, AFTER_FTP['host'], upload_path, package_zip)
    except Exception as e:
        print('\notadiff upload failed: %s' % e)
        return None


def main(argv):
    utils.star_log('otadiff start', 60)
    option_str = ''
    option_str += 'f-bfile:'  # BEFORE_TARGET_FILE
    option_str += ',u-buser:'  # BEFORE_FTP_USERNAME
    option_str += ',p-bpasswd:'  # BEFORE_FTP_PASSWD
    option_str += ',i-afile:'  # AFTER_TARGET_FILE
    option_str += ',s-auser:'  # AFTER_FTP_USERNAME
    option_str += ',a-apasswd:'  # AFTER_FTP_PASSWD
    option_str += ',t-terrace:'  # SV_PLATFORM_TERRACE
    option_str += ',d-id:'  # DEVOPS_OTA_TASK_ID

    opts = utils.dump(argv, option_str)

    if not opts:
        print("otadiff wrong parameter try '-h or --help' to get more information")
        return 4, None

    global BEFORE_TARGET_FILE, BEFORE_FTP_USERNAME, BEFORE_FTP_PASSWD, AFTER_TARGET_FILE, AFTER_FTP_USERNAME, \
        AFTER_FTP_PASSWD, SV_PLATFORM_TERRACE, DEVOPS_OTA_TASK_ID

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
    if '-d' in opts or '--id' in opts:
        DEVOPS_OTA_TASK_ID = opts.get('-d') if opts.get('-d') else opts.get('--id')

    print(
        """
        BEFORE_TARGET_FILE:    %s
        BEFORE_FTP_USERNAME:   %s
        BEFORE_FTP_PASSWD:     %s
        AFTER_TARGET_FILE:     %s
        AFTER_FTP_USERNAME:    %s
        AFTER_FTP_PASSWD:      %s
        SV_PLATFORM_TERRACE:   %s
        DEVOPS_OTA_TASK_ID:    %s
        """ % (BEFORE_TARGET_FILE, BEFORE_FTP_USERNAME, BEFORE_FTP_PASSWD, AFTER_TARGET_FILE, AFTER_FTP_USERNAME,
               AFTER_FTP_PASSWD, SV_PLATFORM_TERRACE, DEVOPS_OTA_TASK_ID))

    if utils.isempty(BEFORE_TARGET_FILE) or utils.isempty(BEFORE_FTP_USERNAME) or utils.isempty(BEFORE_FTP_PASSWD) or \
            utils.isempty(AFTER_TARGET_FILE) or utils.isempty(AFTER_FTP_USERNAME) or \
            utils.isempty(AFTER_FTP_PASSWD) or utils.isempty(SV_PLATFORM_TERRACE) or \
            not BEFORE_TARGET_FILE.endswith('_target_files.zip') or \
            not AFTER_TARGET_FILE.endswith('_target_files.zip'):
        print("otadiff wrong parameter")
        return 4, None

    # notify processing & log url
    http_notify(DEVOPS_OTA_TASK_ID, 2, '')

    global BEFORE_FTP, AFTER_FTP
    # dump ftp url
    BEFORE_FTP = dump_url(BEFORE_TARGET_FILE)
    AFTER_FTP = dump_url(AFTER_TARGET_FILE)

    # download target files
    before, after = download()
    if utils.isempty(before) or utils.isempty(after):
        print('\notadiff download failed.')
        return 5, None

    # enter platform
    ary = SV_PLATFORM_TERRACE.split('_')
    platform = '%s_%s' % (ary[0], ary[1]) if ary and len(ary) > 1 else None
    print('\notadiff platform: %s' % platform)
    if not (platform and (path.isdir(platform) or path.islink(platform))):
        print('\notadiff folder platform: %s not found!' % platform)
        return 6, None
    chdir(platform)
    print('\notadiff now in %s' % getcwd())

    # found cmd
    cmd = PLATFORM_CMD[platform] if platform in PLATFORM_CMD else None
    if utils.isempty(cmd):
        print('\notadiff folder cmd not found!')
        return 7, None

    # remove package.zip & update.zip
    utils.removedirs('package.zip')
    utils.removedirs('update.zip')

    # execute
    cmd = cmd.replace('$before', before, 1).replace('$after', after, 1)
    cmd = cmd.replace('(', '\(').replace(')', '\)')
    print('\notadiff cmd: %s\n' % cmd)
    utils.star_log('make ota start', 60)
    process, rst = utils.async_command(cmd)
    # rst, msg = utils.execute(cmd)
    utils.star_log('make ota end', 60)
    if rst != 0:
        print('\notadiff ota cmd failed')
        return 3, None

    # remove target files
    utils.removedirs('../%s' % BEFORE_FTP['name'])
    utils.removedirs('../%s' % AFTER_FTP['name'])

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
            global OTA_URL
            OTA_URL = upload_package()
            print('\notadiff %s' % OTA_URL)
            if not utils.isempty(OTA_URL):
                return 0, None
    return 8, None


if __name__ == '__main__':
    r, f = main(sys.argv[1:])
    _exit(r, f)
