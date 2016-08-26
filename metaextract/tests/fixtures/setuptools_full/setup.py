import setuptools

setuptools.setup(
    name='testpkg',
    author="的å",
    install_requires=['foo', 'bar'],
    extras_require={
        'extra1': ["ex11", "ex12"],
        'extra2': ["ex21>=3.4", "ex22>=0.11.0,!=0.15.0"],
    },
    scripts=['scripts/testpkg'],
    packages=['testpkg'],
    package_data={'testpkg': ['templates/*', 'spdx_license_map.p']},
    data_files=[('share/doc/testpgk', ['AUTHORS', 'LICENSE', 'README.rst']),
                ('share/doc/testpkg/html', ['doc/testpkg.html']),
                ('man/man1', ['doc/testpkg.1'])],
    tests_require=["testpkg1"],
    test_suite="pkgtestsuite",
    classifiers=[
        'Intended Audience :: Developers',
    ],
    entry_points={
        'console_scripts': [
            'testpkgp1=testpkg:main'
        ]
    },
)
