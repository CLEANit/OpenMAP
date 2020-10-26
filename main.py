#!/usr/bin/env python

"""Script entry point."""

# from paramiko_tutorial import main
#
# if __name__ == '__main__':
#     main()

from pathlib import Path
import os
import pickle
from ase.db import connect
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.io.vasp.inputs import Poscar
from pymatgen.io.vasp.inputs import Potcar
from pymatgen.io.vasp.inputs import Kpoints
from pymatgen.io.vasp.inputs import Incar
from pymatgen.io.vasp.outputs import Vasprun

from ParamikoTools import client  # RemoteClient
from ParamikoTools import files  # fetch_local_files
from ParamikoTools import qsub_vasp
from AWS import sql_wrapper
from ParamikoTools.log import logger

from Tools import Parser
from Tools import Properties

from config_remote_client import (
    host,
    account,
    user,
    ssh_key_filepath,
    local_file_directory,
    remote_path,
    passphrase,
    project_name

)

print('host : {}'.format(host))
print('user : {}'.format(user))
print('remote_path : {}'.format(remote_path))
print('local_file_directory : {}'.format(local_file_directory))

# os.makedirs(local_file_directory, exist_ok=True)
Path(local_file_directory).mkdir(parents=True, exist_ok=True)

# ===================================================
# Connect to the database:
# This define the search space
# ASE database
# ===================================================


# data_dir = os.path.join(local_file_directory, 'Data', project_name)
data_dir = os.path.join(local_file_directory, 'Data')
os.makedirs(data_dir, exist_ok=True)
# database = 'Ag-Pd-to-be-calculated.db'
database = 'fcc_alloys.db'
bucket_name = 'alloys'


@logger.catch
def download_file_from_AWS(bucket, key, filename):
    logger.info(f'Connecting to  AWS  BUCKET: {bucket}')
    sql_wrapper.download_file(bucket, key, filename)
    logger.info(f'Finished  downloading: [{key}] from AWS')


@logger.catch
def upload_file_to_AWS(bucket, key, filename):
    logger.info(f'Connecting to  AWS  BUCKET: {bucket}')
    sql_wrapper.upload_file(bucket, key, filename)
    logger.info(f'Finished  uploading: [{key}] to AWS')


download_file_from_AWS(bucket_name, database, os.path.join(data_dir, database))


db = connect(os.path.join(data_dir, database))


# ===================================================
# Generate descriptor (id from data base): extra properties from data base
# Category writer :
# ===================================================


# ===================================================
# Take a  sample ( n systems )
# ===================================================


# ===================================================
# get structure of systems in the sample
# write inputs for calculations
# ===================================================

#sample_list = [58, 78]
# job_list = []


class JOB(object):

    def __init__(self, id=None, name=None, remote_path=None, local_path=None, output=None):
        self.id = id
        self.name = name
        self.remote_path = remote_path
        self.local_path = local_path
        self.output = output


def main(sample_list=None):
    """
    Initialize remote host client and execute actions

    """
    job_list = []
    job_list = master(sample_list)
    remote = client.RemoteClient(host, user, remote_path, local_file_directory, passphrase, ssh_key_filepath)
    make_dir_on_remote(remote)  # make remote dir if not exist
    upload_dir_to_remote(remote, job_list)  # upload job dir
    # # # upload_files_to_remote(remote)
    # # # execute_command_on_remote(remote) # run job
    # # # job_ids = []
    #
    jobs = run_job(remote, job_list)
    pickle.dump(jobs, open("jobs.pkl", "wb"))
    # # job_ids = [49700634,  49700739, 49700746, 49700748, 49700749]
    job_monitoring(remote, jobs)  # # monitor job
    # # # download_file_from_remote(remote)
    # # # results = prepare_results(jobs)  to update the data base
    # #jobs = pickle.load(open("jobs.pkl", "rb"))
    objective = get_objective(jobs, "energy_per_atom")
    #
    # # print(f"Objectives : {objectives}")
    # # for job in jobs:
    # #    subprocess.call(f'rm -rf  {job["local_path"]}', shell=True)
    remote.disconnect()
    return objective


