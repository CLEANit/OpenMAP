from pathlib import Path
import os
import glob
import zipfile
import sys
import re
import numpy as np

import ase
from ase.db import connect
from ase.io import read, jsonio
from ase.utils import PurePath

from pymatgen import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.io.vasp.inputs import Poscar
from pymatgen.io.vasp.inputs import Potcar
from pymatgen.io.vasp.inputs import Kpoints
from pymatgen.io.vasp.inputs import Incar
from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.io.vasp.sets import MPRelaxSet
from pymatgen.io.vasp.sets import MPStaticSet

# ===================================================

from qsub_vasp import write_vasp_slurm_job

# ===================================================
project_name = 'Alloys'
Work_dir = '/Users/ctetsass/Calculation_NRC/OpenMAP'
Job_dir = os.path.join(Work_dir, 'HPC_Job', project_name)
# Job_output_dir = os.path.join(Work_dir, 'HPC_Job', project_name, 'OUTPUT')
data_dir = os.path.join(Work_dir, 'Data')
database = 'fcc_alloys.db'

Path(Job_dir).mkdir(parents=True, exist_ok=True)
# Path(Job_output_dir).mkdir(parents=True, exist_ok=True)

# Connect to the database: ASE database
db = connect(os.path.join(data_dir, database))

# get structure parameters
atoms = db.get(id=1).toatoms()

# Change ase Atom object into pymatgen structure object
struct = AseAtomsAdaptor.get_structure(atoms)

# Use Material project static Calculation parameter
static_set = MPStaticSet(struct)
relax_set = MPRelaxSet(struct)
id = 1
job_name = project_name + "_{:05d}".format(id)

job_description = {'time': 1,
                   'ntask': 4,
                   'memory': 4000,
                   'email': None,
                   'gpu': 1,
                   'account': "def-itamblyn-ac",
                   'project': "Alloys"}

# write vasp imput parameter
relax_set.write_input(output_dir=os.path.join(Job_dir, job_name, 'job'), potcar_spec=False, zip_output=False)

write_vasp_slurm_job(os.path.join(Job_dir, job_name), job_description, gpu=False)

# def zipdir(path, ziph):
#    # ziph is zipfile handle
#    for root, dirs, files in os.walk(path):
#        for file in files:
#            ziph.write(os.path.join(root, file))

# zipf = zipfile.ZipFile(os.path.join(Job_dir, project_name,job_name)+'.zip', 'w', zipfile.ZIP_DEFLATED)
# zipdir(os.path.join(Job_dir, project_name,job_name), zipf)
# zipf.close()
# os.remove(os.path.join(Job_dir, project_name,job_name)+'.zip')
