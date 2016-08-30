import setuptools

setuptools.setup(
    name='testpkg',
    install_requires=['foo', 'bar'],
    extras_require={'extra1': 'pkg1'},
)
