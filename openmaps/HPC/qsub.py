from pathlib import Path
import os

from ase.db import connect

from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.io.vasp.sets import MPRelaxSet
from pymatgen.io.vasp.sets import MPStaticSet

# ===================================================

from openmaps.computing.qsub_vasp import write_vasp_slurm_job

# ===================================================

hostname = 'cedar.computecanada.ca'  # sys.argv[1]
account = 'rrg-mkarttu-ab'
username = 'ctetsass'  # sys.argv[2]
password = 'Gastipard_Isaro'  # getpass.getpass()
# ================================================

project_name = 'Alloys'
Work_dir = '/Users/ctetsass/Calculation_NRC/OpenMAPs'
Job_dir = os.path.join(Work_dir, 'HPC_Job', project_name)
# Job_output_dir = os.path.join(Work_dir, 'HPC_Job', project_name, 'OUTPUT')
data_dir = os.path.join(Work_dir, 'Data')
database = 'fcc_alloys.db'

Path(Job_dir).mkdir(parents=True, exist_ok=True)

# Path(Job_output_dir).mkdir(parents=True, exist_ok=True)

# ===================================================
# Connect to the database: ASE database
# ===================================================
db = connect(os.path.join(data_dir, database))

# ===================================================
# get structure parameters
# ===================================================
atoms = db.get(id=1).toatoms()

# Change ase Atom object into pymatgen structure object
struct = AseAtomsAdaptor.get_structure(atoms)

# ===================================================
# setup calculation type
# ===================================================
# Use Material project relax Calculation parameter

static_set = MPStaticSet(struct)
relax_set = MPRelaxSet(struct)
id = 1
job_name = project_name + "_{:05d}".format(id)

# ===================================================
# define job optimized parameters
# ===================================================
job_description = {'time': 1,
                   'ntask': 4,
                   'memory': 4000,
                   'email': None,
                   'gpu': 0,
                   'account': "def-itamblyn-ac",
                   'project': "Alloys"}

# cluster = ClusterCommunicator(hostname=hostname, username=username, password=password)
# partitions = cluster.get_partition_info()
#
#
#
#
#
#
# partition = None
# for part in partitions:
#     if job_description['time'] <= part.maxDays:
#         partition = part
#         break
# if partition is None:
#     print(" Running time has been modified to the maximum time limit: {} days".format(partitions[-1].maxDays))
#     job_description['time'] = partitions[-1].maxDays
#
# print(partitions[-1].maxDays)

# write vasp input parameter

relax_set.write_input(output_dir=os.path.join(Job_dir, job_name, 'input_vasp'), potcar_spec=False, zip_output=False)

write_vasp_slurm_job(os.path.join(Job_dir, job_name), job_description, gpu=0)

# def zipdir(path, ziph):
#    # ziph is zipfile handle
#    for root, dirs, files in os.walk(path):
#        for file in files:
#            ziph.write(os.path.join(root, file))

# zipf = zipfile.ZipFile(os.path.join(Job_dir, project_name,job_name)+'.zip', 'w', zipfile.ZIP_DEFLATED)
# zipdir(os.path.join(Job_dir, project_name,job_name), zipf)
# zipf.close()
# os.remove(os.path.join(Job_dir, project_name,job_name)+'.zip')
