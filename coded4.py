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

	if args:
		vcs = args.vcs or detect_vcs(args.directory)
		contributors = calculate_stats(args.directory, vcs, args.initial_time, args.break_time)
		print_stats(contributors)


def create_argument_parser():
	parser = argparse.ArgumentParser(description="Calculate time spent coding by using commit timestamps",
									 formatter_class=argparse.RawDescriptionHelpFormatter)
	
	minutes = lambda m: timedelta(minutes=m)

	parser.add_argument('dir', type=str, default='.',
						help="Directory where the repository is contained (. by default)",
						metavar="DIRECTORY", dest='directory')
	parser.add_argument('--repo', type=str, default=None, choices=SUPPORTED_VCS,
						help="Repository type for which the stats should be generated",
						metavar="TYPE", dest='vcs')
	parser.add_argument('--break', type=minutes, default=DEFAULT_BREAK_TIME,
						help="Maximum time between commits which are still considered a single coding session",
						metavar="MINUTES", dest='break_time')
	parser.add_argument('--initial', type=minutes, default=DEFAULT_INITIAL_TIME,
						help="Time before first commit within a coding session",
						metavar="MINUTES", dest='initial_time')

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
	history_func = locals().get(vcs + '_history')
	if not history_func:
		raise ValueError, "Version control system '%s' is not supported" % vcs

	history = history_func(directory)
	contributors = {}

	# go through history once to extract all contributors
	for commit in history:
		contrib = contributors.setdefault(commit.author,
										  Contributor(commit.author, [], timedelta
		contrib.commits.append(commit)

	contributors = contributors.values()

	# calculate statistics for every contributor
	for contrib in contributors:
		in_session = False
		commit_iter = iter(contrib.commits)
		while True:
			commit = commit_iter.next(None)
			if not commit:	break
			if in_session:
				interval = commit.time - last_commit_time
				if interval > break_time:	# break (end of coding session)
					in_session = False
					continue
				commit.total_time += interval
			else:	# new coding session
				in_session = True
				contrib.total_time += initial_time
			last_commit_time = commit.time

	return contributors

def print_stats(contributors):
	pass


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