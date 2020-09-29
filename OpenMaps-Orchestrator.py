#!/usr/bin/env python

import os, sys
import numpy as np
import pandas as pd
import pickle
import json
import yaml
from subprocess import Popen
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

parser.add_argument('-f',
                    dest='features',
                    #type=str,
                    default=[],
                    action='store',
                    required=True,
                    help='List of predictor to include in the model')

# parser.add_argument('-B', action='append_const', dest='const_collection',
#                     const='value-2-to-append',
#                     help='Add different values to list')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')

args = parser.parse_args()


# ==============================================================================


#NUM_TOTAL = 100  # len of the data base
BUDGET = args.budget  # how many experiment you want to perform
ChemOs_CONFIG_FILE =  json.load(open(args.ChemOs, 'r').read())
HPC_CONFIG_FILE = yaml.safe_load(open(args.HPC).read())
DataBase_CONFIG_FILE = yaml.safe_load(open(args.DataBase).read())
#BATCH_SIZE = args.batch_size
# params = yaml.safe_load(open("Tools/data/miedema.yml").read())
seed = args.seed

# initialize descriptor
json_file = json.load(open(ChemOs_CONFIG_FILE, 'r').read())
data_df = None
features = args.features

BATCH_SIZE = ChemOs_CONFIG_FILE.get('general')["sampling_strategies"]

parameter_name = ChemOs_CONFIG_FILE.get('parameters')["name"]
objective_name = ChemOs_CONFIG_FILE.get("objectives")['name']
category_writer = CategoryWriter(parameter_name, features)
struct_id = 'id'
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
