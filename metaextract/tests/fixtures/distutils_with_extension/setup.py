from distutils.core import setup, Extension

module1 = Extension(
    'demo1',
    sources=['demo.c']
)

module2 = Extension(
    'demo2',
    define_macros=[('MAJOR_VERSION', '1'),
                   ('MINOR_VERSION', '0')],
    include_dirs=['/usr/local/include'],
    libraries=['tcl86'],
    library_dirs=['/usr/local/lib'],
    sources=['demo2.c']
)

setup(
    name='pkg',
    version='1.0',
    description='demo pkg',
    ext_modules=[module1, module2]
)
