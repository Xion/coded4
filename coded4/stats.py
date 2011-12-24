'''
Code for calculating statistics based on commit history.
'''
from collections import namedtuple
from datetime import timedelta
import vcs


Contributor = namedtuple('Contributor', ['name', 'commits', 'total_time'])


def calculate_stats(directory, vcs_name, initial_time, break_time):
    ''' Calculates statistics for given repository.
    @return: List of Contributor tuples
    '''
    history_func = getattr(vcs, vcs_name + '_history', None)
    if not history_func:
        raise ValueError, "Version control system '%s' is not supported" % vcs

    history = history_func(directory)
    commits = {}

    # go through history once to extract all contributors
    for commit in sorted(history, key=lambda c: c.time, reverse=True):
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

    print sums[1]
    return Contributor("(total)", *sums)
