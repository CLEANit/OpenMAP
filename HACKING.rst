Hacking on OpenMap
===================

Here are some guidelines for hacking on OpenMap.


Using a Development Checkout
----------------------------
You will have to create a development environment to hack OpenMap, using a
OpenMap checkout. We use  `Poetry <https://python-poetry.org/docs/basic-usage/>`_  to run tests, run test coverage, and build
documentation.

1- create a writeable fork on GitHub and clone it to implement your changes

2- before_install:

.. sourcecode:: bash

    $pip install poetry

3-  install

.. sourcecode:: bash

    $cd my_package
    $my_package poetry install

4-  script:

.. sourcecode:: bash

    $my_package poetry run pre-commit install
    $my_package poetry run pre-commit
    $my_package poetry run  my_package pytest
    $my_package poetry run ... #coverage run --source=my_package -m unittest discover -b

5- Building HTML Documentation

.. sourcecode:: bash

    $ cd  docs
    $my_package/docs  poetry run sphinx-apidoc  -f -o source/ ../openmap
    $my_package  poetry run doc8

6 - Commit your changes and push

The command **$poetry run pre-commit install$ has created**  ".git/hooks" to  store all the
the hooks edited in the file **.pre-commit-config.yaml**. So  **$git commit -m ""**  will fully validate that all tests work, all
supported formats of documentation will build and their doctests pass, and
test coverage is 100 %, across all supported versions of Python.

.. sourcecode:: bash

    $my_package  git commit -m ""
        Requirements.............................................................Passed
        isort....................................................................Passed
        Black....................................................................Passed
        MyPy.....................................................................Passed
        Pylint...................................................................Passed
        [master 8e9e6e6]
        1 file changed, 1 insertion(+), 1 deletion(-)
    $my_package git push

Change Log
----------

- Feature additions and bugfixes must be added to the `CHANGES.rst`
  file in the prevailing style. Changelog entries should be long and
  descriptive, not cryptic. Other developers should be able to know
  what your changelog entry means.

