#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import sys

import utils


def _exit(code):
    print('*' * 15 + 'commit sign verify end' + '*' * 15)
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
                        if item[name] == keyword:
                            return item
        except Exception as e:
            print e
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
            if rst_model and rst_model == model:
                return data['id']
        finally:
            pass


# check odm(方案商) and return id
def check_odm(odm=SV_ODM_CUSTOMER, user=USER_ID, headers=utils.common_headers):
    data = check_item(user, 'odm', odm, '%s/sv/odms/list' % SV_URL, headers)
    if data:
        try:
            rst_odm = data['odm']
            if rst_odm and rst_odm == odm:
                return data['id']
        finally:
            pass


# check brand(品牌商) and return id
def check_brand(brand=SV_BRAND_CUSTOMER, user=USER_ID, headers=utils.common_headers):
    data = check_item(user, 'brand', brand, '%s/sv/brands/list' % SV_URL, headers)
    if data:
        try:
            rst_brand = data['brand']
            if rst_brand and rst_brand == brand:
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

            if rst_project == project and rst_channel == channel and rst_brand == brand:
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
    purpose = 0 if 'sign.ttddsh.com' in SV_URL else 1
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
        'level': None,
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
        'intro': 'create by python',
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


if __name__ == '__main__':
    print('*' * 15 + 'commit sign verify start' + '*' * 15)
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
    opts = utils.dump(sys.argv[1:], option_str)
    # print(opts)

    if not opts:
        print('commit_sign_verify wrong parameter')
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
    if opts.has_key('-r') or opts.has_key('--brand'):
        SV_BRAND_CUSTOMER = opts.get('-r') if opts.get('-r') else opts.get('--brand')
    if opts.has_key('-o') or opts.has_key('--odm'):
        SV_ODM_CUSTOMER = opts.get('-o') if opts.get('-o') else opts.get('--odm')
    if opts.has_key('-v') or opts.has_key('--verity'):
        SV_BUILD_VERITY = True
    if opts.has_key('-i') or opts.has_key('--publish'):
        SV_FTP_PUBLISH_USERNAME = opts.get('-i') if opts.get('-i') else opts.get('--publish')

    print '''
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
    ''' % (PROJECT_NAME, SV_FTP_PATH, SV_URL, SV_USERNAME, SV_PASSWD,
           SV_PLATFORM, SV_BOARD, SV_CCLIST, SV_MODEL, SV_BRAND_CUSTOMER,
           SV_ODM_CUSTOMER, SV_BUILD_VERITY, SV_FTP_PUBLISH_USERNAME)

    if not (PROJECT_NAME and SV_FTP_PATH):
        print('commit_sign_verify miss importent parameter\n')
        _exit(2)

    # dump prject
    project = utils.dump_project(PROJECT_NAME)
    # print(project)

    if not project or utils.isempty(project.project_path):
        print('commit_sign_verify project not found\n')
        _exit(3)

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
        try:
            TOKEN = response['result']['token']
            USER_ID = response['result']['userInfo']['id']
        finally:
            print('commit_sign_verify USER_ID: %s, token: %s\n' % (USER_ID, TOKEN))
            if utils.isempty(TOKEN) or utils.isempty(USER_ID):
                print('commit_sign_verify login error!\n')
                _exit(4)
    else:
        print('commit_sign_verify login error!\n')
        _exit(4)

    headers_with_token = utils.common_headers.copy()
    headers_with_token['X-Access-Token'] = TOKEN

    # check model
    MODEL_ID = check_model(SV_MODEL, USER_ID, headers_with_token)
    print('commit_sign_verify SV_MODEL: %s, MODEL_ID: %s\n' % (SV_MODEL, MODEL_ID))
    # create model
    if not MODEL_ID or int(MODEL_ID) <= 0:
        # model not exist, create one
        MODEL_ID = create_model(SV_MODEL, USER_ID, headers_with_token)
        if not MODEL_ID or int(MODEL_ID) <= 0:
            print('commit_sign_verify model %s create failed\n' % SV_MODEL)
            _exit(5)
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
            _exit(6)
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
            _exit(7)
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
            _exit(8)
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
        _exit(9)
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
            _exit(10)
        else:
            print('commit_sign_verify verity task created, id: %s\n' % verity_task_data['taskId'])

    # create sign tasks
    verity_task_id = verity_task_data['taskId'] if verity_task_data else 0
    task_name = SV_FTP_PATH.split('/')[-1].replace('.zip', '')
    sign_task_data = create_sign_task(task_name, SV_FTP_PATH, SV_MODEL, SV_PLATFORM, 1 if SV_BUILD_VERITY else 0,
                                      ftpUsername, verity_task_id, USER_ID, headers_with_token)
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
    _exit(0)