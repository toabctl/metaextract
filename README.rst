metaextract - get metadata for python modules
=============================================

.. image:: https://travis-ci.org/toabctl/metaextract.png?branch=master
        :target: https://travis-ci.org/toabctl/metaextract


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
``extras_require``` and friends extracted from the given archive file.

If you already have some source code available (i.e. a git checkout) for some
project you can also run the ``setup.py`` file with the ``metaextract``
distutils command:

.. code-block:: bash

   $ python setup.py --command-packages=metaextract metaextract

This will print the metadata as json. If you want to write the data to a file, do:

.. code-block:: bash

   $ python setup.py --command-packages=metaextract metaextract -o output-file


Hacking and contributing
------------------------
Fork `the repository`_ on Github to start making your changes to the **master**
branch (or branch off of it). Don't forget to write a test for fixed issues or
implemented features whenever appropriate. You can invoke the testsuite from
the repository root directory via `tox`_:

.. code-block:: bash

    $ tox


.. _`Python Package Index`: https://pypi.python.org/
.. _`the repository`: https://github.com/toabctl/metaextract
.. _`tox`: http://testrun.org/tox
