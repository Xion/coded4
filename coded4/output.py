"""
Generating output in various formats.
"""
from __future__ import unicode_literals

from collections import OrderedDict
from copy import deepcopy
from datetime import timedelta
import os

from coded4.stats import calculate_totals


def format_output(repo_dir, contributors, output_format):
    """Formats the output in specified format.

    :param repo_dir: Path to directory with repo that had its statistics generated
    :param contributors: List of Contributor tuples
    :param output_format: Name of output format
    """
    output_func = globals().get('output_' + output_format)
    if not output_func:
        raise ValueError(
            "Unknown or unsupported output format '%s'" % output_format)

    repo_name = os.path.basename(repo_dir)
    contribs = map(to_output_dict, contributors)
    totals = to_output_dict(calculate_totals(contributors))
    return output_func(repo_name, contribs, totals)


def to_output_dict(contributor):
    """Converts Contributor tuple into output dictionary. """
    res = OrderedDict()
    res['name'] = contributor.name
    res['sessions'] = len(contributor.sessions)
    res['commits'] = sum(len(s.commits) for s in contributor.sessions)
    res['time'] = contributor.total_time
    return res


# Formatting functions

str_ = ''.__class__


def output_table(repo_name, contribs, totals):
    """Outputs the repository statistics as table. """
    items = contribs + [totals]
    if not items:
        return ""

    to_str = (lambda obj: timedelta_to_str(obj)
                          if isinstance(obj, timedelta) else str(obj))

    # do some calculations for cells' dimensions
    labels = items[0].keys()
    max_col_lens = [max(map(len, [to_str(item[key]) for item in items] + labels))
                    for key in labels]
    max_row_len = sum(max_col_lens) + (len(labels) - 1)

    def make_row(cell_func):
        return ' '.join(cell_func(label).ljust(col_len)
                        for label, col_len in zip(labels, max_col_lens))

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

    return os.linesep.join(lines)


def output_csv(repo_name, contribs, totals):
    """Outputs the repository statistics in CSV format."""
    import csv
    from StringIO import StringIO

    utf8 = lambda x: str_(x).encode('utf-8')

    result = StringIO()
    writer = csv.writer(result, delimiter=utf8(','),
                        quotechar=utf8('"'), quoting=csv.QUOTE_MINIMAL)

    def write_contrib(contrib):
        """Write a single contributor as CSV, handling Unicode encoding."""
        contrib = contrib.copy()
        for key in ('name', 'time'):
            contrib[key] = utf8(contrib[key])
        writer.writerow(contrib.values())

    for contrib in contribs:
        write_contrib(contrib)
    write_contrib(totals)

    result.seek(0)
    return result.read()


def output_json(repo_name, contribs, totals):
    """Outputs the repository statistics in JSON format. """
    import json
    return json.dumps(repo_dict(repo_name, contribs, totals),
                      default=timedelta_to_str)


def output_yaml(repo_name, contribs, totals):
    """Output the repository statistics in YAML format."""
    from StringIO import StringIO

    result = StringIO()
    print >>result, "repo:", repo_name

    def write_contrib(contrib, indent=0):
        prefix = "- "
        indent = " " * indent
        for key, value in contrib.items():
            print >>result, indent + "%s%s: %s" % (prefix, key, value)
            prefix = "  "

    print >>result, "contributors:"
    for contrib in contribs:
        write_contrib(contrib)

    print >>result, "totals:"
    write_contrib(dict_without(totals, ['name']))

    result.seek(0)
    return result.read()


def output_plist(repo_name, contribs, totals):
    """Outputs the repository statistics in .plist format."""
    import plistlib

    res = repo_dict(repo_name, contribs, totals)
    for c in res['contributors'] + [res['total']]:
        c['time'] = timedelta_to_str(c['time'])

    return plistlib.writePlistToString(res)


def output_xml(repo_name, contribs, totals):
    """Outputs the repository statistics in general XML format."""
    from StringIO import StringIO
    import xml.etree.ElementTree as ET

    stats = ET.Element('statistics', attrib={'repo': repo_name})

    def write_contrib(contrib, parent, tag='contributor'):
        attrs = dict((key, str_(value)) for key, value in contrib.items())
        ET.SubElement(parent, tag, attrs)

    contributors = ET.SubElement(stats, 'contributors')
    for contrib in contribs:
        write_contrib(contrib, parent=contributors)
    write_contrib(dict_without(totals, ['name']), parent=stats, tag='totals')

    result = StringIO()
    ET.ElementTree(stats).write(result, encoding='utf-8', xml_declaration=True)

    result.seek(0)
    return result.read()


# Utilities

def repo_dict(repo_name, contribs, totals):
    """Return a dictionary of repo statistics,
    suitable for certain formats such as JSON.
    """
    totals = dict(item for item in totals.items() if item[0] != 'name')
    return {
        'repo': repo_name,
        'contributors': deepcopy(contribs),
        'total': totals,
    }


def timedelta_to_str(td):
    """Converts timedelta into nice, user-readable string. """
    res = ''
    if td.days != 0:
        res += str_(td.days) + "d "

    seconds = td.seconds
    hours = seconds / 3600  ; seconds -= hours * 3600
    minutes = seconds / 60  ; seconds -= minutes * 60

    parts = (str_(x).rjust(2, '0') for x in (hours, minutes, seconds))
    res += ":".join(parts)

    return res


def dict_without(dict_, keys):
    """Returns a dictionary without specified keys.
    :raise KeyError: If any of the keys do not exist in the dictionary
    """
    dict_ = dict_.copy()
    for key in keys:
        dict_.pop(key)
    return dict_
