#!/usr/bin/env python
'''
Executable script.
'''
from __future__ import unicode_literals

import vcs
import cluster
import approx
import stats
from output import format_output

from datetime import timedelta
import argparse



def main():
    argparser = create_argument_parser()
    args = argparser.parse_args()

    if args:
        contributors = calculate_statistics(args)
        print format_output(args.directory, contributors, args.output)


def create_argument_parser():
    parser = argparse.ArgumentParser(description="Calculate time spent coding by using commit timestamps",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    # add general arguments
    parser.add_argument('directory', type=str, default='.',
                        help="Directory where the repository is contained (. by default)",
                        metavar="DIRECTORY")
    parser.add_argument('--repo', '-r', type=str, default=None, choices=vcs.SUPPORTED_VCS,
                        help="Repository type for which the stats should be generated",
                        metavar="TYPE", dest='vcs')
    parser.add_argument('--format', '-f', type=str, default='table', choices=OUTPUT_FORMATS,
                        help="Output format (formatted table by default)",
                        metavar="FORMAT", dest='output')

    # add algorithms
    parser.add_argument('--cluster-algo', '-c', default='simple', choices=CLUSTERING_ALGORITHMS,
                        help="What algorithm should be used to cluster individual commits. "
                        + "Possible values: %(choices)s",
                        metavar="ALGO", dest='cluster_algo')
    parser.add_argument('--approx-algo', '-a', default='start10', choices=APPROXIMATION_ALGORITHMS,
                        help="What algorithms should be used to approximate time spent coding. "
                        + "Possible values: %(choices)s",
                        metavar="ALGO", dest='approx_algo')

    # add other options
    minutes = lambda m: timedelta(minutes=int(m))
    parser.add_argument('--epsilon', '--eps', '-e', type=minutes, default=minutes(DEFAULT_EPSILON_MINUTES),
                        help="Maximum time between commits which are still considered a single coding session "
                        + "(default: %s)" % DEFAULT_EPSILON_MINUTES,
                        metavar="MINUTES", dest='epsilon')
    
    return parser


OUTPUT_FORMATS = ['table', 'json']
CLUSTERING_ALGORITHMS = ['simple']
APPROXIMATION_ALGORITHMS = {
    'start10': "Simple algorithm that adds 10 minutes before first commit",
    'ten2five': "Simple algorithm that adds 10 minutes before first and 5 minutes after last commit",
    'quarter_end': "Uses average time between commits in session, adding 1/4th of it after last commit",
}

DEFAULT_EPSILON_MINUTES = 30


### Logic

def calculate_statistics(args):
    ''' Calculates statistics, as dictated by command line args.
    @return: List of Contributor tuples
    '''
    commit_history = vcs.retrieve_commit_history(args.directory, args.vcs)
    grouped_commits = cluster.group_by_contributors(commit_history)
    clustered_commits = cluster.cluster_commits(grouped_commits, args.cluster_algo, args.epsilon)
    coding_sessions = approx.approximate_coding_sessions(clustered_commits, args.approx_algo)
    contributors = stats.compute_time_stats(coding_sessions)

    return sorted(contributors, key = lambda c: len(c.commits), reverse=True)


if __name__ == '__main__':
    main()