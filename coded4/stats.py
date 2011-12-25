'''
Code for calculating statistics based on commit history.
'''
from collections import namedtuple
from itertools import chain
from datetime import timedelta
import vcs


Contributor = namedtuple('Contributor', ['name', 'sessions', 'total_time'])
Contributor.commits = property(lambda c: list(chain(*c.sessions)))


def compute_time_stats(coding_sessions):
    ''' Calculates time statistics, given list of coding sessions for every contributor.
    @param coding_sessions: Dictionary mapping contributor names to lists of coding sessions
    @return: List of Contributor tuples
    '''
    contributors = []
    for author, sessions in coding_sessions.iteritems():
        total_time = sum((s.total_time for s in sessions), timedelta())
        contributors.append(Contributor(author, sessions, total_time))        

    return contributors


def calculate_totals(contributors):
    ''' Given list of contributors, calculates aggregate statistics.
    @return: Fake Contributor tuple which contains the aggregated stats
    '''
    if not contributors:    return
    measures = [('sessions', []), ('total_time', timedelta())]

    sums = [initial for _, initial in measures]
    for c in contributors:
        for i in xrange(0, len(measures)):
            attr, _ = measures[i]
            sums[i] += getattr(c, attr)

    return Contributor("TOTAL", *sums)
