#!/usr/bin/env python

import os
import sys
import logparser 

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

test_requires = ["nose"]


setup(
    name='logparser',
    version = logparser.__version__,
    description='Fieldaware assignment: log parser and profiler',
    author='Jacek Spera',
    author_email='jacekspera@gmail.com',
    packages=['logparser'],
    requires=test_requires,
    zip_safe=False,
)
