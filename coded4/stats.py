"""
Code for calculating statistics based on commit history.
"""
from collections import namedtuple
from datetime import timedelta
from itertools import chain, starmap

from taipan.collections import dicts


class Contributor(namedtuple('Contributor',
                             ['name', 'sessions', 'total_time'])):
    """Represents a single contributor to the repository."""

    @property
    def commits(self):
        return list(chain(self.sessions))

    @classmethod
    def from_coding_sessions(cls, author, sessions):
        """Create the Contributor structure from author name
        and list of coding Sessions.
        """
        total_time = sum((s.total_time for s in sessions), timedelta())
        return cls(author, sessions, total_time)


def compute_time_stats(coding_sessions):
    """Calculates time statistics,
    given list of coding sessions for every contributor.

    :param coding_sessions: Dictionary mapping contributor names
                            to lists of coding Sessions

    :return: List of Contributor tuples
    """
    return starmap(Contributor.from_coding_sessions,
                   dicts.iteritems(coding_sessions))


def calculate_totals(contributors):
    """Given list of contributors, calculates aggregate statistics.

    :return: Fake Contributor tuple which contains the aggregated stats,
             or None
    """
    if not contributors:
        return

    measures = [('sessions', []), ('total_time', timedelta())]

    sums = [initial for _, initial in measures]
    for c in contributors:
        for i in xrange(0, len(measures)):
            attr, _ = measures[i]
            sums[i] += getattr(c, attr)

    return Contributor("TOTAL", *sums)
