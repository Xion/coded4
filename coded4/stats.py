'''
Code for calculating statistics based on commit history.
'''
from collections import namedtuple
from itertools import chain
from datetime import timedelta
import vcs


Contributor = namedtuple('Contributor', ['name', 'commits', 'total_time'])


def retrieve_commit_history(directory, vcs_name):
    ''' Retrieves history of commit for given repository.
    @return: List of Commit tuples
    '''
    history_func = getattr(vcs, vcs_name + '_history', None)
    if not history_func:
        raise ValueError, "Version control system '%s' is not supported" % vcs_name

    history = history_func(directory)
    return sorted(history, key=lambda c: c.time, reverse=True)

def group_by_contributors(commit_history):
    ''' Goes through commit history and groups commits by their authors.
    @param commit_history: List of Commit tuples
    @return: Dictionary mapping author names to lists of Commit tuples
    '''
    commits = {}
    for commit in commit_history:
        commit_list = commits.setdefault(commit.author, [])
        commit_list.append(commit)

    return commits

def cluster_commits(grouped_commits, cluster_algo, epsilon):
    ''' Clusters commits for every contributor in given dictionary. 
    @param grouped_commits: Dictionary mapping contributor names to lists of Commit tuples
    @param cluster_algo: Name of clustering algorithm
    @param epsilon: Temporal distance for the epsilon-neighborhood
    @return: Dictionary mapping author names to lists of coding sessions
    '''
    cluster_func = globals().get(cluster_algo + '_clustering')
    if not cluster_func:
        raise ValueError, "Unknown clustering algorithm '%s'" % cluster_algo

    clustered = {}
    for author, commits in grouped_commits.iteritems():
        sessions = cluster_func(commits, epsilon)
        clustered[author] = sessions

    return clustered

def compute_time_stats(coding_sessions, initial_time):
    ''' Calculates time statistics, given list of coding sessions for every contributor.
    @param coding_sessions: Dictionary mapping contributor names to lists of coding sessions
    @return: List of Contributor tuples
    '''
    contributors = []
    for author, sessions in coding_sessions.iteritems():
        total_time = timedelta()
        for s in sessions:
            total_time += initial_time
            total_time += s[0].time - s[-1].time

        # TODO; Contributor could store list of sessions rather than flat list of commits
        # so that we could extract even more interesting stats (e.g. longest/shortest/average session)
        commits = list(chain(*sessions))
        contributors.append(Contributor(author, commits, total_time))        

    return contributors


def calculate_totals(contributors):
    ''' Given list of contributors, calculates aggregate statistics.
    @return: Fake Contributor tuple which contains the aggregated stats
    '''
    if not contributors:    return
    measures = [('commits', []), ('total_time', timedelta())]

    sums = [initial for _, initial in measures]
    for c in contributors:
        for i in xrange(0, len(measures)):
            attr, _ = measures[i]
            sums[i] += getattr(c, attr)

    return Contributor("(total)", *sums)


### Clustering algorithms

def simple_clustering(commits, epsilon):
    ''' Divides list of commits into clusters (coding sessions) using simple clustering.
    @param epsilon: Maximum time interval between commit in single session
    @return: List of lists of Commit tuples
    '''
    sessions = []

    session = []
    commit_iter = iter(commits)
    while True:
        commit = next(commit_iter, None)
        if not commit:
            if session: sessions.append(session)
            break

        # if interval between commits is too long, assume end of session
        if session and last_commit_time - commit.time > epsilon:
            sessions.append(session)
            session = []
        session.append(commit)
        last_commit_time = commit.time

    return sessions
