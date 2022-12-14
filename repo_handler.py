#!/usr/bin/python3
import re
import warnings

import utils

warnings.filterwarnings("ignore")
import os
import sys
from fuzzywuzzy import fuzz
from git import *
from re import match, search
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
    rst_code, text = execute('repo sync --force-sync')
    if rst_code != 0:
        sync_errors = {}
        for line in text.split('\n'):
            if line.startswith('error:'):
                try:
                    ptn1 = 'error:[\s]([^:]*):[\s](.*)'
                    ptn2 = 'error:[\s]Cannot[\s]fetch[\s]([\S]*)[\s]from[\s](.*)'
                    mth = match(ptn1, line)
                    mth = mth if mth else match(ptn2, line)
                    if mth:
                        error_git = ORIGIN_WORK_DIRECTORY + os.sep + mth.group(1)
                        error_reason = mth.group(2)
                        sync_errors[error_git] = error_reason
                        continue
                except Exception as e:
                    print('%s\nexception: %s' % (line, e))
        # print(sync_errors)
        return sync_errors


# recursive sync util success
def handle_sync():
    star_log('handle_sync', 60)
    sync_failed = sync()
    # sync failed
    global SYNC_RECURSIVE_TIMES
    if SYNC_RECURSIVE_TIMES > 0 and sync_failed and len(sync_failed.keys()) > 0:
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
            try:
                repo.remotes.origin.pull()
            except Exception as e:
                print('pull exception: %s' % e)
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
    unclean_nodes = []
    if ary and len(ary) >= 2:
        available_lines = []
        path_index = []
        # clean empty line & record 'path'
        for line in ary[1].split('\n'):
            if utils.isempty(line):
                continue
            available_lines.append(line)
            if os.path.isdir(line):
                path_index.append(len(available_lines) - 1)

        # by path, dump unclean node
        for i in path_index:
            region_start = i
            region_end = len(available_lines) - 1 if path_index.index(i) == len(path_index) - 1 else path_index[
                path_index.index(i) + 1] - 1

            node = {}
            while region_start < region_end:
                line = available_lines[region_start + 1]
                match = re.search('^([ ]{2}|\*)(.*)\([ ]([\d]+)[ ]commit', line)
                if match:
                    branch = match.group(2).strip()
                    heads = int(match.group(3).strip())
                    # print('branch: %s, heads: %s' % (branch, heads))
                    node[branch] = heads
                region_start += 1
            if len(node.keys()) > 0:
                node['path'] = available_lines[i]
                unclean_nodes.append(node)
        # print(unclean_nodes)
    # dump .repo/manifests
    manifests_path = ORIGIN_WORK_DIRECTORY + '/.repo/manifests'
    manifests_repo = Repo(manifests_path)
    heads = dump_node(manifests_repo.git.status())
    if heads is None and 'git rebase --' in manifests_repo.git.status():
        try:
            manifests_repo.git.rebase('--abort')
            heads = dump_node(manifests_repo.git.status())
        except Exception as e:
            pass
    if heads and heads != 0:
        node = {'path': manifests_path, manifests_repo.active_branch.name: heads[0] if isinstance(heads, list) else heads}
        unclean_nodes.append(node)
    return unclean_nodes


# recursive overview util success
def handle_overview():
    star_log('handle_overview', 60)
    unclean_nodes = overview()
    # overview failed
    global OVERVIEW_RECURSIVE_TIMES
    if OVERVIEW_RECURSIVE_TIMES > 0 and not utils.isempty(unclean_nodes):
        OVERVIEW_RECURSIVE_TIMES -= 1
        print('overview failed')
        # clean unclean node
        for node in unclean_nodes:
            print('clean %s:' % node)
            repo = Repo(node['path'])
            if not repo:
                continue
            # clean unclean branch
            for branch in node.keys():
                if branch == 'path':
                    continue
                repo.git.checkout(branch)
                heads = dump_node(repo.git.status())
                # print(node)
                if isinstance(heads, list):
                    reset(repo, heads[0])
                elif isinstance(heads, int):
                    reset(repo, heads)
                repo.remotes.origin.pull()
            if node['path'] == ORIGIN_WORK_DIRECTORY + '/.repo/manifests':
                continue
            checkout_cmd = ['-b', 'master']
            for branch in repo.branches:
                if branch.name == 'master':
                    checkout_cmd.remove('-b')
                    break
            repo.git.checkout(checkout_cmd)
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
    str = file.read().strip()
    lines = str.split(';')
    result = []
    for line in lines:
        if not line.lstrip().startswith('#') and not utils.isempty(line.strip()):
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


def main(argv):
    option_str = 'h-help'
    option_str += ',c-clean'
    option_str += ',s-sync'
    option_str += ',o-overview'
    option_str += ',p-pick:'

    opts = dump(argv, option_str)
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
            # dump cherry-pick cmd
            cps = read_cps_from_file(file)
            print('cps:')
            manifests_cps = []
            for cp in cps:
                print(cp)
                if 'Freeme/platforms/manifest' in cp:
                    manifests_cps.append(cp)
            if len(manifests_cps) > 0:
                manifests_path = ORIGIN_WORK_DIRECTORY + os.sep + '.repo/manifests'
                repo = Repo(manifests_path)
                success = 0
                print('\nin %s try exxcute' % manifests_path)
                for cmd in manifests_cps:
                    cps.remove(cmd)
                    # git checkout . && git clean -xfd
                    repo.git.checkout('.')
                    repo.git.clean('-xdf')
                    local_user_name = repo.config_reader('global').get_value('user', 'name')
                    cmd = change_name(cmd, local_user_name)
                    result = cherry_pick(manifests_path, cmd)
                    print('%s\nresult: %d' % (cmd, result))
                    success = result if result != 0 else success
                if success == 0:
                    print('\nmanifests cherry-pick success, repo sync')
                    utils.execute('repo sync --force-sync && repo start --all master')
                else:
                    print('\nmanifests cherry-pick failed, exit')
                    exit(3)
            # dump current repo
            google_repo = dump_projects()
            git_name_path_dict = {}
            for project in google_repo.projects:
                git_name_path_dict[project.name] = project.path
            # delete file cps
            os.remove(file)
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
                # check all matched
                if len(cps) != len(cmd_project):
                    print('not all commands match successfully')
                    exit(2)
                # begin cherry-pick
                success = 0
                for cmd in cps:
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
                    result = cherry_pick(path, cmd)
                    print('result: %d' % result)
                    success = result if result != 0 else success
                exit(0 if success == 0 else 3)


if __name__ == '__main__':
    main(sys.argv[1:])
