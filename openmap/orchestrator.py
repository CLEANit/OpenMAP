#!/usr/bin/env python
import argparse
import os
import pickle
import sys
from pathlib import Path

from matminer.featurizers.composition import ElementFraction
from pymatgen import Composition, MPRester

from aws import aws_hcp, sql_wrapper
from category_writer import CategoryWriter
from computing import client
from computing.input_generator import InputGenerator
from computing.job import JobManager
from computing.slurm_vasp import qsub_vasp2
from configuration import ChemOs_CONFIG, DataBase_CONFIG, Query
from configuration.resources import allocations, hosts, projects
from online_wrapper import FetchData
from optimizer.phoenics_inc import gryffin as Gryffin

# ===============================================================================

# TestCase =  OpenMapsTestCase()
# TestCase.test_requirements()
# ==============================================================================


# ===============================================================================
parser = argparse.ArgumentParser(description='Automated  Optimizer')
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                    help='an integer for the accumulator')

parser.add_argument('--seed', metavar='N', action='store', dest='seed', type=int, help='seed value')

parser.add_argument(
    '--budget',
    dest='budget',
    type=int,
    default=4,
    action='store',
    # const='value-to-store',
    help='how many experiment you want to perform',
)

# parser.add_argument('--batch_size',
#                     dest='batch_size',
#                     type=int,
#                     default=1,
#                     action='store',
#                     # const='value-to-store',
#                     help='batch size')

parser.add_argument(
    '--project',
    dest='project',
    type=str,
    default='OER',
    action='store',
    # required=True,
    help='project name default:  Oxygen Evolution Reaction',
)

parser.add_argument(
    '--user',
    dest='user',
    type=str,
    default='Tetsassic',
    action='store',
    # required=True,
    help='OpenMAP User Name',
)

# parser.add_argument('-B', action='append_const', dest='const_collection',
#                     const='value-2-to-append',
#                     help='Add different values to list')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')

args = parser.parse_args()

# ================================ HCP  details ==========================
try:
    OpenMap_project = projects[args.project]

except BaseException:
    print(f' The project {args.project} does not exist would you like to create')


# try:
#     OpenMap_user = projects[args.user]
#       if user not in .....
#     print(f' The user {args.project} does not exist would you like to create')
#
# except:
#     print(f' The user {args.project} does not exist would you like to create')
# ===============================================================================


# NUM_TOTAL =   # len of the data base
BUDGET = args.budget  # how many experiment you want to perform
ChemOs_CONFIG_FILE = 'configuration/Optimizer_config.json'

# BATCH_SIZE = args.batch_size

seed = args.seed

BATCH_SIZE = ChemOs_CONFIG.get('general')['sampling_strategies']

campaign_name = ChemOs_CONFIG.get('parameters')[0]['name']
objective_name = ChemOs_CONFIG.get('objectives')[0]['name']

id_colm = DataBase_CONFIG['id_colm']

# download data from Aws

print(DataBase_CONFIG['port'], type(DataBase_CONFIG['port']))
aws = sql_wrapper.RemoteDB(
    DataBase_CONFIG['host'],
    DataBase_CONFIG['user'],
    DataBase_CONFIG['port'],
    DataBase_CONFIG['dbname'],
    DataBase_CONFIG['password'],
)

# need a dictionnary with project and BD and Table


# check bd and table
if not aws.checkDbExists(DB_NAME=DataBase_CONFIG['dbname']):
    aws.create_database(DB_NAME=DataBase_CONFIG['dbname'])

if not aws.checkTableExists(DataBase_CONFIG['tablename']):
    fetchdata = FetchData(Query['criteria'], Query['properties'])
    data_df = fetchdata.wrap_mp  # fetch data on Materials Project
    # data_df.rename(columns={'full_formula':'formula'})

    # aws.df_to_sqltable(data_df,DataBase_CONFIG['tablename'])
    aws.df_to_sql(data_df, DataBase_CONFIG['tablename'])

else:
    pass
    # data_df = aws.load_table_to_pandas(DataBase_CONFIG['tablename'])
    data_df = aws.read_table_to_df(DataBase_CONFIG['tablename'])

# create target colunm in the destination table

if not aws.checkColumnExists(DataBase_CONFIG['tablename'], objective_name):
    aws.add_column(DataBase_CONFIG['tablename'], objective_name, 'FLOAT')


# Create Descriptors from composition
def featurizing_composition(data_df, formula='full_formula', threshold=0.0):
    """
    composition: pymatgen composition packge
    """
    df = data_df.copy()
    ef = ElementFraction()
    df.insert(2, 'composition', df.apply(lambda x: Composition(x[formula]), axis=1))
    df = ef.featurize_dataframe(df, "composition")
    df = df.drop(df.std()[df.std() <= threshold].index.values, axis=1)
    return df


# initialize descriptor
df = featurizing_composition(data_df, formula='full_formula', threshold=0.0)

to_drop = ['map_id', 'material_id', 'composition', 'full_formula']

features = [prop for prop in data_df.columns.tolist() if prop not in to_drop]

# features = DataBase_CONFIG['features']


