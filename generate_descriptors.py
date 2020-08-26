#!/usr/bin/env python

import os, sys
import glob
import json
import pandas as pd
from ase.db import connect 

if __name__ == '__main__':

    db = connect('data/fcc_alloys.db') 
    
    
    
    descriptors = {}

    for row in db.select():
        
        descriptors[row.id] = {'mixing_energy': row.mixing_energy,
                                   'mass':row.mixing_energy,
                                   'volume':row.volume,
                                   'latticeconstant':row.latticeconstant,
                                   'c_Al':row.c_Al,
                                   'c_Au':row.c_Au,
                                   'c_Cu':row.c_Cu,
                                   'c_Ag':row.c_Ag,
                                   'c_Pd':row.c_Pd,
                                   'c_Pt':row.c_Pt,
                                   'c_Ni':row.c_Ni}
                                

    print(descriptors)

    with open('alloys.json', 'w') as fp:
        json.dump(descriptors, fp, indent=6)
