"""
Algorithms for approximating coding sessions
"""
from collections import namedtuple
from datetime import timedelta


class Session(namedtuple('Session',
                         ['commits', 'time_before_first', 'time_after_last'])):
    """Represents a single coding session.

    Session consists of commits, plus some approximated time before the first
    and after last commit.
    """
    @property
    def total_time(self):
        total = self.time_before_first + self.time_after_last
        if self.commits:
            total += self.commits[0].time - self.commits[-1].time
        return total


def approximate_coding_sessions(clustered_commits, approx_algo):
    """Approximates the coding sessions that resulted in given clustered commits.

    :param clustered_commits: Dictionary mapping contributor names
                              to lists of Commit clusters
    :param approx_algo: Name of approximation algorithm

    :return: Dictionary mapping contributor names to lists of Session tuples
    """
    approx_func = globals().get(approx_algo + '_approximation')
    if not approx_func:
        raise ValueError("Unknown approximation '%s'" % approx_algo)

    sessions_dict = {}
    for author, commit_clusters in clustered_commits.iteritems():
        sessions = map(approx_func, commit_clusters)
        sessions_dict[author] = sessions

    return sessions_dict


## Algorithms

SINGLE_COMMIT_TIMES = timedelta(minutes=5), timedelta()


def null_approximation(commit_cluster):
    """A "null" approximation that doesn't add any additional time.
    Useful for testing but not for much else.
    """
    return Session(commit_cluster, timedelta(), timedelta())


def start10_approximation(commit_cluster):
    """A simple approximation that adds 10 minutes
    before the first commit in cluster.
    """
    return Session(commit_cluster, timedelta(minutes=10), timedelta())


def ten2five_approximation(commit_cluster):
    """A simple approximation that adds 10 minutes before the first commit
    and 5 after the last one, except for sessions consisting of single commit.
    """
    if len(commit_cluster) > 1:
        return Session(commit_cluster,
                       timedelta(minutes=10), timedelta(minutes=5))
    return Session(commit_cluster, *SINGLE_COMMIT_TIMES)


def quarter_end_approximation(commit_cluster):
    """A slightly more sophisticated approximation that uses
    the average time between commits in a session.
    """
    diffs = commit_time_diff(commit_cluster)
    if diffs:
        average_diff = sum(diffs, timedelta()) / len(diffs)
        before_first = average_diff
        after_last = average_diff / 4    # quarter end
        return Session(commit_cluster, before_first, after_last)

    return Session(commit_cluster, *SINGLE_COMMIT_TIMES)


## Utilities

def commit_time_diff(commits):
    """Returns time differences between commits. """
    if not commits or len(commits) == 1:
        return []

    diffs = []
    for i in xrange(0, len(commits) - 1):
        diffs.append(commits[i].time - commits[i+1].time)
    return diffs
