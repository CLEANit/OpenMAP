#!/usr/bin/env python
#from __future__ import absolute_import
#from __future__ import division
#from __future__ import print_function


import json
import yaml
from aws import sql_wrapper  # RemoteDB
from core.category_writer import CategoryWriter
from core.Fetch_data_online import FetchData
import argparse

from pymatgen import Composition
from matminer.featurizers.composition import ElementFraction

from ChemOs.phoenics_inc import gryffin as Gryffin

# ===============================================================================

#TestCase =  OpenMapsTestCase()
#TestCase.test_requirements()
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
                    default='./configuration/config.json',
                    action='store',
                    help='the path to  ChemOs config file')

parser.add_argument('--config2',
                    metavar='path',
                    dest='HPC',
                    type=str,
                    default='./configuration/HPC_config.yml',
                    action='store',
                    help='the path to  HPC config file')

parser.add_argument('--config3',
                    metavar='path',
                    dest='DataBase',
                    type=str,
                    default='./configuration/DataBase_config.yml',
                    action='store',
                    help='the path to  Data Base config file')

parser.add_argument('--query',
                    metavar='path',
                    dest='query',
                    type=str,
                    default='./configuration/Query.yml',
                    action='store',
                    help='the path to  query file')


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
ChemOs_CONFIG_FILE = args.ChemOs
ChemOs_CONFIG =  json.load(open(args.ChemOs, 'r'))
HPC_CONFIG = yaml.safe_load(open(args.HPC).read())
DataBase_CONFIG= yaml.safe_load(open(args.DataBase).read())
query = yaml.safe_load(open(args.query).read())
#BATCH_SIZE = args.batch_size
# params = yaml.safe_load(open("core/data/miedema.yml").read())
seed = args.seed


# download data from Aws

print(DataBase_CONFIG['port'], type(DataBase_CONFIG['port']))
aws =  sql_wrapper.RemoteDB(DataBase_CONFIG['host'],
                            DataBase_CONFIG['user'],
                            DataBase_CONFIG['port'],
                            DataBase_CONFIG['dbname'],
                            DataBase_CONFIG['password'])

# need a dictionnary with project and BD and Table


# check bd and table
if not aws.checkDbExists(DB_NAME=DataBase_CONFIG['dbname']):
    aws.create_database(DB_NAME=DataBase_CONFIG['dbname'])



if not aws.checkTableExists(DataBase_CONFIG['tablename']):
    fetchdata = FetchData(query['criteria'], query['properties'])
    data_df = fetchdata.fetch_MP() # fetch data on Materials Project
    #data_df.rename(columns={'full_formula':'formula'})

    #aws.df_to_sqltable(data_df,DataBase_CONFIG['tablename'])
    aws.df_to_sql(data_df,DataBase_CONFIG['tablename'])

else:
    pass
    #data_df = aws.load_table_to_pandas(DataBase_CONFIG['tablename'])
    data_df = aws.read_table_to_df(DataBase_CONFIG['tablename'])

#create target colunm in the data base


def featurizing_composition(data_df, formula='full_formula',threshold=0.0):
    """
    composition: pymatgen composition packge
    """
    df = data_df.copy()
    ef = ElementFraction()
    df.insert(2, 'composition', df.apply(lambda x: Composition(x[formula]), axis=1))
    df = ef.featurize_dataframe(df, "composition")
    df=df.drop(df.std()[df.std() <= threshold].index.values, axis=1)
    return df

# initialize descriptor
df = featurizing_composition(data_df, formula='full_formula',threshold=0.0)

to_drop = ['map_id','material_id' , 'total_magnetization', 'composition', 'full_formula']

features = [prop for prop in data_df.columns.tolist() if prop not in to_drop]



#features = DataBase_CONFIG['features']





BATCH_SIZE = ChemOs_CONFIG.get('general')['sampling_strategies']

parameter_name = ChemOs_CONFIG.get('parameters')[0]["name"]
objective_name = ChemOs_CONFIG.get("objectives")[0]['name']
category_writer = CategoryWriter(parameter_name, features)
id_colm = DataBase_CONFIG['id_colm']



# generate_descriptors
category_writer.generate_descriptors(data_df, id_colm=id_colm)

# initialize category writer
category_writer.write_categories(home_dir='../', with_descriptors=False)

# initialize Gryffin
gryffin = Gryffin.Phoenics(ChemOs_CONFIG_FILE, random_seed=seed)
#
# # main loop
# evaluations = 0
# observations = []
# while evaluations < BUDGET:
#     samples = gryffin.recommend(observations=observations)
#     print(samples)
#     new_observations = []
#     sample_id_list = [int(sample[parameter_name][0]) for sample in samples]
#     measurements = main.main(sample_id_list)
#     for sample, measurement in zip(samples, measurements):
#         sample[objective_name] = measurement
#         new_observations.append(sample)
#     #
#     print('new observations : ', new_observations)
#     observations.extend(new_observations)
#     pickle.dump(observations, open(f'runs/gryf_{seed}.pkl', 'wb'))
#     evaluations += BATCH_SIZE
#     print('EVALUATIONS : ', evaluations)
