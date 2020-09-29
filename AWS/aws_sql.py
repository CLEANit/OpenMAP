import json
import logging

import os
import pandas as pd
import pymysql
import numpy as np
import sqlite3
import getpass
import sqlalchemy
import pickle
import mysql.connector
from mysql.connector import errorcode

import sys

# from ParamikoTools.log import logger
logger = logging.getLogger(__name__)


# try:
#     body = bucket.Object(object_key).get()['Body'].read()
#     logger.info("Got object '%s' from bucket '%s'.", object_key, bucket.name)
# except ClientError:
#     logger.exception(("Couldn't get object '%s' from bucket '%s'.",
#                       object_key, bucket.name))
#     raise
# else:
#     return body


class AWS_sql_client:
    """Client to interact with a sql data base on aws """

    def __init__(self, host, user, port, dbname, password=None):
        self.host = host
        self.user = user
        self.port = port
        self.dbname = dbname
        self.password = password  # getpass.getpass()
        self.conn = None

    # @logger.catch
    def _connect(self):
        """Open connection to remote host. """
        if self.password is None:
            self.password = getpass.getpass(prompt='Enter the database Password: ', stream=None)

        if self.conn is None:
            try:
                logger.info(" Opening connection to   AWS-MySQL  [{}] database : {}".format(self.dbname))
                self.conn = mysql.connector.connect(host=self.host,
                                                    user=self.user,
                                                    port=self.port,
                                                    password=self.password,
                                                    database=self.dbname)
            except mysql.connector.Error as error:
                logger.error("Authentication to  AWS-MySQL table failed  : {}".format(error))
                raise error
            except TimeoutError as e:
                logger.error(f'Timeout.. trying again.')
                # continue
        return self.conn

        # self.conn = self._connect()

    def checkTableExists(self, tablename, dbcon=None):

        if dbcon is None:
            self.conn = self._connect()
        dbcur = self.conn.cursor()
        dbcur.execute("""SELECT COUNT(*)FROM 
        information_schema.tablesWHERE table_name = '{0}' """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone()[0] == 1:
            dbcur.close()
            return True

        dbcur.close()
        return False

    def create_table(self, dbcon, table_name, table_description, drop=False):
        if dbcon is None:
            self.conn = self._connect()
        cursor = self.con.cursor()

        try:
            logger.info("Creating table [{}]: ".format(table_name))
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                if drop:
                    logger.info("Dropping table [{}]: ".format(table_name))
                    cursor.execute("DROP TABLE IF EXISTS {}".format(table_name))
                else:
                    logger.error(f' Table [{table_name}] already exists.')
            else:
                logger.error(f' {err.msg}')
        else:
            logger.info("Table  created ")

            # cursor.close()
            # dbcon.close()
