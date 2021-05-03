.. _install:

==================
Installing OpenMap
==================


Normal installation
===================

To install the latest version of OpenMAP:


- Install poetry (https://github.com/python-poetry/poetry)

    + osx / linux / bashonwindows install instructions
        .. sourcecode:: bash

            $ pip install poetry

    + windows powershell install instructions
        .. sourcecode:: bash

            $ pip install poetry

- Once Poetry is installed you can execute the following:

.. sourcecode:: bash

    $ poetry --version

    $ poetry self update

- Clone the repo

.. sourcecode:: bash

    $ git clone  https://github.com/CLEANit/OpenMAP

    $ cd openmap

- install the packages
.. sourcecode:: bash

    $openmap peotry install

    $openmap peotry check

    $openmap poetry run pytest

    $openmap poetry build


+ Listing the current configuration

    .. sourcecode:: bash

        $openmap poetry config --list

    which will give you something similar to this

    .. sourcecode:: bash

        cache-dir = "/path/to/cache/directory"
        virtualenvs.create = true
        virtualenvs.in-project = null
        virtualenvs.path = "{cache-dir}/virtualenvs"  # /path/to/cache/directory/virtualenvs


Installation for contributors
=============================
- Install poetry (https://github.com/python-poetry/poetry)

    + osx / linux / bashonwindows install instructions
        .. sourcecode:: bash

            $ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
            or
            $ pip install poetry

    + windows powershell install instructions
        .. sourcecode:: bash

            $ (Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py -UseBasicParsing).Content | python -
            or
            $ pip install poetry

- Once Poetry is installed you can execute the following:

.. sourcecode:: bash

    $ poetry --version

    $ poetry self update

- Clone the repo

.. sourcecode:: bash

    $ git clone  https://github.com/CLEANit/OpenMAP

    $ cd openmap

- install the packages
.. sourcecode:: bash

    $openmap peotry install

    $openmap peotry check

    $openmap poetry run pytest

    $openmap poetry build


+ Listing the current configuration

    .. sourcecode:: bash

        $openmap poetry config --list

    which will give you something similar to this

    .. sourcecode:: bash

        cache-dir = "/path/to/cache/directory"
        virtualenvs.create = true
        virtualenvs.in-project = null
        virtualenvs.path = "{cache-dir}/virtualenvs"  # /path/to/cache/directory/virtualenvs

Pre-commit
----------
- Every time you clone a project using pre-commit running pre-commit install should always be the first thing you do.

.. code-block:: bash

    $ pre-commit install

- After making all your change run pre-commit before  committing and pushing

.. code-block:: bash

    $ tox pre-commit

Coding Style
------------

- OpenMap uses Black (https://pypi.org/project/black/) and isort (https://pypi.org/project/isort/) for code formatting style.
  To run formatters:

.. code-block:: bash

    $ tox -e format


- OpenMap also use doc8 (https://pypi.org/project/doc8/) to autoformat .rst file

.. code-block:: bash

    $ tox -e doc8

Running Tests
-------------

- The `tox.ini` uses `pytest` and `coverage`. As such `tox` may be used
  to run groups of tests or only a specific version of Python. For example, the
  following command will run tests on the same version of Python that `tox` is
  installed with:

.. code-block:: bash

    $ tox -e py


 To run `tox` for Python 3.6 explicitly, you may use:

.. code-block:: bash

    $ tox -e py36


- To run individual tests (i.e., during development), you can use `pytest`
  syntax as follows, where `$VENV` is an environment variable set to the path
  to your virtual environment:

    + run a single test

    .. code-block:: bash

        $ tox -e py -- tests/test_xx.py

    + run all tests in a class

    .. code-block:: bash

        $ tox -e py -- tests/

- For more information on how to use pytest, please refer to the pytest
  documentation for selecting tests:
  https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests



Test Coverage
-------------

- The codebase *must* have 100% test statement coverage after each commit. You
  can test coverage via

 .. code-block:: bash

        $ tox -e py36



Documentation Coverage and Building HTML Documentation
------------------------------------------------------

If you fix a bug, and the bug requires an API or behavior modification, all
documentation in this package which references that API or behavior must be
changed to reflect the bug fix, ideally in the same commit that fixes the bug
or adds the feature. To build and review docs, use the following steps.


1. In the main OpenMap checkout directory, run `tox -e docs`:

    .. code-block:: bash

     $ tox -e docs

2. Open the `docs/build/html/index.html` file to see the resulting HTML
   rendering.





Change Log
----------

- Feature additions and bugfixes must be added to the `CHANGES.rst`
  file in the prevailing style. Changelog entries should be long and
  descriptive, not cryptic. Other developers should be able to know
  what your changelog entry means.



