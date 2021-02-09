import io
import os
import re

# import hea
from setuptools import find_packages, setup


# def read(filename):
#     filename = os.path.join(os.path.dirname(__file__), filename)
#     text_type = type('')
#     with open(filename, mode='r', encoding='utf-8') as fd:
#         return re.sub(text_type(r':[a-z]+`~?(.*?)`'), text_type(r'``\1``'), fd.read())
# 
# 
# requirements_txt = os.path.join(os.path.dirname(__file__), 'requirements.txt')
# 
# with open(requirements_txt, encoding='utf-8') as fin:
#     requires = [line.strip() for line in fin if line and line.strip() and not line.strip().startswith('#')]

requirements = [
        'numpy>=1.19.2',
        'sqlalchemy>=1.3.20',
        'pandas>=1.1.3',
        'ase',
        'pymatgen>=2020.10.20',
        'scipy>=1.5.2',
        'h5py>=2.10.0',
        'loguru>=0.5.3',
        'pyyaml>=5.3.1',
        'matminer>=0.6.4',
        'uncertainties>=3.1.',
        'pymysql>=0.10.1',
        'mysql-connector-python>=8.0.22',
        'matplotlib>=3.3.2',
        'seaborn>=0.11.0',
        'paramiko>=2.7.2',
        'scp>=0.13.3',
        'cython>=0.29.21',
        'tensorflow>=2.2.0',
#        'tensorflow-gpu>=2.2.0',
        'pexpect>=4.8.0',
        'nomad-lab==0.9.10',
        ]
setup(
    name='openmap',
    url='https://github.com/CLEANit/OpenMAP',
    version='1.0',
    author=['Conrad Tetsassi', 'Ian Benlolo'],
    author_email='ian.benlolo@uottawa.ca',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=requirements,
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
