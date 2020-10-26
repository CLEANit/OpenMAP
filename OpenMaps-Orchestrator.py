#!/usr/bin/env python

import os, sys
import numpy as np
import pandas as pd
import pickle
import json
import yaml
from subprocess import Popen
from AWS import sql_wrapper  # RemoteDB
from category_writer import CategoryWriter
from ChemOs.phoenics_inc import gryffin as Gryffin
import argparse
import getpass

# ===============================================================================
# from .generate_descriptors import generate_descriptors
#import main

# ==============================================================================

# ===============================================================================
parser = argparse.ArgumentParser(description='Automated  Optimizer')
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                    help='an integer for the accumulator')

parser.add_argument('--seed', metavar='N', action='store', dest='seed',type=int,
                    help='seed value')

parser.add_argument('--budget',
                    dest='budget',
                    type=int,
                    default=10,
                    action='store',
                    #const='value-to-store',
                    help='how many experiment you want to perform')

parser.add_argument('--batch',
                    dest='batch_size',
                    type=int,
                    default=2,
                    action='store',
                    #const='value-to-store',
                    help='batch size')

parser.add_argument('--config1',
                    metavar='path',
                    dest='ChemOs',
                    type=str,
                    default='./Configuration/ChemOs_config.json',
                    action='store',
                    help='the path to  ChemOs config file')

parser.add_argument('--config2',
                    metavar='path',
                    dest='HPC',
                    type=str,
                    default='./Configuration/HPC_config',
                    action='store',
                    help='the path to  HPC config file')

parser.add_argument('--config3',
                    metavar='path',
                    dest='DataBase',
                    type=str,
                    default='./Configuration/DataBase_config',
                    action='store',
                    help='the path to  Data Base config file')

# parser.add_argument('-f',
#                     dest='features',
#                     #type=str,
#                     default=[],
#                     action='store',
#                     required=True,
#                     help='List of predictor to include in the model')

# parser.add_argument('-B', action='append_const', dest='const_collection',
#                     const='value-2-to-append',
#                     help='Add different values to list')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')

args = parser.parse_args()


# ==============================================================================


#NUM_TOTAL = 100  # len of the data base
BUDGET = args.budget  # how many experiment you want to perform
ChemOs_CONFIG = args.ChemOs
ChemOs_CONFIG_FILE =  json.load(open(args.ChemOs, 'r').read())
HPC_CONFIG = yaml.safe_load(open(args.HPC).read())
DataBase_CONFIG= yaml.safe_load(open(args.DataBase).read())
#BATCH_SIZE = args.batch_size
# params = yaml.safe_load(open("Tools/data/miedema.yml").read())
seed = args.seed


# download data from Aws

aws =  sql_wrapper.RemoteDB(DataBase_CONFIG['host'],
                            DataBase_CONFIG['user'],
                            DataBase_CONFIG['dbname'],
                            DataBase_CONFIG['password'])

# need a dictionnary with project and BD and Table


# check bd and table
if not aws.checkDbExists(DB_NAME=DataBase_CONFIG['dbname']):
    aws.create_database(DB_NAME=DataBase_CONFIG['dbname'])

if not aws.checkTableExists(DataBase_CONFIG['tablename']):
    data_df = fetch_data_online()
    aws.df_to_sql(data_df,DataBase_CONFIG['tablename'])
else:
    data_df = aws.load_table_to_pandas(DataBase_CONFIG['tablename'])

# initialize descriptor

features = DataBase_CONFIG['features']

BATCH_SIZE = ChemOs_CONFIG.get('general')["sampling_strategies"]

parameter_name = ChemOs_CONFIG.get('parameters')["name"]
objective_name = ChemOs_CONFIG.get("objectives")['name']
category_writer = CategoryWriter(parameter_name, features)
struct_id = DataBase_CONFIG['structure_id']



# generate_descriptors
category_writer.generate_descriptors(data_df, struct_id=struct_id)

# initialize category writer
category_writer.write_categories(home_dir='./', with_descriptors=False)

# initialize Gryffin
gryffin = Gryffin.Phoenics(ChemOs_CONFIG_FILE, random_seed=seed)

# main loop
evaluations = 0
observations = []
while evaluations < BUDGET:
    samples = gryffin.recommend(observations=observations)
    print(samples)
    new_observations = []
    sample_id_list = [int(sample[parameter_name][0]) for sample in samples]
    measurements = main.main(sample_id_list)
    for sample, measurement in zip(samples, measurements):
        sample[objective_name] = measurement
        new_observations.append(sample)
    #
    print('new observations : ', new_observations)
    observations.extend(new_observations)
    pickle.dump(observations, open(f'runs/gryf_{seed}.pkl', 'wb'))
    evaluations += BATCH_SIZE
    print('EVALUATIONS : ', evaluations)
