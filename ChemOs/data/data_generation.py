#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 10:07:07 2020

@author: ctetsass
"""

import numpy as np
from ase.lattice.cubic import FaceCenteredCubic 
from ase.calculators.emt import EMT
from ase.db import connect
from ase.eos import EquationOfState
from icet.tools import enumerate_structures

# generate data base with pure metal 
ref_db = connect('reference_database.db')

metals = ['Al', 'Au', 'Cu', 'Ag', 'Pd', 'Pt', 'Ni']
#metals = ['Al', 'Au', 'Cu', 'Ag']

for m in metals:
    atoms = FaceCenteredCubic(m)
    atoms.calc = EMT()
    e0 = atoms.get_potential_energy()
    a = atoms.cell[0][0]

    eps = 0.05
    volumes = (a * np.linspace(1 - eps, 1 + eps, 9))**3
    energies = []
    for v in volumes:
        atoms.set_cell([v**(1. / 3)] * 3, scale_atoms=True)
        energies.append(atoms.get_potential_energy())

    eos = EquationOfState(volumes, energies)
    v1, e1, B = eos.fit()

    atoms.set_cell([v1**(1. / 3)] * 3, scale_atoms=True)
    ef = atoms.get_potential_energy()

    ref_db.write(atoms, metal=m,
             latticeconstant=v1**(1. / 3),
             energy_per_atom=ef / len(atoms))
    
    
#generate database with random 4 metal and compute properties




prim= FaceCenteredCubic('Al')

db = connect('fcc_alloys.db')

population_size = 100

i =0 
for structure in enumerate_structures(prim, range(5), metals):
    if len(structure) < 4:# Take only those with 8 site occy
        continue
    else:
        c_Al = structure.get_chemical_symbols().count('Al') / len(structure)
        c_Au = structure.get_chemical_symbols().count('Au') / len(structure)
        c_Cu = structure.get_chemical_symbols().count('Cu') / len(structure)
        c_Ag = structure.get_chemical_symbols().count('Ag') / len(structure)
        c_Pd = structure.get_chemical_symbols().count('Pd') / len(structure)
        c_Pt = structure.get_chemical_symbols().count('Pt') / len(structure)
        c_Ni = structure.get_chemical_symbols().count('Ni') / len(structure)
        db.write(structure,c_Al=c_Al,c_Au=c_Au,c_Ag=c_Ag,c_Cu=c_Cu,c_Pd=c_Pd,c_Pt=c_Pt,c_Ni=c_Ni)
        i+=1
    if i >= population_size:
        break



    
def relax(db, ref_db):
    
    for row in db.select():
        atoms = row.toatoms()
        atoms_string = atoms.get_chemical_symbols()

        # Open connection to the database with reference data

       

        # Compute the average lattice constant of the metals in this individual
        # and the sum of energies of the constituent metals in the fcc lattice
        # we will need this for calculating the heat of formation
        #a = 0
        ei = 0
        for m in set(atoms_string):
            dct = ref_db.get(metal=m)
            count = atoms_string.count(m)
            #a += count * dct.latticeconstant
            ei += count * dct.energy_per_atom
       
        

        # Since calculations are extremely fast with EMT we can also do a volume
        # relaxation
        atoms.calc = EMT()
        a = atoms.cell[0][0]
        eps = 0.05
        volumes = (a * np.linspace(1 - eps, 1 + eps, 9))**3
        energies = []
        for v in volumes:
            atoms.set_cell([v**(1. / 3)] * 3, scale_atoms=True)
            energies.append(atoms.get_potential_energy())

        eos = EquationOfState(volumes, energies)
        v1, ef, B = eos.fit()
        latticeconstant = v1**(1. / 3)
        
        atoms.set_cell([v1**(1. / 3)] * 3, scale_atoms=True)
        
        ef = atoms.get_potential_energy()
        # Calculate the heat of formation by subtracting ef with ei
        hof = (ef - ei) / len(atoms)

        db.update(row.id, volume= v1, latticeconstant= latticeconstant, 
                  mixing_energy=hof, bm =  B )


relax(db, ref_db)

# save the database as json file 

#ase db fcc_alloys.db --insert-into fcc_alloys.json
