#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup for beets-extrafiles."""
from setuptools import setup

setup(
    name='beets-extrafiles',
    version='0.0.1',
    description=(
        'A plugin for beets that copies additional files and directories '
        'during the import process.'
    ),
    author='Jan Holthuis',
    author_email='holthuis.jan@gmail.com',
    url='https://github.com/Holzhaus/beets-extrafiles',
    license='MIT',
    packages=['beetsplug'],
    namespace_packages=['beetsplug'],
    test_suite='tests',
    install_requires=['beets>=1.4.7'],
    classifiers=[
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
