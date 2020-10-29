#!/usr/bin/env python

import numpy as np
import pandas as pd

from ase.calculators.emt import EMT
from ase.db import connect
from ase.eos import EquationOfState


#===============================================================================


#===============================================================================




    

def get_bulk_modulus(input_atoms):
        
    input_atoms.calc = EMT()
    a = input_atoms.cell[0][0]
    eps = 0.05
    volumes = (a * np.linspace(1 - eps, 1 + eps, 9))**3
    energies = []
    for v in volumes:
        input_atoms.set_cell([v**(1. / 3)] * 3, scale_atoms=True)
        energies.append(input_atoms.get_potential_energy())

    eos = EquationOfState(volumes, energies)
    v1, ef, B = eos.fit()
        #latticeconstant = v1**(1. / 3)
        
        #atoms.set_cell([v1**(1. / 3)] * 3, scale_atoms=True)
        
        
    return B
    
