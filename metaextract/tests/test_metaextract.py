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

import os
import pytest
import shutil
import tarfile

from metaextract import utils as meta_utils


@pytest.fixture()
def tararchive(tmpdir):
    """create a tarfile in a temp dir"""
    tmpdir = tmpdir.mkdir("tar")
    tarfile_name = tmpdir.join("file.tar").strpath
    tar = tarfile.open(tarfile_name, "w:gz")
    files = ["file1", "file2", "file3"]
    for name in files:
        new_file = tmpdir.join(name)
        new_file.write(name)
        tar.add(new_file.strpath, arcname=name)
    # also add a setup.py file
    setup_py_name = tmpdir.join("setup.py")
    setup_py_name.write("""import setuptools
setuptools.setup(
    name='testpkg',
    install_requires=['foo', 'bar'],
)
""")
    tar.add(setup_py_name.strpath, arcname="setup.py")
    tar.close()
    return tarfile_name, files + ["setup.py"]


@pytest.fixture()
def ziparchive(tmpdir):
    """create a zip archive in a temp dir"""
    tmpdir = tmpdir.mkdir("zip")
    zip_data = os.path.join(tmpdir.strpath, "data")
    os.mkdir(zip_data)
    zipfile_name = tmpdir.join("file").strpath
    files = ["file1", "file2", "file3"]
    for name in files:
        new_file = os.path.join(zip_data, name)
        with open(new_file, "a+") as f:
            f.write(name)
    shutil.make_archive(zipfile_name, "zip", root_dir=zip_data)
    return zipfile_name + ".zip", files


class TestMetaExtract(object):
    def test__extract_to_tempdir_no_file(self):
        with pytest.raises(Exception) as e_info:
            with meta_utils._extract_to_tempdir("foobar"):
                pass
        assert "foobar" in str(e_info)

    def test__extract_to_tempdir_tar_archive(self, tararchive):
        tarball_name, tarball_files = tararchive
        with meta_utils._extract_to_tempdir(tarball_name):
            assert sorted(os.listdir(".")) == tarball_files

    def test__extract_to_tempdir_zip_archive(self, ziparchive):
        zip_name, zip_files = ziparchive
        with meta_utils._extract_to_tempdir(zip_name):
            assert sorted(os.listdir(".")) == zip_files

    def test__enter_single_subdir_0_dir(self, tmpdir):
        with meta_utils._enter_single_subdir(tmpdir.strpath) as dest_dir:
            assert dest_dir == tmpdir.strpath

    def test__enter_single_subdir_1_dir(self, tmpdir):
        d1 = os.path.join(tmpdir.strpath, "dir1")
        os.mkdir(d1)
        with meta_utils._enter_single_subdir(tmpdir.strpath) as dest_dir:
            assert dest_dir == d1

    def test__enter_single_subdir_2_dirs(self, tmpdir):
        d1 = os.path.join(tmpdir.strpath, "dir1")
        d2 = os.path.join(tmpdir.strpath, "dir2")
        os.mkdir(d1)
        os.mkdir(d2)
        with meta_utils._enter_single_subdir(tmpdir.strpath) as dest_dir:
            assert dest_dir == tmpdir.strpath

    def test__set_file_encoding_utf8(self, tmpdir):
        testfile = tmpdir.mkdir("encoding").join("setup.py")
        firstline = "the first line of the file"
        with open(testfile.strpath, "a") as f:
            f.write(firstline)
        meta_utils._set_file_encoding_utf8(testfile.strpath)
        with open(testfile.strpath, 'r') as f:
            assert f.read() == "# -*- coding: utf-8 -*-\n" + firstline

    def test_from_archive(self, tararchive):
        tar_name, tar_files = tararchive
        data = meta_utils.from_archive(tar_name)
        assert data["data"]["install_requires"] == ['foo', 'bar']


class TestSetupPyRunFromDir(object):
    """all these tests are running the function _setup_py_run_from_dir()"""
    def test_no_setup_py(self, tmpdir):
        with pytest.raises(Exception) as e_info:
            meta_utils._setup_py_run_from_dir(tmpdir.strpath)
        assert tmpdir.strpath in str(e_info)

    def test_simple(self, tmpdir):
        setuppy = tmpdir.mkdir("setuppy").join("setup.py")
        with open(setuppy.strpath, "a") as f:
            f.write("""import setuptools
setuptools.setup(
    name='testpkg',
    install_requires=['foo', 'bar'],
)
""")
        data = meta_utils._setup_py_run_from_dir(tmpdir.strpath)
        assert data["data"]["install_requires"] == ['foo', 'bar']

    def test_with_unicode(self, tmpdir):
        setuppy = tmpdir.mkdir("setuppy").join("setup.py")
        with open(setuppy.strpath, "a") as f:
            f.write("""import setuptools
setuptools.setup(
    name='testpkg',
    author="的å",
    install_requires=['foo', 'bar'],
)
""")
        data = meta_utils._setup_py_run_from_dir(tmpdir.strpath)
        assert data["data"]["install_requires"] == ['foo', 'bar']

    def test_with_unicode_and_header(self, tmpdir):
        setuppy = tmpdir.mkdir("setuppy").join("setup.py")
        with open(setuppy.strpath, "a") as f:
            f.write("""# -*- coding: utf8 -*-
import setuptools
setuptools.setup(
    name='testpkg',
    author="的å",
    install_requires=['foo', 'bar'],
)
""")
        data = meta_utils._setup_py_run_from_dir(tmpdir.strpath)
        assert data["data"]["install_requires"] == ['foo', 'bar']
