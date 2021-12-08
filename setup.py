#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Thomas Bechtold <thomasbechtold@jpberlin.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import setuptools
import metaextract.setup

from metaextract import __version__

with open("README.rst", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="metaextract",
    version=__version__,
    license="Apache-2.0",
    description="get metadata for python modules",
    long_description=long_description,
    author="Thomas Bechtold",
    author_email="thomasbechtold@jpberlin.de",
    url='http://github.com/toabctl/metaextract',
    packages=['metaextract'],
    cmdclass=metaextract.setup.get_cmdclass(),
    tests_require=["flake8", "pytest", "mock"],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    entry_points={
        'console_scripts': [
            'metaextract=metaextract.cmds:main',
        ],
    }
)
