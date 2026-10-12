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


def _tar_extract_safe(tar, dest_dir):
    """extract all tar members to dest_dir but refuse members which would
    end up outside of dest_dir (CVE-2007-4559)"""
    if hasattr(tarfile, "data_filter"):
        tar.extractall(dest_dir, filter="data")
        return

    # no PEP-706 filters available. Without '..' and absolute paths,
    # neither member names nor link targets can escape dest_dir
    def is_unsafe(path):
        return os.path.isabs(path) or ".." in path.split("/")

    for member in tar.getmembers():
        is_link = member.issym() or member.islnk()
        if is_unsafe(member.name) or member.isdev() or \
                (is_link and is_unsafe(member.linkname)):
            raise Exception("Refusing to extract unsafe tar member '%s'" % (
                member.name))
    tar.extractall(dest_dir)


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
                _tar_extract_safe(f, tempdir)
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
        os.chdir(dest_dir)
        yield dest_dir
    finally:
        os.chdir(current_cwd)


def _set_file_encoding_utf8(filename):
    """set a encoding header as suggested in PEP-0263. This
    is not entirely correct because we don't know the encoding of the
    given file but it's at least a chance to get metadata from the setup.py"""
    with open(filename, 'rb+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(b"# -*- coding: utf-8 -*-\n" + content)


def _sorted(items):
    """sort a list which may contain items of different types (i.e.
    data_files can contain strings and (dir, files) tuples)"""
    try:
        return sorted(items, key=lambda item: (type(item).__name__, item))
    except TypeError:
        return items


def _setup_py_run_from_dir(root_dir, py_interpreter):
    """run the extractmeta command via the setup.py in the given root_dir.
    the output of extractmeta is json and is stored in a tempfile
    which is then read in and returned as data"""
    data = {}
    with _enter_single_subdir(root_dir) as single_subdir:
        if not os.path.exists("setup.py"):
            if not os.path.exists("pyproject.toml"):
                raise Exception("'setup.py' does not exist in '%s'" % (
                    single_subdir))

            # Create it for pyproject.toml without setup.py
            with open("setup.py", "w") as f:
                f.write("from setuptools import setup\nsetup()\n")

        # generate a temporary json file which contains the metadata
        with tempfile.NamedTemporaryFile() as output_json:
            cmd = [py_interpreter, "setup.py", "-q",
                   "--command-packages", "metaextract",
                   "metaextract", "-o", output_json.name]
            try:
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                # python 2 needs an encoding header for non-ascii
                # setup.py files
                if b"no encoding declared" not in (e.output or b""):
                    raise
                _set_file_encoding_utf8("setup.py")
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)

            # read json file and return data
            with open(output_json.name, "r") as f:
                data = json.loads(f.read())

        # sort some of the keys if the dict values are lists
        for key in ['data_files', 'entry_points', 'extras_require',
                    'install_requires', 'setup_requires', 'scripts',
                    'tests_require', 'test_suite']:
            if key in data['data'] and isinstance(data['data'][key], list):
                data['data'][key] = _sorted(data['data'][key])
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
