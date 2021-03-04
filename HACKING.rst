Hacking on OpenMap
===================

Here are some guidelines for hacking on OpenMap.


Using a Development Checkout
----------------------------
You will have to create a development environment to hack OpenMap, using a
OpenMap checkout. We use `tox` to run tests, run test coverage, and build
documentation.

tox docs: https: // tox.readthedocs.io / en / latest/

tox on PyPI: https: // pypi.org / project / tox/

- Create a new directory somewhere and `cd` to it:

.. code-block: : bash

     $ mkdir ~ / hack - on - OpenMap
     $ cd ~ / hack - on - OpenMap

- Check out a read - only copy of the OPenMap source:

    + Clone it: ``git clone https: // github.com / CLEANit / OpenMAP``
    + if necessary Create virtualenv and activate it:

    .. code-block: : bash

         $ virtualenv venv - -python = python3
        # activate virtualenv (you need to do that every time)
         $ source venv / bin / activate

    + Install(dev) dependencies: ``pip install - dependencies - dev``.
    + Finally, “install” the pakage: ``pip install - e .``

Alternatively, create a writeable fork on GitHub and clone it to implement your changes(see `[How to Contribute] < https: // github.com / CLEANit / OpenMAP / blob / master / docs / source / contributing.rst >`_)


- Make sure that `tox` is installed, either in your path, or locally. Examples
  below assume that `tox` was installed with:

.. code-block: : bash

     $ pip3 install - -user tox
    # $ export TOX=$(python3 -c 'import site; print(site.USER_BASE + "/bin")')/tox


Before you file a pull request, we recommend that you run your proposed
change through `tox`. `tox` will fully validate that all tests work, all
supported formats of documentation will build and their doctests pass, and
test coverage is 100 %, across all supported versions of Python. `tox` will
only run builds for Python versions that you have installed and made
available to `tox`. Setting up that environment is outside the scope of this
document.


Coding Style
------------

- OpenMap uses Black(https: // pypi.org / project / black /) and isort(https: // pypi.org / project / isort /) for code formatting style.
  To run formatters:

.. code-block: : bash

    $ tox - e format


Running Tests
-------------

- The `tox.ini` uses `pytest` and `coverage`. As such `tox` may be used
  to run groups of tests or only a specific version of Python. For example, the
  following command will run tests on the same version of Python that `tox` is
  installed with:

.. code-block: : bash

    $ tox - e py


  To run `tox` for Python 3.6 explicitly, you may use:

.. code-block:: bash

    $ tox -e py36


- To run individual tests (i.e., during development), you can use `pytest`
  syntax as follows, where `$VENV` is an environment variable set to the path
  to your virtual environment:

    + run a single test

    .. code-block:: bash

        $ tox -e py -- tests/test_httpexceptions.py::TestHTTPMethodNotAllowed::test_it_with_default_body_tmpl

    + run all tests in a class

    .. code-block:: bash

        $ tox -e py -- tests/test_httpexceptions.py::TestHTTPMethodNotAllowed

- For more information on how to use pytest, please refer to the pytest
  documentation for selecting tests:
  https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests



Test Coverage
-------------

- The codebase *must* have 100% test statement coverage after each commit. You
  can test coverage via `tox -e py36`.


Documentation Coverage and Building HTML Documentation
------------------------------------------------------

If you fix a bug, and the bug requires an API or behavior modification, all
documentation in this package which references that API or behavior must be
changed to reflect the bug fix, ideally in the same commit that fixes the bug
or adds the feature. To build and review docs, use the following steps.


1. In the main OpenMap checkout directory, run `tox -e docs`:

    .. code-block:: bash

     $ tox -e docs

2. Open the `.tox/docs/html/index.html` file to see the resulting HTML
   rendering.


Change Log
----------

- Feature additions and bugfixes must be added to the `CHANGES.rst`
  file in the prevailing style. Changelog entries should be long and
  descriptive, not cryptic. Other developers should be able to know
  what your changelog entry means.

