.. metaextract documentation master file, created by
   sphinx-quickstart on Sat Oct  8 22:35:02 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to metaextract's documentation!
=======================================

metaextract is a tool to collect metadata about a python module. For example
you may have a sdist tarball from the `Python Package Index`_ and you want to
know it's dependencies. metaextract can collect theses dependencies.
The tool was first developed in `py2pack`_ but is now it's own module to be
useful for others, too.

.. _`py2pack`: https://pypi.python.org/pypi/py2pack
.. _`Python Package Index`: https://pypi.python.org/


Installation
------------
To install metaextract from the `Python Package Index`_, simply:

.. code-block:: bash

    $ pip install metaextract

Usage
-----

To extract the metadata for a python module using setup.py, do:

.. code-block:: bash

   $ metaextract my-archive-file.tar.gz

This will print a json blob to stdout which contains i.e. ``install_requires``,
``extras_require`` and friends extracted from the given archive file.

If you already have some source code available (i.e. a git checkout) for some
project you can also run the ``setup.py`` file with the ``metaextract``
distutils command:

.. code-block:: bash

   $ python setup.py --command-packages=metaextract metaextract

This will print the metadata as json. If you want to write the data to a file, do:

.. code-block:: bash

   $ python setup.py --command-packages=metaextract metaextract -o output-file

API documentation
-----------------

The :mod:`metaextract.utils` Module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: metaextract.utils
    :noindex:
    :members:
    :undoc-members:
    :show-inheritance:


.. toctree::
   :maxdepth: 2


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

