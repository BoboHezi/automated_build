#!/usr/bin/python3
import re
import warnings

import utils

warnings.filterwarnings("ignore")
import os
import sys
import RepoParser
from fuzzywuzzy import fuzz
from git import *
from re import search
from RepoParser import *
from utils import dump
from utils import execute
from utils import star_log

# 1. clean
#     |
#     |
#     |--------------^
#     |              |
#     |            reset
#     v              |
# 2. overview----->FAILED
#     |
#     |
#  SUCCESS
#     |
#     |--------------^
#     |              |
#     |         clean & pull
#     v              |
# 3. sync--------->FAILED
#     |
#     v
#  SUCCESS

SYNC_RECURSIVE_TIMES = 3
OVERVIEW_RECURSIVE_TIMES = 3
ORIGIN_WORK_DIRECTORY = os.getcwd()


# repo sync
def sync():
    rst_code, text = execute('repo sync')
    if rst_code != 0:
        sync_errors = {}
        for line in text.split('\n'):
            if line.startswith('error:'):
                error_git = ORIGIN_WORK_DIRECTORY + os.sep + line.split(': ')[1]
                error_reason = line.split(': ')[2]
                sync_errors[error_git] = error_reason
        # print(sync_errors)
        return sync_errors


# recursive sync util success
def handle_sync():
    star_log('handle_sync', 60)
    sync_failed = sync()
    # sync failed
    if SYNC_RECURSIVE_TIMES > 0 and sync_failed and len(sync_failed.keys()) > 0:
        global SYNC_RECURSIVE_TIMES
        SYNC_RECURSIVE_TIMES -= 1
        print('sync failed')
        for path in sync_failed.keys():
            print('pull %s:' % path)
            repo = Repo(path)
            if not repo:
                continue
            # git checkout .
            if repo.is_dirty():
                repo.git.checkout('.')
            # git clean -xfd
            if repo.untracked_files:
                repo.git.clean('-xdf')
            # try git reset if not clean
            node = dump_node(repo.git.status())
            reset(repo, node[0] if isinstance(node, list) else node)
            # pull
            repo.remotes.origin.pull()
        handle_sync()
    else:
        print('sync success')


# git reset --hard HEAD~X
def reset(repo, head):
    if repo and head > 0:
        repo.head.reset('HEAD~%d' % head, index=True, working_tree=True)


# dump local & remote node difference
def dump_node(status_str):
    ptn_up_to_date = 'Your branch is up to date with'
    ptn_ahead = 'Your branch is ahead of .* by ([\d]*) commit'
    ptn_behind = 'Your branch is behind .* by ([\d]*) commit'
    ptn_diverge = 'have ([\d]*) and ([\d]*) different commits each'

    match_obj = search(ptn_up_to_date, status_str)
    if match_obj:
        # print('same')
        return 0

    match_obj = search(ptn_ahead, status_str)
    if match_obj:
        # print('ahead %s' % match_obj.group(1))
        return int(match_obj.group(1))

    match_obj = search(ptn_behind, status_str)
    if match_obj:
        # print('behind %s' % match_obj.group(1))
        return -int(match_obj.group(1))

    match_obj = search(ptn_diverge, status_str)
    if match_obj:
        # print('me %s, remote %s' % (match_obj.group(1), match_obj.group(2)))
        return [int(match_obj.group(1)), int(match_obj.group(2))]


# repo overview
def overview():
    rst_code, text = execute('repo info -o')
    ary = text.split('-' * 28)
    if ary and len(ary) >= 2:
        unclean_paths = []
        for line in ary[1].split('\n'):
            if os.path.isdir(line):
                unclean_paths.append(ORIGIN_WORK_DIRECTORY + os.sep + line)
                # print(line)
        return unclean_paths


