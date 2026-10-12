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

import io
import os
import pytest
import shutil
import subprocess
import sys
import tarfile

import setuptools

from metaextract import cmds as meta_cmds
from metaextract import utils as meta_utils


base_dir = os.path.dirname(__file__)
fixtures_base_dir = os.path.join(base_dir, "fixtures")

# setuptools >= 70 removed the tests_require attribute from Distribution
_HAS_TESTS_REQUIRE = hasattr(
    setuptools.Distribution({}), 'tests_require'
)
# setuptools >= 72 removed the test command and test_suite
_HAS_TEST_SUITE = hasattr(setuptools.Distribution({}), 'test_suite')


# keys from the distribution metadata which are always available
_METADATA_KEYS = {
    'author', 'author_email', 'classifiers', 'contact', 'contact_email',
    'description', 'download_url', 'fullname', 'has_ext_modules',
    'keywords', 'license', 'long_description', 'maintainer',
    'maintainer_email', 'name', 'url', 'version'}


def _make_tar(tmpdir, members):
    """create a tarball with the given name -> content members"""
    tarfile_name = tmpdir.join("pkg.tar.gz").strpath
    with tarfile.open(tarfile_name, "w:gz") as tar:
        for name, content in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return tarfile_name


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
        assert "foobar" in str(e_info.value)

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
        assert tmpdir.strpath in str(e_info.value)

    @pytest.mark.parametrize(
        "fixture_name,expected_data,expected_tests_require", [
            (
                "setuptools_simple", {
                    'entry_points': None,
                    'extras_require': {'extra1': ['pkg1']},
                    'install_requires': ['bar', 'foo'],
                    'python_requires': None,
                    'setup_requires': [],
                    'has_ext_modules': False,
                    'scripts': None, 'data_files': None},
                None
            ),
            (
                "setuptools_simple_unicode", {
                    'entry_points': None, 'extras_require': {
                        'extra1': ['pkg1'], 'extra2': ['pkg2', 'pkg3']},
                    'install_requires': ['bar', 'foo'],
                    'python_requires': None,
                    'setup_requires': [],
                    'has_ext_modules': False,
                    'scripts': None, 'data_files': None},
                None
            ),
            (
                "setuptools_simple_unicode_and_header", {
                    'entry_points': None, 'extras_require': {},
                    'install_requires': ['bar', 'foo'],
                    'python_requires': None,
                    'setup_requires': [],
                    'has_ext_modules': False,
                    'scripts': None, 'data_files': None},
                None
            ),
            (
                "setuptools_full", {
                    'install_requires': ['bar', 'foo'],
                    'setup_requires': [],
                    'python_requires':
                        '>=2.6,!=3.0.*,!=3.1.*,!=3.2.*',
                    'has_ext_modules': False,
                    'scripts': ['scripts/testpkg'],
                    'data_files': [
                        ['man/man1', ['doc/testpkg.1']],
                        ['share/doc/testpgk',
                         ['AUTHORS', 'LICENSE', 'README.rst']],
                        ['share/doc/testpkg/html',
                         ['doc/testpkg.html']],
                    ], 'entry_points': {
                        'console_scripts': [
                            'testpkgp1=testpkg:main']
                    },
                    'extras_require': {
                        'extra1': ['ex11', 'ex12'],
                        'extra2': ['ex21>=3.4',
                                   'ex22!=0.15.0,>=0.11.0']
                    },
                    'version': '1.2.3',
                    'name': 'testpkg',
                    'fullname': 'testpkg-1.2.3',
                    'description': 'desc',
                    'long_description': 'long desc',
                    'classifiers': [
                        'Intended Audience :: Developers'],
                    'license': 'Apache-2.0',
                },
                ['testpkg1']
            ),
            (
                "distutils_simple",
                {'data_files': None, 'has_ext_modules': False,
                 'scripts': None, 'version': '1.0'},
                None
            ),
            (
                "distutils_with_extension",
                {'data_files': None, 'has_ext_modules': True,
                 'scripts': None},
                None
            ),
            (
                "pbr_simple",
                {'entry_points': {
                    'console_scripts': ['entry2 = pkg1:main']},
                 'extras_require': {}, 'install_requires': [],
                 'python_requires': None,
                 'setup_requires': ['pbr>=1.0'],
                 'has_ext_modules': False,
                 'scripts': None, 'data_files': None,
                 'version': '1'},
                None
            ),
            (
                "pyproject",
                {
                    'install_requires': ['bar', 'foo'],
                    'setup_requires': [],
                    'python_requires':
                        '!=3.0.*,!=3.1.*,!=3.2.*,>=2.6',
                    'entry_points': {
                        'console_scripts': [
                            'testpkgp1 = testpkg:main']
                    },
                    'extras_require': {
                        'extra1': ['ex11', 'ex12'],
                        'extra2': ['ex21>=3.4',
                                   'ex22!=0.15.0,>=0.11.0']
                    },
                    'version': '1.2.3',
                    'name': 'testpkg',
                    'fullname': 'testpkg-1.2.3',
                    'description': 'desc',
                    'long_description': 'long desc\n',
                    'classifiers': [
                        'Intended Audience :: Developers'],
                    'license': 'Apache-2.0',
                },
                None
            ),
        ])
    def test_run_setup_py_from_dir(self, tmpdir, monkeypatch,
                                   fixture_name, expected_data,
                                   expected_tests_require):
        # the given fixture name is the directory name in the tests/fixtures
        # dir. copy that fixtures dir to a temp dir and run _setup_py_from_dir
        # PBR_VERSION is needed for the PBR tests because the fixture are not
        # containing a git repo
        monkeypatch.setenv("PBR_VERSION", "1")
        fixture_dir = os.path.join(fixtures_base_dir, fixture_name)
        dest_dir = os.path.join(tmpdir.strpath, fixture_name)
        shutil.copytree(fixture_dir, dest_dir)
        data = meta_utils._setup_py_run_from_dir(dest_dir, sys.executable)
        for expected_key, expected_val in expected_data.items():
            assert expected_key in data['data']
            assert data['data'][expected_key] == expected_val
        assert _METADATA_KEYS <= set(data['data'])
        if fixture_name == "setuptools_full" and _HAS_TEST_SUITE:
            assert data['data']['test_suite'] == 'pkgtestsuite'
        # setuptools >= 70 removed tests_require from Distribution
        if _HAS_TESTS_REQUIRE:
            assert data['data'].get('tests_require') == \
                expected_tests_require

    def test_from_archive_mixed_data_files(self, tmpdir):
        tar_name = _make_tar(tmpdir, {
            "pkg/setup.py": b"""import setuptools
setuptools.setup(name='p', data_files=['b.txt', ('share', ['a.txt'])])
"""})
        data = meta_utils.from_archive(tar_name)
        assert data["data"]["data_files"] == [['share', ['a.txt']], 'b.txt']

    def test_from_archive_interpreter_with_space(self, tmpdir, tararchive):
        tar_name, _ = tararchive
        bindir = tmpdir.mkdir("dir with space")
        python = bindir.join("python")
        python.write('#!/bin/sh\nexec "%s" "$@"\n' % sys.executable)
        python.chmod(0o755)
        python = python.strpath
        data = meta_utils.from_archive(tar_name, python)
        assert data["data"]["install_requires"] == ['bar', 'foo']

    @pytest.mark.parametrize("data_filter", [True, False])
    @pytest.mark.parametrize("absolute", [True, False])
    def test__extract_to_tempdir_unsafe_tar(self, tmpdir, monkeypatch,
                                            data_filter, absolute):
        if not data_filter:
            monkeypatch.delattr(tarfile, "data_filter", raising=False)
        elif not hasattr(tarfile, "data_filter"):
            pytest.skip("tarfile extraction filters not available")
        escaped = tmpdir.join("escaped.txt").strpath
        name = escaped if absolute else "../../../../../../../.." + escaped
        tar_name = _make_tar(tmpdir, {name: b"escaped"})
        try:
            with meta_utils._extract_to_tempdir(tar_name):
                pass
        except Exception:
            pass
        assert not os.path.exists(escaped)

    def test__setup_py_run_from_dir_failure(self, tmpdir):
        tmpdir.join("setup.py").write("""
open('runs', 'a').write('run')
raise SystemExit('setup.py failed')
""")
        with pytest.raises(subprocess.CalledProcessError) as e_info:
            meta_utils._setup_py_run_from_dir(tmpdir.strpath, sys.executable)
        assert b"setup.py failed" in e_info.value.output
        # no retry and no encoding header for other failures
        assert tmpdir.join("runs").read() == "run"
        assert tmpdir.join("setup.py").read().startswith("\nopen(")

    def test__setup_py_run_from_dir_encoding_retry(self, tmpdir, monkeypatch):
        shutil.copytree(os.path.join(fixtures_base_dir, "setuptools_simple"),
                        tmpdir.join("pkg").strpath)
        check_output = subprocess.check_output
        calls = []

        def fake_check_output(cmd, **kwargs):
            calls.append(cmd)
            if len(calls) == 1:
                raise subprocess.CalledProcessError(
                    1, cmd, output=b"SyntaxError: Non-ASCII character "
                    b"'\\xc3' in file setup.py, but no encoding declared")
            return check_output(cmd, **kwargs)

        monkeypatch.setattr(subprocess, "check_output", fake_check_output)
        data = meta_utils._setup_py_run_from_dir(tmpdir.join("pkg").strpath,
                                                 sys.executable)
        assert len(calls) == 2
        assert data["data"]["install_requires"] == ['bar', 'foo']
        assert tmpdir.join("pkg", "setup.py").read().startswith(
            "# -*- coding: utf-8 -*-\n")


