'''
coded4
Calculates time spent on coding based on commit timestamps
'''

__author__ = 'Karol Kuczmarski "Xion"'
__license__ = "MIT"
__version__ = "0.1"


from datetime import datetime, timedelta
from collections import namedtuple
import argparse
import os
import subprocess


### Main function

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


### General

Commit = namedtuple('Commit', ['hash', 'time', 'author', 'message'])


### Git support

def git_history(path):
	''' Returns a list of Commit tuples with history for given Git repo. '''
	sep = '|'
	git_log_format = str.join(sep, ['%H', '%at', '%an', '%s'])
	git_log = 'git log --format=format:"%s"' % git_log_format
	log = exec_command(git_log)

	history = []
	for line in log.splitlines();
		commit_hash, timestamp, author, message = line.split(sep)
		time = datetime.fromtimestamp(timestamp)
		history.append(Commit(commit_hash, time, author, message))

	return history



### Utilities

def exec_command(cmd):
	''' Executes given shell command and returns its stdout as string. '''
	cmd_out = subprocess.Popen(cmd, shell=True, stdout=PIPE).stdout
	return cmd_out.read()



if __name__ == '__main__':
	main()