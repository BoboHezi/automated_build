#!/usr/bin/python3
import warnings

warnings.filterwarnings("ignore")
import sys
import os
from re import search
from git import *
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


# repo sync
def sync():
    rst_code, text = execute('repo sync')
    if rst_code != 0:
        sync_errors = {}
        for line in text.split('\n'):
            if line.startswith('error:'):
                error_git = os.getcwd() + os.sep + line.split(': ')[1]
                error_reason = line.split(': ')[2]
                sync_errors[error_git] = error_reason
        # print(sync_errors)
        return sync_errors


# recursive sync util success
def handle_sync():
    star_log('handle_sync', 60)
    sync_failed = sync()
    # sync failed
    if sync_failed and len(sync_failed.keys()) > 0:
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
                unclean_paths.append(os.getcwd() + os.sep + line)
                # print(line)
        return unclean_paths


# recursive overview util success
def handle_overview():
    star_log('handle_overview', 60)
    unclean_paths = overview()
    # overview failed
    if unclean_paths and len(unclean_paths) > 0:
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


if __name__ == '__main__':
    option_str = 'h-help'
    option_str += ',c-clean'
    option_str += ',s-sync'
    option_str += ',o-overview'

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
