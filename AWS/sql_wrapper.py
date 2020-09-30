
#!/usr/bin/env python

__author__ = 'Conrard TETSASSI'


import json
import logging

import os
import pandas as pd
import pymysql
import numpy as np
import getpass
import sqlalchemy
import pickle
import mysql.connector
from mysql.connector import errorcode
from ase import Atoms

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


class RemoteDB:
    """Client to interact with a sql data base on aws """

    def __init__(self, host, user, port, dbname, password=None):
        self.host = host
        self.user = user
        self.port = port
        self.dbname = dbname
        self.password = password  # getpass.getpass()
        self.conn = None
        self.cursor = None

    # @logger.catch
    def _connect(self):
        """Open connection to remote database server. """
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

    def disconnect(self):
        """Close  connection to the database server"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def checkTableExists(self, tablename, dbcon=None):
        """
        :param tablename:
        :param dbcon:
        :return:
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        self.cursor.execute("""SELECT COUNT(*)FROM 
        information_schema.tablesWHERE table_name = '{0}' """.format(tablename.replace('\'', '\'\'')))
        if self.cursor.fetchone()[0] == 1:
            self.cursor.close()
            return True

        dbcur.close()
        return False

    def create_table(self, table_name, table_description,  dbcon=None, drop=False):
        """
        :param table_name:
        :param table_description:
        :param dbcon:
        :param drop:
        :return:
        """
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        try:
            logger.info("Creating table [{}]: ".format(table_name))
            self.cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                if drop:
                    logger.info("Dropping table [{}]: ".format(table_name))
                    self.cursor.execute("DROP TABLE IF EXISTS {}".format(table_name))
                else:
                    logger.error(f' Table [{table_name}] already exists.')
            else:
                logger.error(f' {err.msg}')
        else:
            logger.info("Table  created ")

        self.cursor.close()
            # dbcon.close()

    def load_table_to_pandas(self, tablename, dbcon=None):
        """
        :param tablename: name of the table
        :param dbcon: connection to the database
        :return: pandas dataframe
        """
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn

        pandas_df = pd.read_sql( "select * from {} ".format(tablename), dbcon)

        for col in pandas_df.columns:
            try:
                pandas_df[col] = pandas_df.apply(lambda x: pickle.loads(x[col]), axis=1)
            except:
                continue

        for col in pandas_df.columns:
            try:
                pandas_df[col] = pandas_df.apply(lambda x: x[col].decode(), axis=1)
            except:
                continue

        return pandas_df

    def get_columns_name(self, table_name, dbcon=None):
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn

        self.cursor = dbcon.cursor()
        sql_select_query = "select * from  {}".format(tablename)
        self.cursor.execute(sql_select_query)
        field_names = [i[0] for i in cursor.description]
        self.cursor.close()
        return field_names

    def get_structrure(self, tablename, struc_id, dbcon=None):
        """
        :param tablename:
        :param struc_id: list of id to fecth
        :param dbcon:
        :return: return a list of Ase Atoms class
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn

        field_names = self.get_columns_name(table_name, dbcon)

        self.cursor = dbcon.cursor()
        atms = []
        sql_select_query = "select * from  {} where id = %s".format(tablename)
        for struc in struc_id:
            self.cursor.execute(sql_select_query, (struc_id,))
            record = self.cursor.fetchall()
            numbers = pickle.loads(record[0][field_names.index('numbers')])
            positions = pickle.loads(record[0][field_names.index('positions')])
            cell = pickle.loads(record[0][field_names.index('cell')])
            #pbc = pickle.loads(record[0][field_names.index('pbc')])

            atm = Atoms(numbers=numbers, positions=positions, cell=cell)
            atms.append(atm)
        self.cursor.close()
        return atms