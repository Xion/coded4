'''
Code for supporting specific VCS (version control systems).
'''
from collections import namedtuple
from datetime import  datetime
from utils import exec_command
import os


SUPPORTED_VCS = ['git', 'hg']


def retrieve_commit_history(directory, vcs_name=None):
    ''' Retrieves history of commit for given repository.
    @return: List of Commit tuples
    '''
    vcs_name = vcs_name or detect_vcs(directory)
    if not vcs_name:
        raise ValueError, "Could not find any known version control system in given directory"

    history_func = globals().get(vcs_name + '_history')
    if not history_func:
        raise ValueError, "Version control system '%s' is not supported" % vcs_name

    history = history_func(directory)
    return sorted(history, key=lambda c: c.time, reverse=True)

def detect_vcs(directory):
    ''' Checks which of the supported VCS has repo in given directory.
    @return: Name of version control system found in given directory
    '''
    for vcs in SUPPORTED_VCS:
        vcs_dir = os.path.join(directory, '.' + vcs)
        if os.path.isdir(vcs_dir):
            return vcs


Commit = namedtuple('Commit', ['hash', 'time', 'author', 'message'])


### Git support

def git_history(path):
    ''' Returns a list of Commit tuples with history for given Git repo. '''
    sep = '|'
    git_log_format = str.join(sep, ['%H', '%at', '%an', '%s'])
    git_log = 'git log --format=format:"%s"' % git_log_format
    log = exec_command(git_log, path)

    history = []
    for line in log.splitlines():
        commit_hash, timestamp, author, message = line.split(sep, 3)
        time = datetime.fromtimestamp(float(timestamp))
        history.append(Commit(commit_hash, time, author, message))

    return history


### Hg support

def hg_history(path):
    ''' Returns a list of Commit tuples with history for given Mercurial repo. '''
    sep = '|'
    hg_log_template = str.join(sep, ['{node}', '{date|hgdate}', '{author|person}', '{desc|firstline}'])
    hg_log = r'hg log --template "%s\n"' % hg_log_template
    log = exec_command(hg_log, path)

    history = []
    for line in log.splitlines():
        commit_hash, hg_time, author, message = line.split(sep, 3)
        hg_time = reduce(int.__add__, map(int, hg_time.split()), 0)  # hg_time is 'local_timestamp timezone_offset'
        time = datetime.fromtimestamp(hg_time)
        history.append(Commit(commit_hash, time, author, message))

    return history