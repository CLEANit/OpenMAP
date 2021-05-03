=====================
For the contribution
=====================

OpenMap uses poetry  https://github.com/python-poetry/poetry for Dependency Management

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
    $my_package poetry run  my_package pytest or tox -e pytest
    $my_package poetry run ... #coverage run --source=my_package -m unittest discover -b

5- Building HTML Documentation

.. sourcecode:: bash

    $ cd  docs
    $my_package/docs  poetry run sphinx-apidoc  -f -o source/ ../openmap
    $my_package  poetry run doc8 or tox -e doc8

6 - Commit your changes and push

The command **$poetry run pre-commit install$ has created**  ".git/hooks" to  store all the
the hooks edited in the file **.pre-commit-config.yaml**. So  **$git commit -m ""**  will fully validate that all tests work, all
supported formats of documentation will build and their doctests pass, and
test coverage is 100 %, across all supported versions of Python.

.. sourcecode:: bash

    $my_package  git commit -m ""
    $my_package git push

# before_deploy:
# - poetry config repositories.mypypi http://mypypi.example.com/simple
# - poetry config http-basic.mypypi $MYPYPI_USER $MYPYPI_PASS
# - poetry build -f sdist
# deploy:
#   provider: script
#   script: poetry publish -r mypypi
#   skip_cleanup: true
#   on:
#     tags: true


Getting Started with Sphinx
----------------------------

OpenMap uses   Sphinx (https://docs.readthedocs.io/en/stable/intro/getting-started-with-sphinx.html) to generate the HTMLK documentation
This is just for information  please do not run the following command. The docs directory already exist


- Install Sphinx:

.. code-block:: bash

    $ pip install sphinx

- Create a directory inside your project to hold your docs:

.. code-block:: bash

    $ cd /path/to/project
    $ mkdir docs

- Edit the module.rst. Add the name of the module if you have created new module

.. code-block:: bash

    $ cd  docs
    $ vi module.rst

- Run sphinx-quickstart in there:

.. code-block:: bash

    $ cd  docs
    $ sphinx-quickstart

This quick start will walk you through creating the basic configuration;
in most cases, you can just accept the defaults. When it’s done, you’ll have an index.rst,
a conf.py and some other files. Add these to revision control.

Now, edit your index.rst and add some information about your project. Include as much detail as you like

- Run sphinx-apidoc

sphinx-apidoc is a tool for automatic generation of Sphinx sources that, using the autodoc extension,
document a whole package in the
style of other automatic API documentation tools.

.. code-block:: bash

    $ cd  docs
    $  sphinx-apidoc  -f -o source/ ../