@logger.catch
def master(sample_list):
    """
    :param sample_list: list of  system to compute
    :return: list of job file to be submitted
    """
    job_list = []
    for sample_id in sample_list:
        atoms = db.get(id=int(sample_id)).toatoms()
        # atoms_list = atoms.get_chemical_symbols()

        struct = AseAtomsAdaptor.get_structure(atoms)
        symbol_set = struct.symbol_set

        # write vasp input with pymatgen

        # Job_descriptor: define job parameter  base on structure,  job type and
        # write job file
        job_name = project_name + "_{:d}".format(int(sample_id))
        job_list.append(job_name)
        Path(os.path.join(local_file_directory, job_name, 'vasp_input')).mkdir(parents=True, exist_ok=True)
        # === Prepare Input ===
        # static_set = MPStaticSet(struct)
        # relax_set = MPRelaxSet(struct)
        # relax_set.write_input(output_dir=os.path.join(Job_dir, job_name, 'input_vasp'), potcar_spec=False, zip_output=False)

        # POSCAR
        poscar = Poscar(structure=struct)
        poscar.write_file(os.path.join(local_file_directory, job_name, 'vasp_input', 'POSCAR'))

        # INCAR
        incar_dict = {
            # "ALGO": "Fast",
            # "GGA": "PE",
            "PREC": "Accurate",
            "ISMEAR": 1,
            "ENCUT": 384,
            "EDIFF": 1e-06,
            "ISIF": 3,
            "IBRION": 2,
            "NSW": 100,
            "LORBIT": 11,
            "SIGMA": 0.05
        }
        incar = Incar(incar_dict)
        incar.write_file(os.path.join(local_file_directory, job_name, 'vasp_input', 'INCAR'))

        # POTCAR

        # metals = ['Al', 'Au', 'Cu', 'Ag', 'Pd', 'Pt', 'Ni']

        basis_sets = {"Al": 'Al_GW',
                      "Au": 'Au_GW',
                      "Cu": 'Cu_GW',
                      "Ag": 'Ag_GW',
                      "Pd": 'Pd_GW',
                      "Pt": 'Pt_GW',
                      "Ni": 'Ni_GW'}
        basis_set = [basis_sets[element] for element in symbol_set]
        potcar = Potcar(symbols=basis_set, functional='PBE_54')
        potcar.write_file(os.path.join(local_file_directory, job_name, 'vasp_input', 'POTCAR'))

        # KPOINTS
        kpoints = Kpoints.monkhorst_automatic(kpts=(8, 8, 8), shift=(0.0, 0.0, 0.0))
        kpoints.write_file(os.path.join(local_file_directory, job_name, 'vasp_input', 'KPOINT'))

        job_description = {'time': 1,
                           'ntask': 4,
                           'memory': 8000,
                           'email': None,
                           'gpu': 0,
                           'account': account}

        qsub_vasp.write_slurm_job(os.path.join(local_file_directory, job_name), job_description)

        logger.info(f'Create job  {job_name} on local host')
    return job_list


def upload_files_to_remote(remote):
    """
    Upload files to remote via SCP.
    """
    local_files = files.fetch_local_files(local_file_directory)
    remote.bulk_upload(local_files)


def upload_dir_to_remote(remote, job_list):
    """
    Upload directory to remote via SCP.
    """
    for job in job_list:

        if not os.path.isdir(os.path.join(local_file_directory, job)):
            print(f"The file {os.path.join(local_file_directory, job)} does not exist")
            continue
        remote.dir_upload(os.path.join(local_file_directory, job),
                          remote_path=os.path.join(remote_path, job))


def download_file_from_remote(remote):
    """
    Upload directory to remote via SCP.
    """
    for i in range(631):
        remote_path = os.path.join('/home/ctetsass/scratch/OpenMaps/AgPd', 'AgPd_{}'.format(i + 1), 'vasp_output')
        local_path = os.path.join('/Users/ctetsass/Calculation_NRC/OpenMAPs/HPC_Job/AgPd', 'AgPd_{}'.format(i + 1))

        # remote.download_file(remote_path + '/Alloys_00002', local_file_directory)
        remote.download_file(remote_path, local_directory=local_path)


def make_dir_on_remote(remote):
    """
    Create a Directory on Remote,
    if it not exit
    """
    remote.mkdir_p(os.path.join(remote_path))


# def execute_command_on_remote(remote):
#     """
#     Execute UNIX command on the remote host.
#     """
#
#     return remote.execute_command([f'cd {job_directory};sbatch {job_file}'])


def run_job(remote, job_list):
    """
    Execute UNIX command on the remote host.
    """
    jobs = []
    job_ids = []

    for jobb in job_list:
        job_id = remote.sbatch(os.path.join(remote_path, jobb), job_file=jobb + '_vasp_job.sh')
        job_ids.append(job_id)
        jobs.append({"id": job_id, "name": jobb, "remote_path": os.path.join(remote_path, jobb),
                     "local_path": os.path.join(local_file_directory, jobb), "output": 'vasp_output'})

    return jobs


def job_monitoring(remote, jobs):
    remote.monitor_batch(jobs)


def prepare_results(jobs):
    """ get all of the results of the previous batch ready to be inserted into the DB
        will return a list of dictionaries
    """
    results = []
    for job in jobs:
        vrun = Vasprun(filename=os.path.join(job["local_path"], 'vasp_output/vasprun.xml'))
        energy = vrun.final_energy
        volume = vrun.final_structure.volume
        abc = vrun.final_structure.lattice.abc
        mol_dict = {'energy': energy, 'volume': volume, 'abc': abc}
        results.append(mol_dict)

    return results


def get_objective(jobs, prop_name):
    objectives = []
    for job in jobs:

        file_path = os.path.join(job["local_path"], 'vasp_output/vasprun.xml')

        if os.path.isfile(file_path):
            try:
                file = Parser.parse_file(file_path)
                prop = Properties.Property(file)
                objective = prop.get_property(prop_name)
                objectives.append(objective)
            except:
                print("Unable to read  {}".format(file_path))
                objectives.append(None)
                continue

        else:
            print("The file {} does not exist".format(file_path))
            objectives.append(None)
            continue
    return objectives


# Yield successive n-sized
# chunks from l.
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


# How many elements each


# list should have
# n = 10
#
# my_list = np.arange(1, 632)
#
# sample_lists = list(divide_chunks(my_list, n))
#
# for sample_list in sample_lists:
#     #print(list(sample_list))
#     main(list(sample_list))
if __name__ == '__main__':
    #download_file_from_AWS(bucket_name, database, os.path.join(data_dir, database))
    main()
