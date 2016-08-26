#!/usr/bin/env python

from distutils.core import setup

setup(
    name='testpkg',
    version='1.0',
    description='Test PKG',
    packages=['testpkg', 'testpkg.command'],
)
