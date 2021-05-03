import os
import random

# import sys

# path = str(Path(Path(__file__).parent.absolute().parent.absolute()))
# sys.path.insert(0, path)
import pickle
import json
import yaml
import numpy as np
import argparse
from pathlib import Path
from pymatgen import MPRester
from openmap import __version__
from openmap.util.category_writer import CategoryWriter
from openmap.data_wrapper import search_db
from optimizer.phoenics_inc import gryffin as Gryffin
from openmap.util.log import logger
from openmap.qm_mm.input_generator import InputGenerator
from openmap.qm_mm.job import JobManager
from openmap.ssh_host.hpc_resources import hosts, projects, allocations
from openmap.qm_mm.vasp.slurm import qsub_vasp2
from openmap.ssh_host import client

# ============================ Configuration =====================================

# ===============================================================================
parser = argparse.ArgumentParser(description='Automated  Optimizer')
parser.add_argument('--seed', metavar='N', action='store', dest='seed', type=int,
                    help='seed value')

parser.add_argument('--budget',
                    dest='budget',
                    type=int,
                    default=4,
                    action='store',
                    # const='value-to-store',
                    help='how many experiment you want to perform')

parser.add_argument('--project',
                    dest='project',
                    type=str,
                    default='TEST',
                    action='store',
                    # required=True,
                    help='project name')

parser.add_argument('--user',
                    dest='user',
                    type=str,
                    default='Tetsassic',
                    action='store',
                    # required=True,
                    help='OpenMAP User Name')

parser.add_argument('--version', action='version', version=__version__)

args = parser.parse_args()

# ================================ HCP  details ================================


try:
    OpenMap_project = projects[args.project]

except:
    print(f' The project {args.project} does not exist would you like to create')

# TODO
# try:
#     OpenMap_user = projects[args.user]
#       if user not in .....
#     print(f' The user {args.project} does not exist would you like to create')
# except:
#     print(f' The user {args.project} does not exist would you like to create')
# ===============================================================================
workdir = '/home/ctetsass/Work/OpenMap'

with open(os.path.join(workdir, 'configuration/Optimizer_config.json'), 'r') as fr:
    Gryffin_CONFIG = json.load(fr)

with open(os.path.join(workdir, 'configuration/HPC_config.yml'), 'r') as fr:
    HPC_CONFIG = yaml.safe_load(fr)

with open(os.path.join(workdir, 'configuration/DataBase_config.yml'), 'r') as fr:
    DataBase_CONFIG = yaml.safe_load(fr)

with open(os.path.join(workdir, 'configuration/Query.yml'), 'r') as fr:
    Query = yaml.safe_load(fr)

# ============================ Create Chemical space =====================================
#
# 1- wrap data online  material project, open quantum, nomad

data = search_db.get_pd_db(Query['criteria'], 'mp')

#   2- update openmap database
#

#   3- create the chemical space

data_df = data.copy(deep=True)

data_df = search_db.featurizing_composition(data_df, 'mp')

# ================ Config Phoenics Optimizer ========================================


# NUM_TOTAL =   # len of the data base
BUDGET = args.budget  # how many experiment you want to perform
seed = args.seed
seed = random.randint(0, 100)

Gryffin_CONFIG_FILE = os.path.join(workdir, 'configuration/Optimizer_config.json')

BATCH_SIZE = Gryffin_CONFIG.get('general')['sampling_strategies']

campaign_name = Gryffin_CONFIG.get('parameters')[0]['name']
objective_name = Gryffin_CONFIG.get('objectives')[0]['name']

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# TODO
# check bd and table on server
# create target colunm in the destination table

# ================ Descriptors for ML =============================================

# create target Column
features = data_df.columns.tolist()
if objective_name not in features:
    data_df[objective_name] = np.nan
    features.append(objective_name)

to_drop = ['material_id', 'elasticity', 'energy_per_atom']
features = [prop for prop in data_df.columns.tolist() if prop not in to_drop]

category_writer = CategoryWriter(campaign_name, features)

# generate_descriptors
category_writer.generate_descriptors(data_df, id_colm='material_id')

# initialize category writer
category_writer.write_categories(with_descriptors=False)

# +++++++++++++++++++++++++++  ++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ================ Initilize Optimizer =============================================
#
gryffin = Gryffin.Phoenics(Gryffin_CONFIG_FILE, random_seed=random.randint(0, 10))

