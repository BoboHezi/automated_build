#!/usr/bin/python
import getopt
import json
import requests
import sys
from commands import getstatusoutput
from os import getcwd
from os import path
from os import readlink
from re import match

common_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Length': 77,
    'Content-Type': 'application/json;charset=UTF-8',
    'Host': '192.168.151.31:8084',
    'Origin': 'http://192.168.151.31:2030',
    'Referer': 'http://192.168.151.31:2030/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
}


class ProjectInfo(object):
    """docstring for ProjectInfo"""

    def __init__(self, project_name, project_path, internal_version,
                 external_version, channel, customer, customer_branch, platform):
        # super(ProjectInfo, self).__init__()
        self.project_name = project_name
        self.project_path = project_path
        self.internal_version = internal_version
        self.external_version = external_version
        self.channel = channel
        self.customer = customer
        self.customer_branch = customer_branch
        self.platform = platform

    def __str__(self):
        str = 'ProjectInfo(name=%s, ' % self.project_name
        str += 'path=%s, ' % self.project_path
        str += 'internal_ver=%s, ' % self.internal_version
        str += 'external_ver=%s, ' % self.external_version
        str += 'channel=%s, ' % self.channel
        str += 'customer=%s, ' % self.customer
        str += 'customer_branch=%s, ' % self.customer_branch
        str += 'platform=%s)' % self.platform

        return str


def execute(cmd):
    rst = getstatusoutput(cmd)
    return rst[0], rst[1]


def dump(args=[], opt_str=''):
    """
    dump args like: ./utils.py -n eli -u root -p 123456
    return a dictionary
    opt_str like: h-help,n-name:,u-user:,p-password:
    "n" for short, "name" for long, ":" for with parameter
    """
    if not len(args) or not opt_str or not len(opt_str):
        return

    # dump short and long opt
    short_opt = ''
    long_opt = []
    for combind in opt_str.split(','):
        items = combind.split('-')
        if len(items) != 2:
            break
        have_extra = ':' in items[1]

        _short = items[0] + (':' if have_extra else '')
        _long = items[1].replace(':', '=')

        short_opt += _short
        long_opt.append(_long)
    # empty
    if not (len(short_opt) and len(long_opt)):
        return

    # dump options
    opts = None
    try:
        opts, argvs = getopt.getopt(args, short_opt, long_opt)
    except Exception as e:
        print('dump ', e)

    if opts:
        result = {}
        for opt, arg in opts:
            result[opt] = arg
        return result
    pass


def isempty(obj):
    return True if not (obj and len(obj)) else False


def get_option_val(fpath, key):
    if not path.exists(fpath):
        return

    file = open(fpath, 'r')
    str = file.read()
    file.close()
    lines = str.splitlines()
    for line in lines:
        if not line.lstrip().startswith('#'):
            matchObj = match('^(%s)(\s*)=(\s*)(.*)' % key, line)
            if matchObj:
                return matchObj.group(4)
    return


def dump_platform(folder=getcwd()):
    if isempty(folder) or not path.isdir(folder):
        return None
    # check MTK or SPRD
    manifest = folder + '/.repo/manifest.xml'
    if not (path.exists(manifest) and path.islink(manifest)):
        return None
    source = readlink(manifest)
    PLATFORM = None
    if 'SPRD' in source:
        PLATFORM = 'SPRD'
    elif 'MTK' in source:
        PLATFORM = 'MTK'
    elif path.exists(folder + '/vendor/sprd'):
        PLATFORM = 'SPRD'
    elif path.exists(folder + '/vendor/mediatek'):
        PLATFORM = 'MTK'
    return PLATFORM


def dump_project(project_name=None, code_path=getcwd()):
    if not project_name:
        return None

    # find platform
    platform = dump_platform(code_path)

    # find project path
    find_cmd = 'find %s/droi/ -maxdepth 3 -mindepth 3 -type d -name %s' % (code_path, project_name)
    status, project_path = execute(find_cmd)
    project_config = project_path + '/ProjectConfig.mk'

    # dump project info
    internal_ver = get_option_val(project_config, 'FREEME_PRODUCT_INFO_SW_VERNO_INTERNAL')
    external_ver = get_option_val(project_config, 'FREEME_PRODUCT_INFO_SW_VERNO')
    channel = get_option_val(project_config, 'FREEME_SYS_CHANNEL')
    customer = get_option_val(project_config, 'FREEME_SYS_CUSTOMER')
    customer_branch = get_option_val(project_config, 'FREEME_SYS_CUSTOMER_BRANCH')

    return ProjectInfo(project_name, project_path, internal_ver, external_ver,
                       channel, customer, customer_branch, platform)


def post(url, data, headers=common_headers):
    if isempty(url) or not data:
        return
    if not headers or headers is common_headers:
        headers = common_headers.copy()

    data_str = data if isinstance(data, str) else json.dumps(data)
    headers['Content-Length'] = len(data_str)

    try:
        r = requests.post(url, data=data_str, headers=headers)
        return r.status_code, json.loads(r.text)
    except Exception as e:
        return 0, None


if __name__ == '__main__':
    rst = dump(sys.argv[1:], 'h-help,n-name:,u-user:,p-password:')
    print(rst)