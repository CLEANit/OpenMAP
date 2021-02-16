import io
import os
import re

# import openmap
from setuptools import find_packages, setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type('')
    with open(filename, mode='r', encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+`~?(.*?)`'), text_type(r'``\1``'), fd.read())


requirements_txt = os.path.join(os.path.dirname(__file__), 'requirements.txt')

with open(requirements_txt, encoding='utf-8') as fin:
    requires = [line.strip() for line in fin if line and line.strip() and not line.strip().startswith('#')]

setup(
    name='OpenMAP',
    url='https://github.com/CLEANit/OpenMAP',
    # version=openmap.__version__,
    # author=openmap.__author__,
    # author_email=openmap.__email__,
    # description=openmap.__doc__,
    version='1.0',
    author='Conrard TETSASSI',
    author_email='giresse.feugmo@gmail.com',
    long_description=read('README.rst'),
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
)
