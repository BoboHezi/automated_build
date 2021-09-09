#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import sys
from os import path

import update_db
import utils


def _exit(code):
    utils.star_log('commit sign verify end', 60)
    exit(code)


PROJECT_NAME = None
# 签名包地址
SV_FTP_PATH = None
# 签名验收后台
SV_URL = 'http://192.168.151.31:8084'
# 签名账号用户
SV_USERNAME = 'hongxiangyuan'
USER_ID = None
# 签名账号密码
SV_PASSWD = 'hongxiangyuan014'
# 签名平台
SV_PLATFORM = None
# 主板
SV_BOARD = None
# 抄送地址
SV_CCLIST = None
# 机型
SV_MODEL = None
MODEL_ID = None
# 品牌商
SV_BRAND_CUSTOMER = None
BRAND_ID = None
# 方案商
SV_ODM_CUSTOMER = None
ODM_ID = None
# 项目
PROJECT_ID = None
# 是否验收
SV_BUILD_VERITY = False
# 验收包释放用户
SV_FTP_PUBLISH_USERNAME = None
# 验收用途
SV_VERITY_PURPOSE = 'official'
# 编译任务ID
DEVOPS_COMPILE_ID = None
# 优先级
SV_VERITY_LEVEL = 0

TOKEN = None


# check item by specified attribute and return id
def check_item(user_id=USER_ID, name=None, keyword=None, url=None, headers=utils.common_headers, extra=None):
    if utils.isempty(user_id) or utils.isempty(keyword) or utils.isempty(url):
        return

    request_data = {
        'pageNo': 1,
        'pageSize': 20,
        'searchParam': {
            'commonField': keyword
        },
        'userid': user_id
    }

    if extra and len(extra) > 0:
        del request_data['searchParam']['commonField']
        for key, value in extra.items():
            request_data['searchParam'][key] = value

    status, response = utils.post(url, request_data, headers)
    if status == 200:
        try:
            code = response['code']
            msg = response['msg']

            if code == 1000 and msg == 'SUCCESS':
                datas = response['data']['data']
                if len(datas) == 1:
                    return datas[0]
                elif len(datas) > 1:
                    for item in datas:
                        if extra and len(extra) > 0:
                            flag = True
                            for key, value in extra.items():
                                if not utils.equals_ignore_case(item[key], value):
                                    flag = False
                                    break
                            if flag:
                                return item
                        elif not utils.isempty(keyword):
                            if utils.equals_ignore_case(item[name], keyword):
                                return item
        except Exception as e:
            print('commit_sign_verify check %s: %s, %s' % (name, keyword, e))
        finally:
            pass


# create item by specified attribute and return json data
def create_item(request_data=None, user=USER_ID, url=None, headers=utils.common_headers):
    if not request_data or len(request_data) < 1 or utils.isempty(url):
        return

    request_data['userId1'] = user
    status, response = utils.post(url, request_data, headers)
    if status == 200:
        try:
            code = response['code']
            msg = response['msg']
            if code == 1000 and msg == 'SUCCESS':
                data = response['data']
                if data:
                    return data
        finally:
            pass


# check model(机型) and return id
def check_model(model=SV_MODEL, user=USER_ID, headers=utils.common_headers):
    data = check_item(user, 'model', model, '%s/sv/models/list' % SV_URL, headers)
    if data:
        try:
            rst_model = data['model']
            if rst_model and utils.equals_ignore_case(rst_model, model):
                return data['id']
        finally:
            pass


# check odm(方案商) and return id
def check_odm(odm=SV_ODM_CUSTOMER, user=USER_ID, headers=utils.common_headers):
    data = check_item(user, 'odm', odm, '%s/sv/odms/list' % SV_URL, headers)
    if data:
        try:
            rst_odm = data['odm']
            if rst_odm and utils.equals_ignore_case(rst_odm, odm):
                return data['id']
        finally:
            pass


# check brand(品牌商) and return id
def check_brand(brand=SV_BRAND_CUSTOMER, user=USER_ID, headers=utils.common_headers):
    data = check_item(user, 'brand', brand, '%s/sv/brands/list' % SV_URL, headers)
    if data:
        try:
            rst_brand = data['brand']
            if rst_brand and utils.equals_ignore_case(rst_brand, brand):
                return data['id']
        finally:
            pass


