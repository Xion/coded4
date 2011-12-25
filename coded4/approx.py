'''
Algorithms for approximating coding sessions
'''
from collections import namedtuple
from datetime import timedelta


Session = namedtuple('Session', ['commits', 'time_before_first', 'time_after_last'])

def __session_total_time(session):
	total = session.time_before_first + session.time_after_last
	if session.commits:
		total += session.commits[0].time - session.commits[-1].time
	return total

Session.total_time = property(__session_total_time)


def approximate_coding_sessions(clustered_commits, approx_algo):
    ''' Approximates the coding sessions that resulted in given clustered commits.
    @param clustered_commits: Dictionary mapping contributor names to lists of commit clusters
    @param approx_algo: Name of approximation algorithm
    @return: Dictionary mapping contributor names to lists of Session tuples
    '''
    approx_func = globals().get(approx_algo + '_approximation')
    if not approx_func:
        raise ValueError, "Unknown approximation '%s'" % approx_algo

    sessions_dict = {}
    for author, commit_clusters in clustered_commits.iteritems():
        sessions = map(approx_func, commit_clusters)
        sessions_dict[author] = sessions

    return sessions_dict


## Algorithms

def start10_approximation(commit_cluster):
	''' A simple approximation that adds 10 minutes before the first commit in cluster. '''
	return Session(commit_cluster, timedelta(minutes=10), timedelta())

def ten2five_approximation(commit_cluster):
	''' A simple approximation that adds 10 minutes before the first commit and 5 after the last one,
	except for sessions consisting of single commit.
	'''
	if len(commit_cluster) > 1:
		return Session(commit_cluster, timedelta(minutes=10), timedelta(minutes=5))
	else:
		return Session(commit_cluster, timedelta(minutes=5), timedelta())