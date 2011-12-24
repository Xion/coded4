#!/usr/bin/env python
'''
Executable script.
'''
from __future__ import unicode_literals

from vcs import SUPPORTED_VCS, detect_vcs
from stats import calculate_stats
from output import format_stats, dicts_to_table
from datetime import timedelta
import argparse



def main():
    argparser = create_argument_parser()
    args = argparser.parse_args()

    if args:
        vcs_name = args.vcs or detect_vcs(args.directory)
        contributors = calculate_stats(args.directory, vcs_name, args.initial_time, args.break_time)
        contributors = sorted(contributors, key = lambda c: len(c.commits), reverse=True)

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


DEFAULT_BREAK_TIME = timedelta(minutes=30)
DEFAULT_INITIAL_TIME = timedelta(minutes=10)



if __name__ == '__main__':
    main()