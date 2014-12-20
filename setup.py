#!/usr/bin/env python

__version__ = "2.0.0-dev"

from setuptools import find_packages, setup
from glob import glob

classes = """
    Development Status :: 1 - Planning
    License :: OSI Approved :: BSD License
    Topic :: Scientific/Engineering
    Topic :: Scientific/Engineering :: Bio-Informatics
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: 3.4
    Operating System :: Unix
    Operating System :: POSIX
    Operating System :: MacOS :: MacOS X
"""
classifiers = [s.strip() for s in classes.split('\n') if s]

description = ('Quantitative insights into microbial ecology')

with open('README.md') as f:
    long_description = f.read()

setup(name='metoo',
      version=__version__,
      license='BSD',
      description=description,
      long_description=long_description,
      author="qiime development team",
      author_email="gregcaporaso@gmail.com",
      maintainer="qiime development team",
      maintainer_email="gregcaporaso@gmail.com",
      url='http://qiime.org',
      test_suite='nose.collector',
      scripts=glob('scripts/*'),
      packages=find_packages(),
      # peewee[playhouse] won't be necessary for postgresql
      # ... also very creepy
      install_requires=['click', 'tornado', 'peewee', 'scikit-bio'],
      extras_require={'test': ["nose >= 0.10.1", "pep8", "flake8"],
                      'doc': ["Sphinx == 1.2.2", "sphinx-bootstrap-theme"]},
      classifiers=classifiers
      )
