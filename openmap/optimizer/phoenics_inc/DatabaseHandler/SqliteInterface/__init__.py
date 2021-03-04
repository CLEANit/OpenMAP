#!/usr/bin/env python

__author__ = 'Florian Hase'

# =======================================================================

import sys

from utilities import PhoenicsModuleError

# =======================================================================

try:
    import sqlalchemy as sql
except ModuleNotFoundError:
    _, error_message, _ = sys.exc_info()
    extension = '\n\tTry installing the sqlalchemy package or use a different database framework instead.'
    PhoenicsModuleError(str(error_message) + extension)

# =======================================================================

from DatabaseHandler.SqliteInterface.sqlite_database import SqliteDatabase
from DatabaseHandler.SqliteInterface.sqlite_operations import (
    AddEntry,
    FetchEntries,
    UpdateEntries,
)
