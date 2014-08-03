#!/usr/bin/env python
"""
coded4
Setup script
"""
import ast
import os
from setuptools import setup, find_packages


def read_tags(filename):
    """Reads values of "magic tags" defined in the given Python file.

    :param filename: Python filename to read the tags from
    :return: Dictionary of tags
    """
    with open(filename) as f:
        ast_tree = ast.parse(f.read(), filename)

    res = {}
    for node in ast.walk(ast_tree):
        if type(node) is not ast.Assign:
            continue

        target = node.targets[0]
        if type(target) is not ast.Name:
            continue

        if not (target.id.startswith('__') and target.id.endswith('__')):
            continue

        name = target.id[2:-2]
        res[name] = ast.literal_eval(node.value)

    return res


tags = read_tags(os.path.join('coded4', '__init__.py'))


setup(name="coded4",
      version=tags['__version__'],
      description="Time-based statistics for Git and Hg repositories",
      author=tags['__author__'],
      author_email="karol.kuczmarski@gmail.com",
      url="http://github.com/Xion/coded4",
      license=tags['__license__'],

      classifiers = [
         'Development Status :: 4 - Beta',
         'Intended Audience :: Developers',
         'Intended Audience :: Information Technology',
         'License :: OSI Approved :: MIT License',
         'Operating System :: OS Independent',
         'Programming Language :: Python',
         'Programming Language :: Python :: 2.7',
         'Topic :: Software Development',
      ],

      packages = find_packages(),
      entry_points = {
          'console_scripts': [
              'coded4 = coded4.__main__:main',
          ],
      },
)
