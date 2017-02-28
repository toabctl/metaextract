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
import sys
import tarfile

from metaextract import utils as meta_utils


base_dir = os.path.dirname(__file__)
fixtures_base_dir = os.path.join(base_dir, "fixtures")


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
        current_cwd = os.getcwd()
        with meta_utils._extract_to_tempdir(tarball_name) as tempdir:
            assert sorted(os.listdir(".")) == tarball_files
        # back in the original working dir
        assert current_cwd == os.getcwd()
        # tempdir no longer exists
        assert os.path.exists(tempdir) is False

    def test__extract_to_tempdir_zip_archive(self, ziparchive):
        zip_name, zip_files = ziparchive
        current_cwd = os.getcwd()
        with meta_utils._extract_to_tempdir(zip_name) as tempdir:
            assert sorted(os.listdir(".")) == zip_files
        # back in the original working dir
        assert current_cwd == os.getcwd()
        # tempdir no longer exists
        assert os.path.exists(tempdir) is False

    def test__enter_single_subdir_0_dir(self, tmpdir):
        current_cwd = os.getcwd()
        with meta_utils._enter_single_subdir(tmpdir.strpath) as dest_dir:
            assert dest_dir == tmpdir.strpath
        # back in the original working dir
        assert current_cwd == os.getcwd()

    def test__enter_single_subdir_1_dir(self, tmpdir):
        current_cwd = os.getcwd()
        d1 = os.path.join(tmpdir.strpath, "dir1")
        os.mkdir(d1)
        with meta_utils._enter_single_subdir(tmpdir.strpath) as dest_dir:
            assert dest_dir == d1
        # back in the original working dir
        assert current_cwd == os.getcwd()

    def test__enter_single_subdir_2_dirs(self, tmpdir):
        current_cwd = os.getcwd()
        d1 = os.path.join(tmpdir.strpath, "dir1")
        d2 = os.path.join(tmpdir.strpath, "dir2")
        os.mkdir(d1)
        os.mkdir(d2)
        with meta_utils._enter_single_subdir(tmpdir.strpath) as dest_dir:
            assert dest_dir == tmpdir.strpath
        # back in the original working dir
        assert current_cwd == os.getcwd()

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
        assert data["data"]["install_requires"] == ['bar', 'foo']

    def test_no_setup_py(self, tmpdir):
        with pytest.raises(Exception) as e_info:
            meta_utils._setup_py_run_from_dir(tmpdir.strpath, sys.executable)
        assert tmpdir.strpath in str(e_info)

    @pytest.mark.parametrize("fixture_name,expected_data", [
        (
            "setuptools_simple", {
                'entry_points': None, 'extras_require': {'extra1': 'pkg1'},
                'install_requires': ['bar', 'foo'], 'python_requires': None,
                'setup_requires': None, 'has_ext_modules': None,
                'scripts': None, 'data_files': None, 'tests_require': None}
        ),
        (
            "setuptools_simple_unicode", {
                'entry_points': None, 'extras_require': {
                    'extra1': 'pkg1', 'extra2': ['pkg2', 'pkg3']},
                'install_requires': ['bar', 'foo'], 'python_requires': None,
                'setup_requires': None, 'has_ext_modules': None,
                'scripts': None, 'data_files': None, 'tests_require': None}
        ),
        (
            "setuptools_simple_unicode_and_header", {
                'entry_points': None, 'extras_require': None,
                'install_requires': ['bar', 'foo'], 'python_requires': None,
                'setup_requires': None, 'has_ext_modules': None,
                'scripts': None, 'data_files': None, 'tests_require': None}
        ),
        (
            "setuptools_full", {
                'install_requires': ['bar', 'foo'], 'setup_requires': None,
                'python_requires': '>=2.6,!=3.0.*,!=3.1.*,!=3.2.*',
                'has_ext_modules': None, 'scripts': ['scripts/testpkg'],
                'data_files': [
                    ['man/man1', ['doc/testpkg.1']],
                    ['share/doc/testpgk',
                     ['AUTHORS', 'LICENSE', 'README.rst']],
                    ['share/doc/testpkg/html', ['doc/testpkg.html']],
                ], 'tests_require': ['testpkg1'], 'entry_points':
                {
                    'console_scripts': ['testpkgp1=testpkg:main']
                },
                'extras_require': {
                    'extra1': ['ex11', 'ex12'],
                    'extra2': ['ex21>=3.4', 'ex22>=0.11.0,!=0.15.0']
                }
            }
        ),
        (
            "distutils_simple",
            {'data_files': None, 'has_ext_modules': None, 'scripts': None}
        ),
        (
            "distutils_with_extension",
            {'data_files': None, 'has_ext_modules': True, 'scripts': None}
        ),
        (
            "pbr_simple",
            {'entry_points': {'console_scripts': ['entry2 = pkg1:main']},
             'extras_require': {}, 'install_requires': [],
             'python_requires': None, 'setup_requires': ['pbr>=1.0'],
             'has_ext_modules': None, 'scripts': None, 'data_files': None,
             'tests_require': None}
        ),
    ])
    def test_run_setup_py_from_dir(self, tmpdir, monkeypatch,
                                   fixture_name, expected_data):
        # the given fixture name is the directory name in the tests/fixtures
        # dir. copy that fixtures dir to a temp dir and run _setup_py_from_dir
        # PBR_VERSION is needed for the PBR tests because the fixture are not
        # containing a git repo
        monkeypatch.setenv("PBR_VERSION", "1")
        fixture_dir = os.path.join(fixtures_base_dir, fixture_name)
        dest_dir = os.path.join(tmpdir.strpath, fixture_name)
        shutil.copytree(fixture_dir, dest_dir)
        data = meta_utils._setup_py_run_from_dir(dest_dir, sys.executable)
        assert data['data'] == expected_data
