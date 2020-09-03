#!/usr/bin/env python

import os, sys
import numpy as np
import pandas as pd
import pickle
from subprocess import Popen
from category_writer import CategoryWriter
from ChemOs.phoenics_inc import gryffin as Gryffin

# ===============================================================================
#from .generate_descriptors import generate_descriptors
import main


# ==============================================================================

NUM_TOTAL = 100  # len of the data base
BUDGET = 50  # how many experiment you want to perform
CONFIG_FILE = 'config.json'
BATCH_SIZE = 5
#seed = int(sys.argv[1])
seed = int(0)


# initialize descriptor

#generate_descriptors

# initialize category writer
category_writer = CategoryWriter()
category_writer.write_categories(home_dir='./', with_descriptors=False)

# initialize Gryffin
gryffin = Gryffin.Phoenics(CONFIG_FILE, random_seed=seed)

# main loop
evaluations = 0
observations = []
while evaluations < BUDGET:
    samples = gryffin.recommend(observations=observations)
    print(samples)
    new_observations = []
    sample_id_list = [int(sample['alloys'][0]) for sample in samples]
    measurements = main.main(sample_id_list)
    for sample, measurement in zip(samples, measurements):
        sample['energy'] = measurement
        new_observations.append(sample)
    #
    print('new observations : ', new_observations)
    observations.extend(new_observations)
    pickle.dump(observations, open(f'runs/gryf_{seed}.pkl', 'wb'))
    evaluations += BATCH_SIZE
    print('EVALUATIONS : ', evaluations)
