import setuptools

setuptools.setup(
    name='testpkg',
    version='1.2.3',
    author="的å",
    license='Apache-2.0',
    description='desc',
    long_description='long desc',
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
    python_requires=">=2.6,!=3.0.*,!=3.1.*,!=3.2.*",
    classifiers=[
        'Intended Audience :: Developers',
    ],
    entry_points={
        'console_scripts': [
            'testpkgp1=testpkg:main'
        ]
    },
)
