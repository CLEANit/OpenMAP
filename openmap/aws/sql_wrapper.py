
import logging

import pandas as pd
import getpass
import sqlalchemy
import pickle
import mysql.connector
from mysql.connector import errorcode
from ase import Atoms

from openmap.computing.log import logger
#logger = logging.getLogger(__name__)


__version__ = '0.1'
__author__ = 'Conrard TETSASSI'
__maintainer__ = 'Conrard TETSASSI'
__email__ = 'ConrardGiresse.TetsassiFeugmo@nrc-cnrc.gc.ca'
__status__ = 'Development'


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
                logger.info("Opening connection to aws database")
                self.conn = mysql.connector.connect(host=self.host,
                                                    user=self.user,
                                                    port=self.port,
                                                    password=self.password,
                                                    database=self.dbname)
                logger.info("Connection established to aws:    database  [{}]".format(self.dbname))
            except mysql.connector.Error as error:
                logger.error("Authentication to  aws-MySQL table failed  : {}".format(error))
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

    def checkDbExists(self,  DB_NAME=None, dbcon=None):
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        if DB_NAME is None:
            DB_NAME = self.dbname

        self.cursor.execute("SHOW DATABASES")

        db_list = [name[0] for name in self.cursor]
        if DB_NAME in db_list:
            self.cursor.close()
            return True

        self.cursor.close()
        return False

    def checkTableExists(self, tablename, DB_NAME=None, dbcon=None):
        """
        :param tablename:
        :param dbcon:
        :return:
        """
        if DB_NAME is None:
            DB_NAME = self.dbname

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        self.cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{0}'".format(tablename.replace('\'', '\'\'')))
        if self.cursor.fetchone()[0] == 1:
            self.cursor.close()
            logger.info("Table [{}] found in the database [{}]".format(tablename,DB_NAME ))
            return True

        self.cursor.close()
        logger.info("Table [{}] not found in the database [{}]".format(tablename, DB_NAME))
        return False

    def create_database(self, DB_NAME=None, dbcon=None):
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()
        if DB_NAME is None:
            DB_NAME = self.dbname

        try:
            self.cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
        except mysql.connector.Error as err:
            logger.info(" {}".format(err))
            #print(" {}".format(err))
            exit(0)

        try:
            self.cursor.execute("USE {}".format(DB_NAME))
        except mysql.connector.Error as err:
            logger.info("Database {} does not exists.".format(DB_NAME))
            #print("Database {} does not exists.".format(DB_NAME))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                create_database(self.cursor)
                #print("Database {} created successfully.".format(DB_NAME))
                logger.info("Database {} created successfully.".format(DB_NAME))
                dbcon.database = DB_NAME
            else:
                logger.error(f' {err}')
                #print(err)
                exit(1)

    def create_table(self, table_name, table_description,DB_NAME=None,  dbcon=None, drop=False):
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

        if DB_NAME is None:
            DB_NAME = self.dbname

        try:
            logger.info("Creating table [{}]: ".format(table_name))
            self.cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                if drop:
                    logger.info("Dropping table [{}]: ".format(table_name))
                    self.cursor.execute("DROP TABLE IF EXISTS {}".format(table_name))
                else:
                    logger.error(f'Table [{table_name}] already exists.')
            else:
                logger.error(f'{err.msg}')
        else:
            logger.info("Table  created ")

        self.cursor.close()
            # dbcon.close()




    def df_to_sql(self, df, tablename, dbcon=None):
        """
        use the sqlalchemy package to upload a Dataframe
        :param df: Dataframe
        :param tablename:
        :param dbcon:
        :return:
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn

        engine = sqlalchemy.create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=self.host, db=self.dbname,
                                                                                           user=self.user, pw=self.password))


        try:
            logger.info(f"Writing  [{tablename}] table  to aws")
            df.to_sql(name=tablename,
                      con=engine,
                      if_exists='append',
                      index=False, # It means index of DataFrame will save. Set False to ignore the index of DataFrame.
                      chunksize=1000)  # Just means chunksize. If DataFrame is big will need this param

        except ValueError as vx:
            logger.error(f"{vx}")

        except Exception as ex:
            logger.error(f"{ex}")

        else:
            logger.info(f"Table {tablename} created successfully")

        finally:
            self.cursor.close()



    def insert_Dataframe_to_DB(self,df, tablename, dbcon=None):
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        # creating column list for insertion
        cols = "`,`".join([str(i) for i in df.columns.tolist()])

        # Insert DataFrame recrds one by one.
        for i, row in df.iterrows():
            sql = f"INSERT INTO `{tablename}` (`" + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
            self.cursor.execute(sql, tuple(row))

            # the connection is not necesserly autocommitted(pymysql, mysql-connection)  , so we must commit to save our changes
        try:
            dbcon.commit()
        except:
            pass
        finally:
            self.cursor.close()

    def df_to_sqltable(self,  df, tablename,DB_NAME=None,  dbcon=None, drop=False):
        """
        :param df: DataFrame to upload
        :param tablename: name of the table
        :param DB_NAME:
        :param dbcon:
        :param drop: drop the table if exists
        :return:
        """

        colms = ['`'+i+'`' for i in df.columns.tolist()]
        types = [str(df[col].dtypes) for col in df.columns.tolist()]
        #if isinstance(row[prop], (np.ndarray, np.generic)):
        for i, typ in enumerate(types):
            if typ == 'object':
                types[i] = 'varchar(255)'
            elif typ == 'float64' or 'float32':
                types[i] = 'FLOAT' # 'DECIMAL(12, 6)'
            elif typ == 'int64' or 'int32':
                types[i] = 'INT'

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        self.cursor = dbcon.cursor()

        if DB_NAME is None:
            DB_NAME = self.dbname

        description =  [" ".join([i,j]) for i, j in zip(colms, types)]

        description = ",".join([str(i) for i in description])
        sql = f"CREATE TABLE {tablename}  (" + description + ")"

        try:
            logger.info("Creating table [{}]: ".format(tablename))
            self.cursor.execute(sql)

            # creating column list for insertion
            cols = "`,`".join([str(i) for i in df.columns.tolist()])

            # Insert DataFrame recrds one by one.
            for i, row in df.iterrows():
                sql = f"INSERT INTO `{tablename}` (`" + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
                self.cursor.execute(sql, tuple(row))
            try:
                dbcon.commit()
            except:
                pass

            logger.info("Table [{}] has been  created  successfully".format(tablename))
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                if drop:
                    logger.info("Dropping table [{}]: ".format(table_name))
                    self.cursor.execute("DROP TABLE IF EXISTS {}".format(tablename))
                    self.cursor.execute(f" CREATE TABLE {tablename}  (" + description + ")}")

                    # creating column list for insertion
                    cols = "`,`".join([str(i) for i in df.columns.tolist()])

                    # Insert DataFrame recrds one by one.
                    for i, row in df.iterrows():
                        sql = f"INSERT INTO `{tablename}` (`" + cols + "`) VALUES (" + "%s," * (len(row) - 1) + "%s)"
                        self.cursor.execute(sql, tuple(row))
                    try:
                        dbcon.commit()
                    except:
                        pass

                    logger.info("Table [{}] has been  created successfully".format(tablename))
                else:
                    logger.error(f'Table [{tablename}] already exists.')
            else:
                logger.error(f' {err.msg}')


        self.cursor.close()
            # dbcon.close()


    def read_table_to_df(self, tablename, dbcon=None):
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn

        try:
            pandas_df = pd.read_sql("SELECT * FROM  {}".format(tablename), dbcon)
        except ValueError as vx:
            logger.error(f"{vx}")

        except Exception as ex:
            logger.error(f"{ex}")

        else:
            logger.info(f"Table {tablename} loaded successfully to  Dataframe")

        finally:
            self.cursor.close()
        return   pandas_df

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
        try :
            self.cursor = dbcon.cursor()
            sql_select_query = "select * from  {}".format(tablename)
            self.cursor.execute(sql_select_query)
            field_names = [i[0] for i in cursor.description]
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
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

    def get_value(self, tablename, colname, id_col, struc_id, dbcon=None):
        """
        :param tablename: name of the table
        :param colname: column to check
        :param id_col: name of the column with structure id
        :param struc_id: id of the structure == row
        :param dbcon: connection to db
        :return: return value of column [colname] at row [struc_id]
        """
        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn


        try:
            self.cursor = dbcon.cursor()
            sql_select_query = f"select {colname} from  {tablename} where {id_col} ={struc_id} "
            self.cursor.execute(sql_select_query)
            record = self.cursor.fetchall()
            return record[0][0]
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            self.cursor.close()


    def add_column(self,tablename, colname, coltype, dbcon=None):
        """
        add column in a table
        :param tablename:
        :param colname:
        :param coltype: type off the colunm to add
        :param dbcon:
        :return:
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        try:
            self.cursor = dbcon.cursor()
            sql = f'ALTER TABLE  {tablename} ADD {colname} {coltype}'
            self.execute(sql)
            logging.info(f'Table [{tablename}] altered with column [{colname}]')
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            self.cursor.close()

    def drop_column(self,tablename, colname, dbcon=None):
        """
        drop a column in a table
        :param tablename:
        :param colname:
        :param dbcon:
        :return:
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        try:
            self.cursor = dbcon.cursor()
            sql = f'ALTER TABLE  {tablename} DROP COLUMN  {colname}'
            self.execute(sql)
            logging.info(f' column [{colname}] in table [{tablename}]')
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            self.cursor.close()

    def insert_value(self,tablename, colname, val,id_col, struc_id, dbcon=None):
        """
        :param tablename:
        :param colname:
        :param val:
        :param id_col:
        :param struc_id:
        :param dbcon:
        :return:
        """

        if dbcon is None:
            self.conn = self._connect()
            dbcon = self.conn
        try:
            self.cursor = dbcon.cursor()
            sql = f'UPDATE   {tablename} SET  {colname}= {val} WHERE {id_col}={struc_id}'
            self.cursor.execute(sql)
        except Exception as ex:
            logger.error(f"{ex}")
        finally:
            self.cursor.close()

    @logger.catch
    def monitor_batch(self, jobs):
        """
        :param jobs: list of dictionary with job information
        :return:
        """
        status_list = [None for job in jobs]
        while not all(status == 'COMPLETED' for status in status_list):
            status_list = [self.sacct(job["id"]) for job in jobs]
            job_ids = [job["id"] for job in jobs]
            for id, status in zip(job_ids, status_list):
                logger.info(f' {id}:  {status}')
            #
            if all(status == 'COMPLETED' for status in status_list):
                logger.info(f'All Jobs COMPLETED')
                continue
            else:
                sleeptime = 120
                countdown(sleeptime)
        for job in jobs:
            if not self.check_remote_dir(job["remote_path"]):
                print(f'The file {job["remote_path"]} does not exist')
                continue
            self.download_file(job["remote_path"] + '/' + job["output"], local_directory=job["local_path"])
            self.clean_dir(job["remote_path"])
            logger.info(f'Job:  {job["name"]}  Cleaned on {self.host}')
        # for job in jobs:
        #    self.clean_dir(job.remote_path)
        #    logger.info(f'file: {job.name}  Cleaned on {self.host}')
        logger.info(f'Task completed')
        return None