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

from contextlib import contextmanager
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile


__all__ = [
    "from_archive"
]


@contextmanager
def _extract_to_tempdir(archive_filename):
    """extract the given tarball or zipfile to a tempdir and change
    the cwd to the new tempdir. Delete the tempdir at the end"""
    if not os.path.exists(archive_filename):
        raise Exception("Archive '%s' does not exist" % (archive_filename))

    tempdir = tempfile.mkdtemp(prefix="metaextract_")
    current_cwd = os.getcwd()
    try:
        if tarfile.is_tarfile(archive_filename):
            with tarfile.open(archive_filename) as f:
                f.extractall(tempdir)
        elif zipfile.is_zipfile(archive_filename):
            with zipfile.ZipFile(archive_filename) as f:
                f.extractall(tempdir)
        else:
            raise Exception("Can not extract '%s'. "
                            "Not a tar or zip file" % archive_filename)
        os.chdir(tempdir)
        yield tempdir
    finally:
        os.chdir(current_cwd)
        shutil.rmtree(tempdir)


@contextmanager
def _enter_single_subdir(root_dir):
    """if the given directory has just a single subdir, enter that"""
    current_cwd = os.getcwd()
    try:
        dest_dir = root_dir
        dir_list = os.listdir(root_dir)
        if len(dir_list) == 1:
            first = os.path.join(root_dir, dir_list[0])
            if os.path.isdir(first):
                dest_dir = first
        else:
            dest_dir = root_dir
        os.chdir(dest_dir)
        yield dest_dir
    finally:
        os.chdir(current_cwd)


def _set_file_encoding_utf8(filename):
    """set a encoding header as suggested in PEP-0263. This
    is not entirely correct because we don't know the encoding of the
    given file but it's at least a chance to get metadata from the setup.py"""
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write("# -*- coding: utf-8 -*-\n" + content)


def _setup_py_run_from_dir(root_dir, py_interpreter):
    """run the extractmeta command via the setup.py in the given root_dir.
    the output of extractmeta is json and is stored in a tempfile
    which is then read in and returned as data"""
    data = {}
    with _enter_single_subdir(root_dir) as single_subdir:
        if not os.path.exists("setup.py"):
            raise Exception("'setup.py' does not exist in '%s'" % (
                single_subdir))
        # generate a temporary json file which contains the metadata
        output_json = tempfile.NamedTemporaryFile()
        cmd = "%s setup.py -q --command-packages metaextract " \
              "metaextract -o %s " % (py_interpreter, output_json.name)
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError:
            # try again with a encoding in setup.py
            _set_file_encoding_utf8("setup.py")
            subprocess.check_output(cmd, shell=True)

        # read json file and return data
        with open(output_json.name, "r") as f:
            data = json.loads(f.read())

        # sort some of the keys if the dict values are lists
        for key in ['data_files', 'entry_points', 'extras_require',
                    'install_requires', 'setup_requires', 'scripts',
                    'tests_require', 'tests_suite']:
            if key in data['data'] and isinstance(data['data'][key], list):
                data['data'][key] = sorted(data['data'][key])
    return data


###############################################################################
def from_archive(archive_filename, py_interpreter=sys.executable):
    """extract metadata from a given sdist archive file

    :param archive_filename: a sdist archive file
    :param py_interpreter: The full path to the used python interpreter

    :returns: a json blob with metadata
"""
    with _extract_to_tempdir(archive_filename) as root_dir:
        data = _setup_py_run_from_dir(root_dir, py_interpreter)
    return data
