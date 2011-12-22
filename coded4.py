'''
coded4
Calculates time spent on coding based on commit timestamps
'''

__author__ = 'Karol Kuczmarski "Xion"'
__license__ = "MIT"
__version__ = "0.1"


from datetime import datetime, timedelta
import os
import argparse


def main():
	argparser = create_argument_parser()
	args = argparser.parse_args()


def create_argument_parser():
	parser = argparse.ArgumentParser(description="Calculate time spent coding by using commit timestamps",
									 formatter_class=argparse.RawDescriptionHelpFormatter)
	
	minutes = lambda m: timedelta(minutes=m)

	parser.add_argument('dir', metavar="DIRECTORY", type=str, default='.',
						help="Directory where the repository is contained (. by default)")
	parser.add_argument('--break', metavar="MINUTES", type=minutes, default=DEFAULT_BREAK_TIME,
						help="Maximum time between commits which are still considered a single coding session")
	parser.add_argument('--initial', metavar="MINUTES", type=minutes, default=DEFAULT_INITIAL_TIME,
						help="Time before first commit within a coding session")

	return parser


DEFAULT_BREAK_TIME = timedelta(minutes=30)
DEFAULT_INITIAL_TIME = timedelta(minutes=10)


###############################################################################


if __name__ == '__main__':
	main()