# project: 项目号(customer_branch), channel: 渠道号(channel), brand: 客户号(customer)
def check_project(project=None, channel=None, brand=None, user=USER_ID, headers=utils.common_headers):
    extra = {
        'project': project,
        'channel': channel,
        'brand': brand
    }
    data = check_item(user, 'None', 'None', '%s/sv/projects/list' % SV_URL, headers, extra)
    if data:
        try:
            rst_project = data['project']
            rst_channel = data['channel']
            rst_brand = data['brand']

            if utils.equals_ignore_case(rst_project, project) \
                    and utils.equals_ignore_case(rst_channel, channel) \
                    and utils.equals_ignore_case(rst_brand, brand):
                return data['id']
        finally:
            pass


# create model(机型) and return id
def create_model(model=SV_MODEL, user=USER_ID, headers=utils.common_headers):
    request_data = {
        'model': model
    }

    data = create_item(request_data, user, '%s/sv/models/add' % SV_URL, headers)
    if data:
        try:
            return data['id']
        finally:
            pass


# create odm(方案商) and return id
def create_odm(odm=SV_MODEL, user=USER_ID, headers=utils.common_headers):
    request_data = {
        'odm': odm
    }

    data = create_item(request_data, user, '%s/sv/odms/add' % SV_URL, headers)
    if data:
        try:
            return data['id']
        finally:
            pass


# create brand(品牌商) and return id
def create_brand(brand=SV_BRAND_CUSTOMER, user=USER_ID, headers=utils.common_headers):
    request_data = {
        'brand': brand
    }

    data = create_item(request_data, user, '%s/sv/brands/add' % SV_URL, headers)
    if data:
        try:
            return data['id']
        finally:
            pass


# project: 项目号(customer_branch), channel: 渠道号(channel), brand: 客户号(customer)
def create_project(project=None, channel=None, brand=None, user=USER_ID, headers=utils.common_headers):
    request_data = {
        'project': project,
        'channel': channel,
        'brand': brand
    }
    data = create_item(request_data, user, '%s/sv/projects/add' % SV_URL, headers)
    if data:
        try:
            return data['id']
        finally:
            pass


# create verity task
def create_verity_task(project_id, ftpPath, ftpUsername, platform, board, ccList, model, brandCustomer, odmCustomer,
                       ftpPublishUsername, userName, userId1, headers):
    purpose = 0 if SV_VERITY_PURPOSE == 'official' else 1
    request_data = {
        'signAndVerify': 1,
        'purpose': purpose,
        'projectId': project_id,
        'ftpPath': ftpPath,
        'ftpUsername': ftpUsername,
        'platform': platform,
        'board': board,
        'ccList': ccList,
        'model': model,
        'brandCustomer': brandCustomer,
        'odmCustomer': odmCustomer,
        'ftpPublishFolder': 'ftp://upload.droi.com:21/',
        'ftpPublishUsername': ftpPublishUsername,
        'passby': 0,
        'level': SV_VERITY_LEVEL,
        'userName': userName,
        'userId1': userId1
    }
    status, response = utils.post('%s/sv/verifytasks/add' % SV_URL, request_data, headers)
    if status == 200:
        try:
            code = response['code']
            msg = response['msg']
            if code == 1000 and msg == 'SUCCESS':
                return response['data']
        finally:
            pass


# create sign task
def create_sign_task(task_name, urlBefore, model, platform, signAndVerify, ftpUsername, verity_taskId, userId1,
                     headers):
    request_data = {
        'name': task_name,
        'urlBefore': urlBefore,
        'intro': 'created by automatic deployment(%s)' % DEVOPS_COMPILE_ID,
        'model': model,
        'platform': platform,
        'signAndVerify': signAndVerify,
        'ftpUsername': ftpUsername,
        'userId1': userId1
    }
    if signAndVerify == 1:
        request_data['taskId'] = verity_taskId

    status, response = utils.post('%s/sv/signtasks/add' % SV_URL, request_data, headers)
    if status == 200:
        try:
            code = response['code']
            msg = response['msg']
            if code == 1000 and msg == 'SUCCESS':
                return response['data']
        finally:
            pass


