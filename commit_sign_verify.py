#!/usr/bin/python
# -*- coding: utf-8 -*-
from commands import getstatusoutput
from ftplib import FTP
from os import path
from os import readlink
import sys
import re
import time
import utils

def _exit(code):
    print('*' * 15 + 'commit sign verify end' + '*' * 15)
    exit(code)

PROJECT_NAME = None
# 签名包地址
SV_FTP_PATH = None
# 签名验收后台
SV_URL = 'http://192.168.151.31:8084/'
# 签名账号用户
SV_USERNAME = None
# 签名账号密码
SV_PASSWD = None
# 签名平台
SV_PLATFORM = None
# 主板
SV_BOARD = None
# 抄送地址
SV_CCLIST = None
# 机型
SV_MODEL = None
# 品牌商
SV_BRAND_CUSTOMER = None
# 方案商
SV_ODM_CUSTOMER = None
# 是否验收
SV_BUILD_VERITY = None
# 验收包释放用户
SV_FTP_PUBLISH_USERNAME = None

if ( __name__ == "__main__"):
    print('*' * 15 + 'commit sign verify start' + '*' * 15)
    option_str = ''
    option_str += 'p-project:'  # PROJECT_NAME
    option_str += ',f-ftp:'     # SV_FTP_PATH
    option_str += ',u-url:'     # SV_URL
    option_str += ',s-user:'    # SV_USERNAME
    option_str += ',c-code:'    # SV_PASSWD
    option_str += ',t-terrace:' # SV_PLATFORM
    option_str += ',b-board:'   # SV_BOARD
    option_str += ',l-cclist:'  # SV_CCLIST
    option_str += ',m-model:'   # SV_MODEL
    option_str += ',b-brand:'   # SV_BRAND_CUSTOMER
    option_str += ',o-odem:'    # SV_ODM_CUSTOMER
    option_str += ',v-verity'   # SV_BUILD_VERITY
    option_str += ',i-publish:' # SV_FTP_PUBLISH_USERNAME
    opts = utils.dump(sys.argv[1:], option_str)
    # print(opts)

    if not opts:
        print("commit_sign_verify wrong parameter")
        _exit(1)

    if opts.has_key('-p') or opts.has_key('--project'):
        PROJECT_NAME = opts.get('-p') if opts.get('-p') else opts.get('--project')
    if opts.has_key('-f') or opts.has_key('--ftp'):
        SV_FTP_PATH = opts.get('-f') if opts.get('-f') else opts.get('--ftp')
    if opts.has_key('-u') or opts.has_key('--url'):
        SV_URL = opts.get('-u') if opts.get('-u') else opts.get('--url')
    if opts.has_key('-s') or opts.has_key('--user'):
        SV_USERNAME = opts.get('-s') if opts.get('-s') else opts.get('--user')
    if opts.has_key('-c') or opts.has_key('--code'):
        SV_PASSWD = opts.get('-c') if opts.get('-c') else opts.get('--code')
    if opts.has_key('-t') or opts.has_key('--terrace'):
        SV_PLATFORM = opts.get('-t') if opts.get('-t') else opts.get('--terrace')
    if opts.has_key('-b') or opts.has_key('--board'):
        SV_BOARD = opts.get('-b') if opts.get('-b') else opts.get('--board')
    if opts.has_key('-l') or opts.has_key('--cclist'):
        SV_CCLIST = opts.get('-l') if opts.get('-l') else opts.get('--cclist')
    if opts.has_key('-m') or opts.has_key('--model'):
        SV_MODEL = opts.get('-m') if opts.get('-m') else opts.get('--model')
    if opts.has_key('-b') or opts.has_key('--brand'):
        SV_BRAND_CUSTOMER = opts.get('-b') if opts.get('-b') else opts.get('--brand')
    if opts.has_key('-o') or opts.has_key('--odem'):
        SV_ODM_CUSTOMER = opts.get('-o') if opts.get('-o') else opts.get('--odem')
    if opts.has_key('-v') or opts.has_key('--verity'):
        SV_BUILD_VERITY = opts.get('-v') if opts.get('-v') else opts.get('--verity')
    if opts.has_key('-i') or opts.has_key('--publish'):
        SV_FTP_PUBLISH_USERNAME = opts.get('-i') if opts.get('-i') else opts.get('--publish')

        print(
    """
    PROJECT_NAME:            %s
    SV_FTP_PATH:             %s
    SV_URL:                  %s
    SV_USERNAME:             %s
    SV_PASSWD:               %s
    SV_PLATFORM:             %s
    SV_BOARD:                %s
    SV_CCLIST:               %s
    SV_MODEL:                %s
    SV_BRAND_CUSTOMER:       %s
    SV_ODM_CUSTOMER:         %s
    SV_BUILD_VERITY:         %s
    SV_FTP_PUBLISH_USERNAME: %s
    """ % (PROJECT_NAME, SV_FTP_PATH, SV_URL, SV_USERNAME, SV_PASSWD, 
        SV_PLATFORM, SV_BOARD, SV_CCLIST, SV_MODEL, SV_BRAND_CUSTOMER,
        SV_ODM_CUSTOMER, SV_BUILD_VERITY, SV_FTP_PUBLISH_USERNAME))

    if not (PROJECT_NAME and SV_FTP_PATH):
        print('commit_sign_verify miss importent parameter\n')
        _exit(2)

    project = utils.dump_project(PROJECT_NAME)

    print(project)
