'''
Generating output in various formats.
'''
from collections import OrderedDict
from datetime import timedelta
from stats import calculate_totals
import os


def format_output(repo_dir, contributors, output_format):
    ''' Formats the output in specified format.
    @param repo_dir: Path to directory with repo that had its statistics generated
    @param contributors: List of Contributor tuples
    @param output_format: Name of output format
    '''
    output_func = globals().get('output_' + output_format)
    if not output_func:
        raise ValueError, "Unknown or unsupported output format '%s'" % output_format

    repo_name = os.path.basename(repo_dir)
    contribs = map(to_output_dict, contributors)
    totals = to_output_dict(calculate_totals(contributors))
    return output_func(repo_name, contribs, totals)

def to_output_dict(contributor):
    ''' Converts Contributor tuple into output dictionary. '''
    res = OrderedDict()
    res['name'] = contributor.name
    res['sessions'] = len(contributor.sessions)
    res['commits'] = sum(len(s.commits) for s in contributor.sessions)
    res['time'] = contributor.total_time
    return res


## Formatting functions

def output_table(repo_name, contribs, totals):
    ''' Outputs the repository statistics as table. '''
    items = contribs + [totals]
    if not items:   return ''

    to_str = (lambda obj: timedelta_to_str(obj)
                          if isinstance(obj, timedelta) else str(obj))

    # do some calculations for cells' dimensions
    labels = items[0].keys()
    max_col_lens = [max(map(len, [to_str(item[key]) for item in items] + labels))
                    for key in labels]
    max_row_len = sum(max_col_lens) + (len(labels) - 1)

    def make_row(cell_func):
        return str.join(' ', (cell_func(label).ljust(col_len)
                              for label, col_len in zip(labels, max_col_lens)))

    lines = ["Statistics for '%s'" % repo_name, '']

    # format header
    lines.append(make_row(lambda label: label))
    lines.append('-' * max_row_len)

    # format rows with contributors' stats
    for c in contribs:
        row = make_row(lambda key: to_str(c[key]))
        lines.append(row)

    # format footer with aggregate totals
    lines.append('-' * max_row_len)
    lines.append(make_row(lambda key: to_str(totals[key])))

    return str.join('\n', lines)

def output_json(repo_name, contribs, totals):
    ''' Outputs the repository statistics in JSON format. '''
    import json

    totals = dict(item for item in totals.iteritems() if item[0] != 'name')
    res = {'repo': repo_name, 'contributors': contribs, 'total': totals}
    return json.dumps(res, default=timedelta_to_str)


### Utilities

def timedelta_to_str(td):
    ''' Converts timedelta into nice, user-readable string. '''
    res = ''
    if td.days != 0: res += str(td.days) + "d "

    seconds = td.seconds
    hours = seconds / 3600  ; seconds -= hours * 3600
    minutes = seconds / 60  ; seconds -= minutes * 60

    parts = (str(x).rjust(2, '0') for x in (hours, minutes, seconds))
    res += str.join(":", parts)

    return res