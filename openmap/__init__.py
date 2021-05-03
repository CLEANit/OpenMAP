# openmap/__init__.py


import configparser
import getpass

import os
from pathlib import Path
# import warnings
# warnings.filterwarnings("ignore")

from openmap.util.log import logger

import yaml

# loc = Path(__file__).resolve().parent
# filepath = Path(os.path.join(loc, 'campaign'))
# try:
#     filepath.mkdir(parents=True, exist_ok=False)
# except FileExistsError:
#     logger.info('Folder "campaign" is already there')
# else:
#     logger.info('Folder "campaign" was created')

__version__ = '0.1.0'