category_writer = CategoryWriter(campaign_name, features)

# generate_descriptors
category_writer.generate_descriptors(data_df, id_colm=id_colm)

# initialize category writer
category_writer.write_categories(home_dir='./', with_descriptors=False)

# initialize Gryffin
gryffin = Gryffin.Phoenics(ChemOs_CONFIG_FILE, random_seed=seed)
#


#######################
# deal with User Host .... history of user in database
#####################
mpr = MPRester()
# main loop
evaluations = 0
observations = []
workdir = os.path.join(str(Path.home()), 'MAPS', campaign_name)
inputgenerator = InputGenerator(local_path=workdir, software='vasp')

# remove the file  h5file if exit
h5file = 'runs/jobs.h5'
if Path(h5file).is_file():
    Path(h5file).unlink()
while evaluations < BUDGET:
    samples = []
    # 1 take a sample
    samples = gryffin.recommend(observations=observations)

    new_observations = []
    sample_id_list = []
    sample_id_list = [sample[campaign_name][0] for sample in samples]

    # 2 check the objective for each system in the sample
    measurements = [aws.get_value(DataBase_CONFIG['tablename'], objective_name, id_colm, idx) for idx in sample_id_list]
    computing_idx = [i for i in range(len(measurements)) if measurements[i] is None]

    # if len(computing_idx) == 0:
    #     for sample, measurement in zip(samples, measurements):
    #         sample[objective_name] = measurement
    #         new_observations.append(sample)
    #     #
    #     print('new observations : ', new_observations)
    #     observations.extend(new_observations)
    #     pickle.dump(observations, open(f'runs/gryf_{seed}.pkl', 'wb'))
    #     evaluations += BATCH_SIZE
    #     print('EVALUATIONS : ', evaluations)
    if len(computing_idx) != 0:
        computing_list = []
        computing_list = [sample_id_list[i] for i in computing_idx]

        # 3 load structure from materials project
        structures = [mpr.get_structure_by_material_id(idx) for idx in computing_list]

        # 4 generate input

        job_paths = inputgenerator.vasp_input_from_structure(computing_list, structures, objective_name)

        # ['def-itamblyn-ac', 'def-mkarttu', 'rrg-mkarttu-ab']
        account = OpenMap_project['allocations'][0]
        allocation = allocations[account]

        host = hosts[allocation['host']]

        job_description = {
            'time': 1,
            'ntask': 2,
            'memory': 8000,
            'email': None,
            'gpu': 0,
            'account': account,
            'binary': host['binaries']['vasp_serial'],
            'objective_name': objective_name,
        }

        job_manager = JobManager(campaign_name=campaign_name, local_path=workdir, remote_path=host['sub_text'])

        # write submission file (slurm) and module to update result on aws
        # (python)

        for path, sample in zip(job_paths, computing_list):
            qsub_vasp2.write_slurm_job(path, job_description)
            # aws.write_slurm_job(job, job_description)

            checkWords = (
                "@host",
                "@port",
                "@dbname",
                "@user",
                "@password",
                "@tablename",
                "@colname",
                # "@val",
                "@id_col",
                "@struc_id",
            )
            repWords = (
                DataBase_CONFIG['host'],
                str(DataBase_CONFIG['port']),
                DataBase_CONFIG['dbname'],
                DataBase_CONFIG['user'],
                DataBase_CONFIG['password'],
                DataBase_CONFIG['tablename'],
                objective_name,
                # "@objective",
                id_colm,
                sample,
            )

            job_manager.write_slurm_aws(aws_hcp, path, checkWords, repWords)
            # # 4 upload input on HPC

        remote = client.RemoteClient(
            host=host['hostname'],
            user=allocation['users'],
            remote_path=host['sub_text'],
            local_path=os.path.join(str(Path.home()), 'MAPS', campaign_name),
            passphrase=allocation['passphrase'],
            ssh_key_filepath=allocation['key'],
        )
        # 5 submit job
        jobs = {}
        for path, sample in zip(job_paths, computing_list):
            job_manager.upload_dir_to_remote(remote, sample)  # upload job dir
            jobs[sample] = job_manager.run_job(remote, sample)

        remote.disconnect()
        job_manager.save_dict_to_hdf5(jobs, h5file)
        # jobs_dict = job_manager.load_dict_from_hdf5(h5file)
        # hf = h5py.File('runs/job.h5', 'w')

        # 6 check db (aws) if jobs  are completed
        computing_results = aws.monitoring(
            computing_list, DataBase_CONFIG['tablename'], objective_name, id_colm, sleeptime=120, dbcon=None
        )

    for idx, result in zip(computing_idx, computing_results):
        measurements[idx] = result
    # 7 Extract computed objective from aws table

    for sample, measurement in zip(samples, measurements):
        sample[objective_name] = measurement
        new_observations.append(sample)
        #
    print('new observations : ', new_observations)
    observations.extend(new_observations)
    pickle.dump(observations, open(f'runs/gryf_{seed}.pkl', 'wb'))
    evaluations += BATCH_SIZE
    print('EVALUATIONS : ', evaluations)
    # # # 10 go to #1