run_dir = os.path.join('campaign', campaign_name)
# try:
#     Path(run_dir).mkdir(parents=True, exist_ok=False)
# except FileExistsError:
#     logger.info(f'Simulation Folder "{campaign_name}" is already there')
# else:
#     logger.info(f'Simulation Folder "{campaign_name}" was created')

# +++++++++++++++++++++++++++  ++++++++++++++++++++++++++++++++++++++++++++++++++++++


# ================ Optimization loop =============================================

inputgenerator = InputGenerator(local_path=run_dir)
# remove the file  h5file if exit
h5file = os.path.join(run_dir, 'jobs.h5')
if Path(h5file).is_file():
    Path(h5file).unlink()

# +++++++++++++++++++++++++++  ++++++++++++++++++++++++++++++++++++++++++++++++++++++

# main loop
evaluations = 0
observations = []
mpr = MPRester()
while evaluations < BUDGET:
    samples = []
    # 1 take a sample
    samples = gryffin.recommend(observations=observations)

    new_observations = []
    sample_id_list = []
    sample_id_list = [sample[campaign_name][0] for sample in samples]

    # 2 check the objective for each system in the sample

    to_be_measured = [idx for idx in sample_id_list if
                      data_df.loc[data_df['material_id'] == idx, objective_name].isnull().values.any()]
    # computing_idx = [i for i in range(len(measurements)) if measurements[i] =='None']

    if len(to_be_measured) == 0:
        measurements = [data_df.loc[data_df['material_id'] == idx, objective_name].values[0] for idx in sample_id_list]
        for sample, measurement in zip(samples, measurements):
            sample[objective_name] = measurement
            new_observations.append(sample)
        #
        print('new observations : ', new_observations)
        observations.extend(new_observations)
        pickle.dump(observations, open(f'{run_dir}/gryf_{seed}.pkl', 'wb'))
        evaluations += BATCH_SIZE
        print('EVALUATIONS : ', evaluations)

    else:
        # 3 load structure from materials project
        structures = [mpr.get_structure_by_material_id(idx) for idx in to_be_measured]

        # 4 generate input for the simulation

        job_paths = inputgenerator.input_from_structure(to_be_measured, structures, objective_name, software='vasp')
        account = OpenMap_project['allocations'][0]  # ['def-itamblyn-ac', 'def-mkarttu', 'rrg-mkarttu-ab']
        allocation = allocations[account]

        host = hosts[allocation['host']]

        job_description = {'time': 1,
                           'ntask': 2,
                           'memory': 8000,
                           'email': None,
                           'gpu': 0,
                           'account': account,
                           'binary': host['binaries']['vasp_serial'],
                           'objective_name': objective_name}

        job_manager = JobManager(campaign_name=campaign_name, local_path=run_dir, remote_path=host['sub_text'])

        # 5 write submission file (slurm) and module to update result on aws (python)

        for path, sample in zip(job_paths, to_be_measured):
            qsub_vasp2.write_slurm_job(path, job_description)
            # aws.write_slurm_job(job, job_description)

        # 5 upload input on HPC

        remote = client.RemoteClient(
            host=host['hostname'],
            user=allocation['users'],
            remote_path=host['sub_text'],
            local_path=os.path.join(str(Path.home()), 'MAPS', campaign_name),
            passphrase=HPC_CONFIG['passphrase'],
            ssh_key_filepath=HPC_CONFIG['ssh_key_filepath']
        )
        # 6 upload and submit job
        jobs = {}
        for path, sample in zip(job_paths, to_be_measured):
            job_manager.upload_dir_to_remote(remote, sample)  # upload job dir
            jobs[sample] = job_manager.run_job(remote, sample)

        # 7 Monitor job
        computing_results = remote.monitor_batch(jobs)

        # remote.disconnect()

        job_manager.save_dict_to_hdf5(jobs, h5file)
        for sample in to_be_measured:
            remote.kill(jobs[sample]['id'])

        # 8 TODO  Extract computed objective
        measurements = [data_df.loc[data_df['material_id'] == idx, 'energy_per_atom'].values[0] for idx in
                        sample_id_list]

        for sample, measurement in zip(samples, measurements):
            sample[objective_name] = measurement
            new_observations.append(sample)
            #
    print('new observations : ', new_observations)
    observations.extend(new_observations)
    pickle.dump(observations, open(f'{run_dir}/gryf_{seed}.pkl', 'wb'))
    evaluations += BATCH_SIZE
    print('EVALUATIONS : ', evaluations)
    # # # 10 go to #1


