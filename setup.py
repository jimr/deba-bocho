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
    version='0.5.0',
    provides=['bocho'],
    description='Slice up PDFs like a pro.',
    long_description=open('README.rst').read(),
    author='James Rutherford',
    author_email='jim@jimr.org',
    url='https://github.com/jimr/deba-bocho',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
    ],
    license='MIT',
    test_suite='tests',
    entry_points={'console_scripts': 'bocho = bocho.cmd:main'},
    py_modules=['bocho'],
    packages=['bocho'],
    install_requires=install_requires,
)
