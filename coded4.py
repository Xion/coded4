#!/usr/bin/env python
'''
coded4
Calculates time spent on coding based on commit timestamps
'''

__author__ = 'Karol Kuczmarski "Xion"'
__license__ = "MIT"
__version__ = "0.2"


from datetime import datetime, timedelta
from collections import namedtuple
from subprocess import Popen, PIPE
import argparse
import os


### Main function

def main():
    argparser = create_argument_parser()
    args = argparser.parse_args()

    if args:
        vcs = args.vcs or detect_vcs(args.directory)
        contributors = calculate_stats(args.directory, vcs, args.initial_time, args.break_time)

        output = dicts_to_table if args.output == 'table' else __import__(args.output)
        print format_stats(contributors, output)


def create_argument_parser():
    parser = argparse.ArgumentParser(description="Calculate time spent coding by using commit timestamps",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    minutes = lambda m: timedelta(minutes=int(m))

    parser.add_argument('directory', type=str, default='.',
                        help="Directory where the repository is contained     (. by default)",
                        metavar="DIRECTORY")
    parser.add_argument('--repo', '-r', type=str, default=None, choices=SUPPORTED_VCS,
                        help="Repository type for which the stats should be generated",
                        metavar="TYPE", dest='vcs')
    parser.add_argument('--break', '-b', type=minutes, default=DEFAULT_BREAK_TIME,
                        help="Maximum time between commits which are still considered a single coding session",
                        metavar="MINUTES", dest='break_time')
    parser.add_argument('--initial', '-i', type=minutes, default=DEFAULT_INITIAL_TIME,
                        help="Time before first commit within a coding session",
                        metavar="MINUTES", dest='initial_time')
    parser.add_argument('--format', '-f', type=str, default='table', choices=['table', 'json'],
                        help="Output format (formatted table by default)",
                        metavar="FORMAT", dest='output')

    return parser


SUPPORTED_VCS = ['git']
DEFAULT_BREAK_TIME = timedelta(minutes=30)
DEFAULT_INITIAL_TIME = timedelta(minutes=10)


### General

Commit = namedtuple('Commit', ['hash', 'time', 'author', 'message'])
Contributor = namedtuple('Contributor', ['name', 'commits', 'total_time'])

def detect_vcs(directory):
    ''' Checks which of the supported VCS has repo in given directory. '''
    for vcs in SUPPORTED_VCS:
        vcs_dir = os.path.join(directory, '.' + vcs)
        if os.path.isdir(vcs_dir):
            return vcs

def calculate_stats(directory, vcs, initial_time, break_time):
    ''' Calculates statistics for given repository.
    @return: List of Contributor tuples
    '''
    history_func = globals().get(vcs + '_history')
    if not history_func:
        raise ValueError, "Version control system '%s' is not supported" % vcs

    history = history_func(directory)
    commits = {}

    # go through history once to extract all contributors
    for commit in history:
        commit_list = commits.setdefault(commit.author, [])
        commit_list.append(commit)

    # calculate statistics for every contributor
    contributors = []
    for author, commits in commits.iteritems():
        total_time = timedelta()

        commit_iter = iter(commits)
        in_session = False
        while True:
            commit = next(commit_iter, None)
            if not commit:    break
            if in_session:
                interval = last_commit_time - commit.time
                if interval > break_time:    # break (end of coding session)
                    in_session = False
                    continue
                total_time += interval
            else:    # new coding session
                in_session = True
                total_time += initial_time
            last_commit_time = commit.time

        contributors.append(Contributor(author, commits, total_time))        

    return contributors

def format_stats(contributors, output=str):
    ''' Formats the statistics using the specified output method. '''
    stats = [dict(name=c.name, commits=len(c.commits), time="%s secs" % c.total_time.total_seconds())
             for c in contributors]
    if output:
        if callable(output):    return output(stats)
        else:                    return output.dumps(stats)
    return stats

def dicts_to_table(dicts):
    ''' Pretty prints the list of dictionaries as a table. '''
    if not dicts:    return ''
    lines  = []

    labels = dicts[0].keys()
    max_col_lens = [max(map(len, [str(d[key]) for d in dicts] + labels))
                    for key in labels]
    max_row_len = sum(max_col_lens) + (len(labels) - 1)

    # format header
    lines.append(str.join(' ', (label.ljust(col_len)
                                for label, col_len in zip(labels, max_col_lens))))
    lines.append('-' * max_row_len)

    # format rows
    for d in dicts:
        lines.append(str.join(' ', (str(d[key]).ljust(col_len)
                                    for key, col_len in zip(labels, max_col_lens))))

    return str.join('\n', lines)


### Git support

def git_history(path):
    ''' Returns a list of Commit tuples with history for given Git repo. '''
    sep = '|'
    git_log_format = str.join(sep, ['%H', '%at', '%an', '%s'])
    git_log = 'git log --format=format:"%s"' % git_log_format
    log = exec_command(git_log, path)

    history = []
    for line in log.splitlines():
        commit_hash, timestamp, author, message = line.split(sep)
        time = datetime.fromtimestamp(float(timestamp))
        history.append(Commit(commit_hash, time, author, message))

    return history



### Utilities

def exec_command(cmd, workdir=None):
    ''' Executes given shell command and returns its stdout as string.
    @param workdir: Working directory for the command
    '''
    cmd_out = Popen(cmd, shell=True, cwd=workdir, stdout=PIPE).stdout
    return cmd_out.read()



if __name__ == '__main__':
    main()