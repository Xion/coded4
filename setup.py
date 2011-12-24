#!/usr/bin/env python
'''
coded4
Setup script
'''
from setuptools import setup, find_packages
import coded4


setup(name="coded4",
	  version=coded4.__version__,
	  description="Time-based statistics for Git and Hg repositories",
	  author='Karol Kuczmarski "Xion"',
	  author_email="karol.kuczmarski@gmail.com",
	  url="http://github.com/Xion/coded4",
	  license="MIT",

	  classifiers = [
	     'Development Status :: 4 - Beta',
	     'Intended Audience :: Developers',
	     'Intended Audience :: Information Technology',
	     'License :: OSI Approved :: MIT License',
	     'Operating System :: OS Independent',
	     'Programming Language :: Python',
         'Programming Language :: Python :: 2.6',
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