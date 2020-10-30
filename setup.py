from setuptools import setup
from pip.download import PipSession
from pip.req import parse_requirements

import openmaps

pkgs = []
dependency_links = []
session = PipSession()
for pkg in parse_requirements('requirements.txt', session=session):
    if pkg.req:
        pkgs.append(str(pkg.req))
        if pkg.link and pkg.link.url:
            dependency_links.append(str(pkg.link.url))

setup(
    name='openmaps',
    packages=['openmaps', 'openmaps.core', 'openmaps.computing', 'openmaps.aws'],
    version=openmaps.__version__,
    author=openmaps.__author__,
    author_email=openmaps.__email__,
    description=openmaps.__doc__,
    classifiers=[
        'Environment :: Scientific',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
    install_requires=pkgs,
    dependency_links=dependency_links,
    python_requires='>=3',
    test_suite='tests',
    entry_points={
        'console_scripts': openmaps.make_console_scripts()
    },
)
