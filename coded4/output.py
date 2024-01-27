"""Generating output in various formats."""


import os
from collections import OrderedDict
from copy import deepcopy
from datetime import timedelta
from itertools import starmap

from taipan.collections import dicts

from coded4.stats import calculate_totals


def format_output(repo_dir, contributors, output_format):
    """Formats the output in specified format.

    :param repo_dir: Path to directory with repo that had its statistics generated
    :param contributors: List of Contributor tuples
    :param output_format: Name of output format
    """
    output_func = globals().get("output_" + output_format)
    if not output_func:
        raise ValueError(
            "Unknown or unsupported output format '%s'" % output_format)

    repo_name = os.path.basename(repo_dir)
    contribs = list(map(to_output_dict, contributors))
    totals = to_output_dict(calculate_totals(contributors))
    return output_func(repo_name, contribs, totals)


def to_output_dict(contributor):
    """Converts Contributor tuple into output dictionary."""
    res = OrderedDict()
    res["name"] = contributor.name
    res["sessions"] = len(list(contributor.sessions))
    res["commits"] = sum(len(s.commits) for s in contributor.sessions)
    res["time"] = contributor.total_time
    return res


# Formatting functions

str_ = "".__class__


def output_table(repo_name, contribs, totals):
    """Outputs the repository statistics as table."""
    items = [*contribs, totals]
    if not items:
        return ""

    def to_str(obj):
        return timedelta_to_str(obj) if isinstance(obj, timedelta) else str(obj)

    # do some calculations for cells' dimensions
    labels = list(items[0].keys())
    max_col_lens = [max(list(map(len, [to_str(item[key]) for item in items] + labels)))
                    for key in labels]
    max_row_len = sum(max_col_lens) + (len(labels) - 1)

    def make_row(cell_func):
        return " ".join(cell_func(label).ljust(col_len)
                        for label, col_len in zip(labels, max_col_lens))

    lines = ["Statistics for '%s'" % repo_name, ""]

    # format header
    lines.extend((make_row(lambda label: label), "-" * max_row_len))

    # format rows with contributors' stats
    for c in contribs:
        row = make_row(lambda key, c=c: to_str(c[key]))
        lines.append(row)

    # format footer with aggregate totals
    lines.extend(("-" * max_row_len, make_row(lambda key: to_str(totals[key]))))

    return os.linesep.join(lines)


def output_csv(repo_name, contribs, totals):
    """Outputs the repository statistics in CSV format."""
    import csv
    from io import StringIO

    def utf8(x):
        return str_(x).encode("utf-8")

    result = StringIO()
    writer = csv.writer(result, delimiter=utf8(","),
                        quotechar=utf8('"'), quoting=csv.QUOTE_MINIMAL)

    def write_contrib(contrib) -> None:
        """Write a single contributor as CSV, handling Unicode encoding."""
        contrib = contrib.copy()
        for key in ("name", "time"):
            contrib[key] = utf8(contrib[key])
        writer.writerow(list(contrib.values()))

    for contrib in contribs:
        write_contrib(contrib)
    write_contrib(totals)

    result.seek(0)
    return result.read()


def output_json(repo_name, contribs, totals):
    """Outputs the repository statistics in JSON format."""
    import json
    return json.dumps(repo_dict(repo_name, contribs, totals),
                      default=timedelta_to_str)


def output_yaml(repo_name, contribs, totals):
    """Output the repository statistics in YAML format."""
    from io import StringIO

    result = StringIO()
    print("repo:", repo_name, file=result)

    def write_contrib(contrib, indent=0) -> None:
        prefix = "- "
        indent = " " * indent
        for key, value in list(contrib.items()):
            print(indent + f"{prefix}{key}: {value}", file=result)
            prefix = "  "

    print("contributors:", file=result)
    for contrib in contribs:
        write_contrib(contrib)

    print("totals:", file=result)
    write_contrib(dicts.omit(["name"], from_=totals))

    result.seek(0)
    return result.read()


def output_plist(repo_name, contribs, totals):
    """Outputs the repository statistics in .plist format."""
    import plistlib

    res = repo_dict(repo_name, contribs, totals)
    for c in res["contributors"] + [res["total"]]:
        c["time"] = timedelta_to_str(c["time"])

    return plistlib.writePlistToString(res)


def output_xml(repo_name, contribs, totals):
    """Outputs the repository statistics in general XML format."""
    import xml.etree.ElementTree as ETree
    from io import StringIO

    stats = ETree.Element("statistics", attrib={"repo": repo_name})

    def write_contrib(contrib, parent, tag) -> None:
        ETree.SubElement(parent, tag, attrib=dicts.mapvalues(str_, contrib))

    contributors = ETree.SubElement(stats, "contributors")
    for contrib in contribs:
        write_contrib(contrib, parent=contributors, tag="contributor")
    write_contrib(dicts.omit(["name"], from_=totals),
                  parent=stats, tag="totals")

    result = StringIO()
    ETree.ElementTree(stats).write(result, encoding="utf-8", xml_declaration=True)

    result.seek(0)
    return result.read()


def output_sexp(repo_name, contribs, totals):
    """Output the repository statistics as an S-expression."""
    from io import StringIO

    result = StringIO()
    print('(repo "%s"' % repo_name, file=result)

    def write_contrib(contrib, tag, indent=0) -> None:
        indent = " " * indent
        print(indent + "({} {})".format(tag, " ".join(
            starmap('({} "{}")'.format, list(contrib.items())))), file=result)

    for contrib in contribs:
        write_contrib(contrib, tag="contributor", indent=1)
    write_contrib(dicts.omit(["name"], from_=totals), tag="totals", indent=1)

    # insert final closing parenthesis before the last newline
    result.seek(-len(os.linesep), 1)
    print(")", file=result)

    result.seek(0)
    return result.read()[:-len(os.linesep)]  # remove that last newline


# Utilities

def repo_dict(repo_name, contribs, totals):
    """Return a dictionary of repo statistics,
    suitable for certain formats such as JSON.
    """
    totals = dict(item for item in list(totals.items()) if item[0] != "name")
    return {
        "repo": repo_name,
        "contributors": deepcopy(contribs),
        "total": totals,
    }


def timedelta_to_str(td):
    """Converts timedelta into nice, user-readable string."""
    res = ""
    if td.days != 0:
        res += str_(td.days) + "d "

    seconds = td.seconds
    hours = seconds / 3600
    seconds -= hours * 3600
    minutes = seconds / 60
    seconds -= minutes * 60

    parts = (str_(x).rjust(2, "0") for x in (hours, minutes, seconds))
    res += ":".join(parts)

    return res
