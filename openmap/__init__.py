# openmap/__init__.py

__version__ = '1.0'
__author__ = 'Conrard TETSASSI'
__maintainer__ = 'Conrard TETSASSI'
__email__ = 'giresse.feugmo@gmail.com'
__status__ = 'Developments'

"""
openmap is a package for materials acceleration combining AI and Molecular modelling
"""
import os
import stat
import sys
import configparser
from sys import stdout
from openmap.computing.log import logger

with open(os.path.join(os.path.dirname(__file__), "VERSION.txt")) as fr:
    __version__ = fr.read().strip()

VERSION = __version__

INSTALL_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path = [os.path.join(INSTALL_PATH, "openmap")] + sys.path

LOG_PATH = os.path.join(INSTALL_PATH, "logs")

config = configparser.ConfigParser()
config.read(os.path.join(INSTALL_PATH, "configuration", "site.cfg"))





try:
    import ase

    FOUND_ASE = True
except ImportError:
    FOUND_ASE = False
    logger.warning("Failed to import ASE")

# try:
#     import pymatgen
#
#     FOUND_PMG = True
# except ImportError:
#     FOUND_PMG = False
#     logger.warning("Failed to import pymatgen")
#
# try:
#     import tensorflow
#
#     FOUND_TF = True
# except ImportError:
#     FOUND_TF = False
#     logger.warning("Failed to import tensorflow")



