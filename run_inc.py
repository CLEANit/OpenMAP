#!/usr/bin/env python

import os, sys
import numpy as np
import pandas as pd
import pickle

from category_writer import CategoryWriter
from phoenics_inc    import Phoenics as Gryffin


#===============================================================================

from ase.db import connect

from Calculations import utils

#==============================================================================

NUM_TOTAL = 100 # len of the data base
BUDGET    = 50 # how many experiment you want to perform
CONFIG_FILE = 'config.json'
seed = int(sys.argv[1])
#seed = int(0)


# initializ category writer
category_writer = CategoryWriter()
category_writer.write_categories(home_dir = './', with_descriptors = False)

# initialize Gryffin
gryffin = Gryffin(CONFIG_FILE, random_seed = seed)

# main loop
evaluations = 0
observations = []
data_db = connect('data/fcc_alloys.db')
while evaluations < BUDGET: 
    samples = gryffin.recommend(observations = observations) 
    new_observations  = [] 
    for sample in samples:
        structure_id = int(sample['alloys'][0]) 
        atoms=data_db.get(id=structure_id).toatoms()
        measurement = utils.get_bulk_modulus(atoms)
        sample['bulk_modulus'] = measurement
        new_observations.append(sample)

    print('new observations : ', new_observations)
    observations.extend(new_observations)
    pickle.dump(observations, open(f'runs/gryf_{seed}.pkl', 'wb'))
    evaluations += 2
    print('EVALUATIONS : ', evaluations)