# recursive overview util success
def handle_overview():
    star_log('handle_overview', 60)
    unclean_paths = overview()
    # overview failed
    if OVERVIEW_RECURSIVE_TIMES > 0 and not utils.isempty(unclean_paths):
        global OVERVIEW_RECURSIVE_TIMES
        OVERVIEW_RECURSIVE_TIMES -= 1
        print('overview failed')
        for path in unclean_paths:
            print('clean %s:' % path)
            repo = Repo(path)
            if not repo:
                continue
            node = dump_node(repo.git.status())
            # print(node)
            if isinstance(node, list):
                reset(repo, node[0])
            elif isinstance(node, int):
                reset(repo, node)
            repo.remotes.origin.pull()
        handle_overview()
    else:
        print('overview success')


# treat as after repoclean -a
def handle_clean():
    star_log('handle_clean', 60)
    handle_overview()
    handle_sync()


def read_cps_from_file(path):
    if not os.path.exists(path):
        return None
    file = open(path, 'r')
    str = file.read()
    lines = str.split(';')
    result = []
    for line in lines:
        if not line.lstrip().startswith('#'):
            result.append(line)
    return result


def fuzzy_match(str, list, nearly=85):
    # print('%s matchs below:' % str)
    most_suit = 0
    most_match = None
    for item in list:
        suit = fuzz.ratio(str, item)
        if suit > most_suit and suit >= nearly:
            most_suit = suit
            most_match = item
            if suit == 100:
                break
    # print('most_match: %s, %d' % (most_match, most_suit))
    return most_suit, most_match


def change_name(cmd, new_name):
    if not utils.isempty(cmd):
        match = re.search('ssh://(.*)@', cmd)
        if match:
            old_name = match.group(1)
            cmd = cmd.replace(old_name, new_name)
    return cmd


def cherry_pick(path, cmd):
    os.chdir(path)
    rst_code, rst_msg = execute(cmd)
    if rst_code != 0:
        execute('git cherry-pick --abort')
    os.chdir(ORIGIN_WORK_DIRECTORY)
    return rst_code


if __name__ == '__main__':
    option_str = 'h-help'
    option_str += ',c-clean'
    option_str += ',s-sync'
    option_str += ',o-overview'
    option_str += ',p-pick:'

    opts = dump(sys.argv[1:], option_str)
    if not opts:
        exit(1)

    for opt in opts:
        if opt in ['-s', '--sync']:
            handle_sync()
        elif opt in ['-c', '--clean']:
            handle_clean()
        elif opt in ['-o', '--overview']:
            handle_overview()
        elif opt in ['-p', '--pick']:
            star_log('cherry-pick', 60)
            file = opts.get(opt)
            if utils.isempty(file) or not os.path.exists(file):
                print('%s not exists' % file)
                continue
            # dump current repo
            google_repo = dump_projects()
            git_name_path_dict = {}
            for project in google_repo.projects:
                git_name_path_dict[project.name] = project.path
            print('git_name_path_dict size: %d' % len(git_name_path_dict.keys()))
            # dump cherry-pick cmd
            cps = read_cps_from_file(file)
            print('cps:\n%s' % cps)
            if not utils.isempty(cps):
                # cherry-pick cmd & project map
                cmd_project = {}
                for cmd in cps:
                    match = re.search('[0-9]\/.*"', cmd)
                    if match:
                        git_name = match.group()[2: -1]
                        suit, local_git_name = fuzzy_match(git_name, git_name_path_dict.keys())
                        if local_git_name:
                            cmd_project[cmd] = [local_git_name, git_name_path_dict[local_git_name]]
                print('cmd_project size: %d' % len(cmd_project.keys()))
                # begin cherry-pick
                for cmd in cmd_project.keys():
                    path = ORIGIN_WORK_DIRECTORY + os.sep + cmd_project[cmd][1]
                    repo = Repo(path)
                    # git checkout .
                    if repo.is_dirty():
                        repo.git.checkout('.')
                    # git clean -xfd
                    if repo.untracked_files:
                        repo.git.clean('-xdf')
                    local_user_name = repo.config_reader('global').get_value('user', 'name')
                    cmd = change_name(cmd, local_user_name)
                    print('\nin %s try exxcute\n%s' % (path, cmd))
                    print('result: %d' % cherry_pick(path, cmd))