class TestCmds(object):
    def test_main_python_option(self, monkeypatch, capsys):
        calls = []

        def fake_from_archive(archive, py_interpreter):
            calls.append((archive, py_interpreter))
            return {}

        monkeypatch.setattr(meta_utils, "from_archive", fake_from_archive)
        monkeypatch.setattr(sys, "argv", [
            "metaextract", "--python", "/usr/bin/python2", "pkg.tar.gz"])
        meta_cmds.main()
        assert calls == [("pkg.tar.gz", "/usr/bin/python2")]

    def test_main_python_default(self, monkeypatch, capsys):
        calls = []
        monkeypatch.setattr(meta_utils, "from_archive",
                            lambda *args: calls.append(args) or {})
        monkeypatch.setattr(sys, "argv", ["metaextract", "pkg.tar.gz"])
        meta_cmds.main()
        assert calls == [("pkg.tar.gz", sys.executable)]

    def test_main_setup_py_failure(self, tmpdir, monkeypatch, capsys):
        tar_name = _make_tar(tmpdir, {
            "pkg/setup.py": b"raise SystemExit('setup.py failed')\n"})
        monkeypatch.setattr(sys, "argv", ["metaextract", tar_name])
        with pytest.raises(SystemExit) as e_info:
            meta_cmds.main()
        assert tar_name in str(e_info.value)
        assert "setup.py failed" in capsys.readouterr().err
