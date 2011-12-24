#!/usr/bin/env python
'''
Executable script.
'''
from __future__ import unicode_literals

import vcs
import stats
from output import format_stats, dicts_to_table
from datetime import timedelta
import argparse



def main():
    argparser = create_argument_parser()
    args = argparser.parse_args()

    if args:
        contributors = calculate_statistics(args)
        output = dicts_to_table if args.output == 'table' else __import__(args.output)
        print format_stats(contributors, output)


def create_argument_parser():
    parser = argparse.ArgumentParser(description="Calculate time spent coding by using commit timestamps",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    # add general arguments
    parser.add_argument('directory', type=str, default='.',
                        help="Directory where the repository is contained     (. by default)",
                        metavar="DIRECTORY")
    parser.add_argument('--repo', '-r', type=str, default=None, choices=vcs.SUPPORTED_VCS,
                        help="Repository type for which the stats should be generated",
                        metavar="TYPE", dest='vcs')
    parser.add_argument('--cluster-algo', '-c', default='simple', choices=CLUSTERING_ALGORITHMS,
                        help="What algorithm should be used to cluster individual commits into coding sessions",
                        metavar="ALGO", dest='cluster_algo')
    parser.add_argument('--format', '-f', type=str, default='table', choices=OUTPUT_FORMATS,
                        help="Output format (formatted table by default)",
                        metavar="FORMAT", dest='output')

    minutes = lambda m: timedelta(minutes=int(m))

    # add arguments for algorithms
    parser.add_argument('--break', '-b', type=minutes, default=DEFAULT_BREAK_TIME,
                        help="Maximum time between commits which are still considered a single coding session",
                        metavar="MINUTES", dest='epsilon')
    parser.add_argument('--initial', '-i', type=minutes, default=DEFAULT_INITIAL_TIME,
                        help="Time before first commit within a coding session",
                        metavar="MINUTES", dest='initial_time')

    return parser


CLUSTERING_ALGORITHMS = ['simple']
OUTPUT_FORMATS = ['table', 'json']

DEFAULT_BREAK_TIME = timedelta(minutes=30)
DEFAULT_INITIAL_TIME = timedelta(minutes=5)


### Logic

def calculate_statistics(args):
    ''' Calculates statistics, as dictated by command line args.
    @return: List of Contributor tuples
    '''
    commit_history = vcs.retrieve_commit_history(args.directory, args.vcs)
    grouped_commits = stats.group_by_contributors(commit_history)
    coding_sessions = stats.cluster_commits(grouped_commits, args.cluster_algo, args.epsilon)
    contributors = stats.compute_time_stats(coding_sessions, args.initial_time)

    return sorted(contributors, key = lambda c: len(c.commits), reverse=True)


if __name__ == '__main__':
    main()