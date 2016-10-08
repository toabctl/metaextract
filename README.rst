metaextract - get metadata for python modules
=============================================

.. image:: https://travis-ci.org/toabctl/metaextract.png?branch=master
           :target: https://travis-ci.org/toabctl/metaextract
.. image:: https://readthedocs.org/projects/metaextract/badge/
           :target: http://metaextract.readthedocs.io/en/latest/
           :alt: Documentation Status

metaextract is a tool to collect metadata about a python module. For example
you may have a sdist tarball from the `Python Package Index`_ and you want to
know it's dependencies. metaextract can collect theses dependencies.
The tool was first developed in `py2pack`_ but is now it's own module to be
useful for others, too.

Documentation
-------------
You can find the documentation on `readthedocs`_.

Hacking and contributing
------------------------
Fork `the repository`_ on Github to start making your changes to the **master**
branch (or branch off of it). Don't forget to write a test for fixed issues or
implemented features whenever appropriate. You can invoke the testsuite from
the repository root directory via `tox`_:

.. code-block:: bash

    $ tox

Bugs
----
If you run into bugs, you can file them in the `issue tracker`_.

.. _`readthedocs`: http://metaextract.readthedocs.io/
.. _`py2pack`: https://pypi.python.org/pypi/py2pack
.. _`issue tracker`: https://github.com/toabctl/metaextract/issues
.. _`Python Package Index`: https://pypi.python.org/
.. _`the repository`: https://github.com/toabctl/metaextract
.. _`tox`: http://testrun.org/tox
