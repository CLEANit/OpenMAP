# save job in h5 file
import numpy as np
import h5py
from pathlib import Path
import os
import pickle
import ase
from ase.db import connect
from ase.io import read, jsonio
from ase.utils import PurePath
import subprocess
from pymatgen import Structure
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.io.vasp.inputs import Poscar
from pymatgen.io.vasp.inputs import Potcar
from pymatgen.io.vasp.inputs import Kpoints
from pymatgen.io.vasp.inputs import Incar
from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.io.vasp.sets import MPRelaxSet
from pymatgen.io.vasp.sets import MPStaticSet

from openmap.computing import files
from openmap.computing import client
from openmap.core import parser
from openmap.core import properties


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
                file = parser.parse_file(file_path)
                prop = properties.Property(file)
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


class JOB(object):

    def __init__(self, job_id=None, name=None, remote_path=None, local_path=None, output=None):
        self.job_id = job_id
        self.name = name
        self.remote_path = remote_path
        self.local_path = local_path
        self.output = output
        self.make_wordir()
        self.remote = client.RemoteClient(host, user, self.remote_path, self.local_path, passphrase, ssh_key_filepath)

    # hf = h5py.File('data.h5', 'w')
    def make_wordir(self):
        # os.makedirs(local_file_directory, exist_ok=True)
        Path(self.local_path).mkdir(parents=True, exist_ok=True)

    def upload_files_to_remote(self, remote):
        """
        Upload files to remote via SCP.
        """
        local_files = files.fetch_local_files(self.local_path)
        remote.bulk_upload(local_files)

    def upload_dir_to_remote(self, remote, job_list):
        """
        Upload directory to remote via SCP.
        """
        for job in job_list:

            if not os.path.isdir(os.path.join(self.local_path, job)):
                print(f"The file {os.path.join(self.local_path, job)} does not exist")
                continue
            remote.dir_upload(os.path.join(self.local_path, job), remote_path=os.path.join(self.remote_path, job))

    # def download_file_from_remote(self, remote):
    #     """
    #     download directory  via SCP.
    #     """
    #     for i in range(631):
    #         remote_path = os.path.join('/home/ctetsass/scratch/OpenMap/AgPd', 'AgPd_{}'.format(i + 1), 'vasp_output')
    #         local_path = os.path.join('/Users/ctetsass/Calculation_NRC/OpenMAPs/HPC_Job/AgPd', 'AgPd_{}'.format(i + 1))
    #
    #         # remote.download_file(remote_path + '/Alloys_00002', local_file_directory)
    #         remote.download_file(remote_path, local_directory=local_path)
    def make_dir_on_remote(self, remote):
        """
        Create a Directory on Remote,
        if it not exit
        """
        remote.mkdir_p(os.path.join(self.remote_path))

    def run_job(self, remote, job_list):
        """
        Execute UNIX command on the remote host.
        """
        jobs = []
        job_ids = []

        for jobb in job_list:
            job_id = remote.sbatch(os.path.join(self.remote_path, jobb), job_file=jobb + '_vasp_job.sh')
            job_ids.append(job_id)
            jobs.append({"id": job_id, "name": jobb, "remote_path": os.path.join(self.remote_path, jobb),
                         "local_path": os.path.join(self.local_path, jobb), "output": 'vasp_output'})

        return jobs

    def job_monitoring(self, remote, jobs):
        remote.monitor_batch(jobs)
