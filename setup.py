#!/usr/bin/env python
"""coded4.
======

{description}
"""
import ast
import locale
import os

from setuptools import find_packages, setup


def read_tags(filename):
    """Reads values of "magic tags" defined in the given Python file.

    :param filename: Python filename to read the tags from
    :return: Dictionary of tags
    """
    with open(filename, encoding=locale.getpreferredencoding(False)) as f:
        ast_tree = ast.parse(f.read(), filename)

    res = {}
    for node in ast.walk(ast_tree):
        if type(node) is not ast.Assign:
            continue

        target = node.targets[0]
        if type(target) is not ast.Name:
            continue

        if not (target.id.startswith("__") and target.id.endswith("__")):
            continue

        name = target.id[2:-2]
        res[name] = ast.literal_eval(node.value)

    return res


def read_requirements(filename="requirements.txt"):
    """Reads the list of requirements from given file.

    :param filename: Filename to read the requirements from.
                     Uses ``'requirements.txt'`` by default.

    :return: Requirements as list of strings
    """
    # allow for some leeway with the argument
    if not filename.startswith("requirements"):
        filename = "requirements-" + filename
    if not os.path.splitext(filename)[1]:
        filename += ".txt"  # no extension, add default

    def valid_line(line):
        line = line.strip()
        return line and not any(line.startswith(p) for p in ("#", "-"))

    def extract_requirement(line):
        egg_eq = "#egg="
        if egg_eq in line:
            _, requirement = line.split(egg_eq, 1)
            return requirement
        return line

    with open(filename, encoding=locale.getpreferredencoding(False)) as f:
        lines = f.readlines()
        return list(map(extract_requirement, list(filter(valid_line, lines))))


tags = read_tags(os.path.join("coded4", "__init__.py"))
__doc__ = __doc__.format(**tags)


setup(name="coded4",
      version=tags["version"],
      description=tags["description"],
      long_description=__doc__,
      author=tags["author"],
      url="http://github.com/Xion/coded4",
      license=tags["license"],

      classifiers=[
         "Development Status :: 4 - Beta",
         "Intended Audience :: Developers",
         "Intended Audience :: Information Technology",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
         "Programming Language :: Python",
         "Programming Language :: Python :: 2.7",
         "Topic :: Software Development",
      ],

      install_requires=read_requirements(),

      packages=find_packages(),
      entry_points={
          "console_scripts": [
              "coded4 = coded4.__main__:main",
          ],
      },
)
