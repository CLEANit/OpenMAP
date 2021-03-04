import os
import re

from setuptools import find_packages, setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type('')
    with open(filename, mode='r', encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+`~?(.*?)`'), text_type(r'``\1``'), fd.read())


def readfile(name):
    with open(name) as f:
        return f.read()


README = readfile('README.rst')
CHANGES = readfile('CHANGES.rst')

VERSION = '1.0'

requirements_txt = os.path.join(os.path.dirname(__file__), 'requirements.txt')

with open(requirements_txt, encoding='utf-8') as fin:
    requires = [line.strip() for line in fin if line and line.strip()
                and not line.strip().startswith('#')]

setup(
    name='openmap',
    url='https://github.com/CLEANit/OpenMAP',
    version='1.0',
    author='Conrard TETSASSI',
    author_email='giresse.feugmo@gmail.com',
    description='OpenMAP is an Automated Material Acceleration Platforms',
    long_description=README + '\n\n' + CHANGES,
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=requires,
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha' 'Environment :: Scientific',
        'Operating System :: Os Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.yml files found in the "data" subdirectory
        # of the "tools" package, also:
        'hea': ['*.yml'],
    },
    # ...but exclude README.txt from all packages
    # exclude_package_data={"": ["README.txt"]},
)
