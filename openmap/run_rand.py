#!/usr/bin/env python

import os, sys
import numpy as np
import pandas as pd
import pickle

#===============================================================================
from ase.db import connect

from Calculations import utils

#==============================================================================

NUM_TOTAL = 100
BUDGET    = 50
CONFIG_FILE = 'ChemOs_config.json'
seed = int(sys.argv[1])
#seed =0
np.random.seed(seed)


avail_params = np.arange(NUM_TOTAL)+1

#==========================================================================
# helper functions

def random_num_gen(avail_params):
	ix = np.random.choice(np.arange(avail_params.shape[0]))
	#param = np.random.choice(avail_params)
	return avail_params[ix], ix

#==========================================================================
# main loop

observations = []

data_db = connect('data/fcc_alloys.db')
for _ in range(BUDGET):
    structure_id, ix = random_num_gen(avail_params)
    atoms=data_db.get(id=int(structure_id)).toatoms()
    measurement = utils.get_bulk_modulus(atoms)
    
    new_observations = [{'alloys' : [f'{structure_id}'],
						 'bulk_modulus': measurement}]

    avail_params = np.delete(avail_params, ix, axis = 0)
    print('new observations : ', new_observations)
    print('num avail : ', len(avail_params))
    observations.extend(new_observations)
    pickle.dump(observations, open(f'runs/rand_{seed}.pkl', 'wb'))
