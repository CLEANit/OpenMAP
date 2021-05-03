OpenMap
=======

OpenMap is an Automated Material Acceleration Platforms


Support and Documentation
-------------------------
see docs for documentation, reporting bugs, and getting support.

Authors
-------
OpenMap is made available by  the `National Research Council Canada <https://nrc.canada.ca/en>`_

See  `CONTRIBUTORS.txt <https://github.com/CLEANit/OpenMAP/blob/master/CONTRIBUTORS.txt>`_


Installation
-------------------------

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

Usage
-------------------------

Here is the schematic of the workflow to generate HEAs structures:



Developing and Contributing
---------------------------
See `HACKING.rst <https://github.com/CLEANit/OpenMAP/blob/master/HACKING.rst>`_ and
`contributing.md <https://github.com/CLEANit/OpenMAP/blob/master/contributing.md>`_
for guidelines on running tests, adding features, coding style, and updating
documentation when developing in or contributing to OpenMap.

