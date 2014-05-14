#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

install_requires = open('requirements.txt').read().split()

try:
    import argparse
except ImportError:
    install_requires.append('argparse')

setup(
    name='deba-bocho',
    version='0.2.1',
    provides=['bocho'],
    description='Slice up PDFs like a pro.',
    long_description=open('README.rst').read(),
    author='James Rutherford',
    author_email='jim@jimr.org',
    url='https://github.com/jimr/deba-bocho',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        ],
    license='MIT',
    test_suite='tests',
    scripts=['bocho.py'],
    py_modules=['bocho'],
    install_requires=install_requires,
)
