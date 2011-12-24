'''
Generating output in various formats.
'''
from collections import OrderedDict
from datetime import timedelta
from stats import calculate_totals


def format_stats(contributors, output=str):
    ''' Formats the statistics using the specified output method. '''
    totals = calculate_totals(contributors)
    stats = [OrderedDict([('name', c.name), ('commits', len(c.commits)), ('time', c.total_time)])
             for c in contributors + [totals]]

    if output:
        if callable(output):    return output(stats)
        else:                   return output.dumps(stats, default=timedelta_to_str)
    return stats


def dicts_to_table(dicts):
    ''' Pretty prints the list of dictionaries as a table. '''
    if not dicts:    return ''

    lines  = []
    to_str = (lambda obj: timedelta_to_str(obj)
                          if isinstance(obj, timedelta) else str(obj))

    labels = dicts[0].keys()
    max_col_lens = [max(map(len, [to_str(d[key]) for d in dicts] + labels))
                    for key in labels]
    max_row_len = sum(max_col_lens) + (len(labels) - 1)

    # format header
    lines.append(str.join(' ', (label.ljust(col_len)
                                for label, col_len in zip(labels, max_col_lens))))
    lines.append('-' * max_row_len)

    # format rows
    for d in dicts:
        lines.append(str.join(' ', (to_str(d[key]).ljust(col_len)
                                    for key, col_len in zip(labels, max_col_lens))))

    return str.join('\n', lines)


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