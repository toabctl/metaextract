import setuptools

setuptools.setup(
    name='testpkg',
    author="的å",
    install_requires=['foo', 'bar'],
    extras_require={
        'extra1': 'pkg1', 'extra2': ['pkg2', 'pkg3']
    },
)
