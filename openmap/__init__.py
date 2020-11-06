# openmap/__init__.py

"""
openmap is a package for materials acceleration combining AI and Molecular modelling
"""
import os, os.path
import stat
import sys
import configparser
from sys import stdout
from loguru import logger as custom_logger

with open(os.path.join(os.path.dirname(__file__), "VERSION.txt")) as fr:
    __version__ = fr.read().strip()
VERSION = __version__

INSTALL_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path = [os.path.join(INSTALL_PATH, "openmap")] + sys.path

LOG_PATH = os.path.join(INSTALL_PATH, "logs")

config = configparser.ConfigParser()
config.read(os.path.join(INSTALL_PATH, "configuration", "site.cfg"))



def create_logger():
    """Create custom logger."""
    custom_logger.remove()
    custom_logger.add(
        stdout,
        colorize=True,
        level="INFO",
        format="<light-cyan>{time:MM-DD-YYYY HH:mm:ss}</light-cyan> | \
		<light-green>{level}</light-green>: \
		<light-white>{message}</light-white>"
    )
    custom_logger.add(
        'logs/errors.log',
        colorize=True,
        level="ERROR",
        rotation="200 MB",
        catch=True,
        format="<light-cyan>{time:MM-DD-YYYY HH:mm:ss}</light-cyan> | \
		<light-red>{level}</light-red>: \
		<light-white>{message}</light-white>"
    )
    return custom_logger


logger = create_logger()

try:
    import ase

    FOUND_ASE = True
except ImportError:
    FOUND_ASE = False
    logger.warn("Failed to import ASE")

try:
    import pymatgen

    FOUND_PMG = True
except ImportError:
    FOUND_PMG = False
    logger.warn("Failed to import pymatgen")

try:
    import tensorflow

    FOUND_TF = True
except ImportError:
    FOUND_TF = False
    logger.warn("Failed to import tensorflow")



