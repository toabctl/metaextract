# -*- coding: utf-8 -*-
#
# Copyright (c) 2016, Thomas Bechtold <thomasbechtold@jpberlin.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function

from distutils.core import Command
import json


# define the data format version. Increase if
# - a key is renamed
# - a key is removed
DATA_VERSION = 1


class metaextract(Command):
    """a distutils command to extract metadata"""
    description = "extract package metadata"
    user_options = [
        ("output=", "o", "output for metadata json")
    ]

    def initialize_options(self):
        self.output = None

    def finalize_options(self):
        pass

    def run(self):
        data = dict()
        # keep list ordered!
        for key in ['data_files', 'entry_points', 'extras_require',
                    'install_requires', 'python_requires', 'setup_requires',
                    'scripts', 'tests_require', 'tests_suite']:
            if hasattr(self.distribution, key):
                data[key] = getattr(self.distribution, key)
                # dict_items objects can not be serialized with json
                if data[key].__class__.__name__ == 'dict_items':
                    data[key] = list(data[key])
                if key == 'entry_points' and isinstance(data[key], dict):
                    for k, v in data[key].items():
                        if isinstance(v, set):
                            data[key][k] = list(v)

        # keep list ordered!
        for func in ['get_author', 'get_author_email', 'get_classifiers',
                     'get_contact', 'get_contact_email', 'get_description',
                     'get_download_url', 'get_fullname', 'get_keywords',
                     'get_license', 'get_long_description', 'get_mainainer',
                     'get_maintainer_email', 'get_name', 'get_url',
                     'get_version', 'get_download_url',
                     'get_fullname', 'get_author', 'get_author_email',
                     'has_ext_modules']:
            if hasattr(self.distribution, func):
                data['{}'.format(func.replace('get_', ''))] = getattr(
                    self.distribution, func)()

        data_with_version = {
            'version': DATA_VERSION,
            'data': data
        }

        if self.output:
            with open(self.output, "w+") as f:
                f.write(json.dumps(data_with_version, indent=2,
                                   sort_keys=True, default=str))
        else:
            print(json.dumps(data_with_version, indent=2,
                             sort_keys=True, default=str))