def main(argv):
    utils.star_log('commit sign verify start', 60)
    option_str = ''
    option_str += 'p-project:'  # PROJECT_NAME
    option_str += ',f-ftp:'  # SV_FTP_PATH
    option_str += ',u-url:'  # SV_URL
    option_str += ',s-user:'  # SV_USERNAME
    option_str += ',c-code:'  # SV_PASSWD
    option_str += ',t-terrace:'  # SV_PLATFORM
    option_str += ',b-board:'  # SV_BOARD
    option_str += ',l-cclist:'  # SV_CCLIST
    option_str += ',m-model:'  # SV_MODEL
    option_str += ',r-brand:'  # SV_BRAND_CUSTOMER
    option_str += ',o-odm:'  # SV_ODM_CUSTOMER
    option_str += ',v-verity'  # SV_BUILD_VERITY
    option_str += ',i-publish:'  # SV_FTP_PUBLISH_USERNAME
    option_str += ',e-purpose:'  # SV_VERITY_PURPOSE
    option_str += ',d-id:'  # DEVOPS_COMPILE_ID
    option_str += ',y-priority:'  # SV_VERITY_LEVEL
    opts = utils.dump(argv, option_str)
    # print(opts)

    if not opts:
        print('commit_sign_verify wrong parameter')
        return 1
    global PROJECT_NAME, SV_FTP_PATH, SV_URL, SV_USERNAME, SV_PASSWD, SV_PLATFORM, \
        SV_BOARD, SV_CCLIST, SV_MODEL, SV_BRAND_CUSTOMER, SV_ODM_CUSTOMER, SV_BUILD_VERITY, \
        SV_FTP_PUBLISH_USERNAME, SV_VERITY_PURPOSE, SV_VERITY_LEVEL, DEVOPS_COMPILE_ID

    if '-p' in opts or '--project' in opts:
        PROJECT_NAME = opts.get('-p') if opts.get('-p') else opts.get('--project')
    if '-f' in opts or '--ftp' in opts:
        SV_FTP_PATH = opts.get('-f') if opts.get('-f') else opts.get('--ftp')
    if '-u' in opts or '--url' in opts:
        SV_URL = opts.get('-u') if opts.get('-u') else opts.get('--url')
    if '-s' in opts or '--user' in opts:
        SV_USERNAME = opts.get('-s') if opts.get('-s') else opts.get('--user')
    if '-c' in opts or '--code' in opts:
        SV_PASSWD = opts.get('-c') if opts.get('-c') else opts.get('--code')
    if '-t' in opts or '--terrace' in opts:
        SV_PLATFORM = opts.get('-t') if opts.get('-t') else opts.get('--terrace')
    if '-b' in opts or '--board' in opts:
        SV_BOARD = opts.get('-b') if opts.get('-b') else opts.get('--board')
    if '-l' in opts or '--cclist' in opts:
        SV_CCLIST = opts.get('-l') if opts.get('-l') else opts.get('--cclist')
    if '-m' in opts or '--model' in opts:
        SV_MODEL = opts.get('-m') if opts.get('-m') else opts.get('--model')
    if '-r' in opts or '--brand' in opts:
        SV_BRAND_CUSTOMER = opts.get('-r') if opts.get('-r') else opts.get('--brand')
    if '-o' in opts or '--odm' in opts:
        SV_ODM_CUSTOMER = opts.get('-o') if opts.get('-o') else opts.get('--odm')
    if '-v' in opts or '--verity' in opts:
        SV_BUILD_VERITY = True
    if '-i' in opts or '--publish' in opts:
        SV_FTP_PUBLISH_USERNAME = opts.get('-i') if opts.get('-i') else opts.get('--publish')
    if '-e' in opts or '--purpose' in opts:
        SV_VERITY_PURPOSE = opts.get('-e') if opts.get('-e') else opts.get('--purpose')
    if '-d' in opts or '--id' in opts:
        DEVOPS_COMPILE_ID = opts.get('-d') if opts.get('-d') else opts.get('--id')
    if '-y' in opts or '--priority' in opts:
        SV_VERITY_LEVEL = opts.get('-y') if opts.get('-y') else opts.get('--priority')

    if utils.isempty(SV_FTP_PATH):
        build_config_file = utils.get_option_val('mk', 'readonly BUILD_INFO_FILE').replace('\'', '')
        if utils.isempty(build_config_file) or not path.isfile(build_config_file):
            status, project_path = utils.execute('find droi/ -maxdepth 3 -mindepth 3 -type d -name %s' % PROJECT_NAME)
            build_config_file = '%s/ProjectConfig.mk'
        if path.isfile(build_config_file):
            SV_FTP_PATH = utils.get_option_val(build_config_file, 'IMP_FTP_URL')

    if not utils.isempty(SV_FTP_PATH) and path.isfile(SV_FTP_PATH):
        file = open(SV_FTP_PATH, 'r')
        SV_FTP_PATH = file.read()
        SV_FTP_PATH = SV_FTP_PATH.strip()
        file.close()

    print('''
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
        DEVOPS_COMPILE_ID:       %s
        ''' % (PROJECT_NAME, SV_FTP_PATH, SV_URL, SV_USERNAME, SV_PASSWD,
               SV_PLATFORM, SV_BOARD, SV_CCLIST, SV_MODEL, SV_BRAND_CUSTOMER,
               SV_ODM_CUSTOMER, SV_BUILD_VERITY, SV_FTP_PUBLISH_USERNAME, DEVOPS_COMPILE_ID))

    if not (PROJECT_NAME and SV_FTP_PATH):
        print('commit_sign_verify miss importent parameter\n')
        return 2

    # dump prject
    project = utils.dump_project(PROJECT_NAME)
    # print(project)

    if not project or utils.isempty(project.project_path):
        print('commit_sign_verify project not found\n')
        return 3

    # if model(机型) not specified, use uppercase project name
    if utils.isempty(SV_MODEL):
        SV_MODEL = str(project.project_name).upper()
    # if board(主板) not specified, use uppercase project name
    if utils.isempty(SV_BOARD):
        SV_BOARD = str(project.project_name).upper()
    # if odm(方案商) not specified, use project channel
    if utils.isempty(SV_ODM_CUSTOMER):
        SV_ODM_CUSTOMER = str(project.channel).split('_')[-1]
    # if brand(品牌商) not specified, use project customer
    if utils.isempty(SV_BRAND_CUSTOMER):
        SV_BRAND_CUSTOMER = str(project.customer)
    # if SV_FTP_PUBLISH_USERNAME
    if SV_BUILD_VERITY and utils.isempty(SV_FTP_PUBLISH_USERNAME):
        SV_FTP_PUBLISH_USERNAME = str(project.customer)

    # sign SV
    data = {'remember_me': True,
            'username': SV_USERNAME,
            'password': SV_PASSWD}
    status, response = utils.post('%s/sys/login' % SV_URL, data)
    if status == 200:
        global TOKEN, USER_ID
        try:
            TOKEN = response['result']['token']
            USER_ID = response['result']['userInfo']['id']
        finally:
            print('commit_sign_verify USER_ID: %s, token: %s\n' % (USER_ID, TOKEN))
            if utils.isempty(TOKEN) or utils.isempty(USER_ID):
                print('commit_sign_verify login error!\n')
                return 4
    else:
        print('commit_sign_verify login error!\n')
        return 4

    headers_with_token = utils.common_headers.copy()
    headers_with_token['X-Access-Token'] = TOKEN

    # check model
    global MODEL_ID, ODM_ID, PROJECT_ID, BRAND_ID
    MODEL_ID = check_model(SV_MODEL, USER_ID, headers_with_token)
    print('commit_sign_verify SV_MODEL: %s, MODEL_ID: %s\n' % (SV_MODEL, MODEL_ID))
    # create model
    if not MODEL_ID or int(MODEL_ID) <= 0:
        # model not exist, create one
        MODEL_ID = create_model(SV_MODEL, USER_ID, headers_with_token)
        if not MODEL_ID or int(MODEL_ID) <= 0:
            print('commit_sign_verify model %s create failed\n' % SV_MODEL)
            return 5
        else:
            print('commit_sign_verify SV_MODEL: %s created, id: %s\n' % (SV_MODEL, MODEL_ID))

    # check odm
    ODM_ID = check_odm(SV_ODM_CUSTOMER, USER_ID, headers_with_token)
    print('commit_sign_verify SV_ODM_CUSTOMER: %s, ODM_ID: %s\n' % (SV_ODM_CUSTOMER, ODM_ID))
    # create odm
    if not ODM_ID or int(ODM_ID) <= 0:
        ODM_ID = create_odm(SV_ODM_CUSTOMER, USER_ID, headers_with_token)
        if not ODM_ID or int(ODM_ID) <= 0:
            print('commit_sign_verify odm %s create failed\n' % SV_ODM_CUSTOMER)
            return 6
        else:
            print('commit_sign_verify SV_ODM_CUSTOMER: %s created, id: %s\n' % (SV_ODM_CUSTOMER, ODM_ID))

    # check project
    # PROJECT_ID = check_project('V10K', 'HONGXIANGYUAN_HONGXIANGYUAN', 'HONGXIANGYUAN', USER_ID, headers_with_token)
    PROJECT_ID = check_project(project.customer_branch, project.channel, project.customer, USER_ID, headers_with_token)
    print('commit_sign_verify project: %s, PROJECT_ID: %s\n' % (project.customer_branch, PROJECT_ID))
    # create project
    if not PROJECT_ID or int(PROJECT_ID) <= 0:
        PROJECT_ID = create_project(project.customer_branch, project.channel, project.customer, USER_ID,
                                    headers_with_token)
        if not PROJECT_ID or int(PROJECT_ID) <= 0:
            print('commit_sign_verify project %s create failed\n' % project.customer_branch)
            return 7
        else:
            print('commit_sign_verify project: %s created, id: %s\n' % (project.customer_branch, PROJECT_ID))

    # check brand
    BRAND_ID = check_brand(SV_BRAND_CUSTOMER, USER_ID, headers_with_token)
    print('commit_sign_verify SV_BRAND_CUSTOMER: %s, BRAND_ID: %s\n' % (SV_BRAND_CUSTOMER, BRAND_ID))
    # create brand
    if not BRAND_ID or int(BRAND_ID) <= 0:
        BRAND_ID = create_brand(SV_BRAND_CUSTOMER, USER_ID, headers_with_token)
        if not BRAND_ID or int(BRAND_ID) <= 0:
            print('commit_sign_verify brand %s create failed\n' % SV_BRAND_CUSTOMER)
            return 8
        else:
            print('commit_sign_verify SV_BRAND_CUSTOMER: %s created, id: %s\n' % (SV_BRAND_CUSTOMER, ODM_ID))

    # dump ftpUsername
    ftpUsername = None
    match_obj = re.match('^(ftp://).*@', SV_FTP_PATH)
    if match_obj:
        ftpUsername = str(match_obj.group(0))
        ftpUsername = ftpUsername.replace('ftp://', '').replace('@', '')
        SV_FTP_PATH = str(SV_FTP_PATH).replace('%s@' % ftpUsername, '')
    if utils.isempty(ftpUsername):
        print('ftpUsername not specified!\n')
        return 9
    print('commit_sign_verify ftpUsername: %s\n' % ftpUsername)

    # create verity task first
    verity_task_data = None
    if SV_BUILD_VERITY:
        ftpPath = SV_FTP_PATH.replace('upload', 'download')
        verity_task_data = create_verity_task(PROJECT_ID, ftpPath, ftpUsername, SV_PLATFORM, SV_BOARD, SV_CCLIST,
                                              SV_MODEL,
                                              SV_BRAND_CUSTOMER, SV_ODM_CUSTOMER, SV_FTP_PUBLISH_USERNAME, SV_USERNAME,
                                              USER_ID,
                                              headers_with_token)
        if not verity_task_data:
            print('commit_sign_verify create verity task failed!\n')
            return 10
        else:
            print('commit_sign_verify verity task created, id: %s\n' % verity_task_data['taskId'])

    # create sign tasks
    verity_task_id = verity_task_data['taskId'] if verity_task_data else 0
    task_name = SV_FTP_PATH.split('/')[-1].replace('.zip', '')
    sign_task_data = create_sign_task(task_name, SV_FTP_PATH, SV_MODEL, SV_PLATFORM, 1 if SV_BUILD_VERITY else 0,
                                      ftpUsername, verity_task_id, USER_ID, headers_with_token)
    if not sign_task_data:
        print('commit_sign_verify create sign task failed!\n')
        return 11
    print('commit_sign_verify sign task created: %s\n' % sign_task_data['id'])

    # start task
    if sign_task_data and sign_task_data['id'] > 0:
        start_status, start_response = utils.post('%s/sv/signtasks/handle' % SV_URL, {
            'taskId': sign_task_data['id'],
            'type': 10,
            'userid': USER_ID
        }, headers_with_token)

        if start_status == 200 and start_response['code'] == 1000 and start_response['msg'] == 'SUCCESS':
            print('commit_sign_verify sign task %s started!\n' % sign_task_data['id'])

    # update database
    update_argv = ["-t", "devops_compile", "-k", "compile_sign_ftp_url,compile_sign_id,compile_verity_id",
                   "-v", "%s,%s,%s" % (SV_FTP_PATH, sign_task_data['id'], verity_task_id), "-w", "id",
                   "-e", DEVOPS_COMPILE_ID]
    update_db.main(update_argv)
    return 0


if __name__ == '__main__':
    r = main(sys.argv[1:])
    _exit(r)
