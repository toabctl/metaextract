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

import argparse
import json

from . import utils as meta_utils


def main():
    parser = argparse.ArgumentParser(prog="metaextract")
    parser.add_argument('archive', type=str, nargs=1,
                        help='filename of the archive')
    args = parser.parse_args()
    archive = args.archive[0]
    data = meta_utils.from_archive(archive)
    print(json.dumps(data, indent=4, sort_keys=True))


# for debugging
if __name__ == '__main__':
    main()
