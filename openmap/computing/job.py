# save job in h5 file
import numpy as np
import h5py
from pathlib import Path
import os

from openmap.configuration.resources import users, hosts, projects, allocations

from openmap.computing import files
from openmap.computing import client
from openmap.analysis import parser
from openmap.analysis import properties


class JobProfile(object):

    def __init__(self, job_id=None, name=None, remote_path=None, local_path=None, output=None):
        self.job_id = job_id
        self.name = name
        self.remote_path = remote_path
        self.local_path = local_path
        self.output = output


class JobManager(object):

    def __init__(self, campaign_name, local_path, remote_path):
        self.campaign_name = campaign_name
        self.remote_path = os.path.join(remote_path, 'MAPS', campaign_name)
        self.local_path = local_path
        # self.make_workdir()
        self.software = None

    # hf = h5py.File('data.h5', 'w')
    def make_workdir(self):
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
        self.make_dir_on_remote(remote)  # make remote dir if not exist

        for job in job_list:

            if not os.path.isdir(os.path.join(self.local_path, job)):
                print(f"The file {os.path.join(self.local_path, job)} does not exist")
                continue
            remote.dir_upload(os.path.join(self.local_path, job), remote_path=os.path.join(self.remote_path, job))

    def download_file_from_remote(self, remote, job_list):
        """
        download directory  via SCP.
        """
        for job in job_list:
            copy_dir = os.path.join(self.remote_path, job, 'vasp_output.tar.gz')
            dest_dir = os.path.join(self.local_path, job)
            remote.download_file(copy_dir, local_directory=dest_dir)

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

    def write_slurm_aws(self, script, input_path,checkWords, repWords):

        if not os.path.isdir(input_path):
            raise Exception("The directory {} does not exist".format(input_path))

        basename = os.path.basename(os.path.normpath(input_path))


        outputfile = os.path.join(input_path, basename + "_aws_job.py")

        jobname = basename
        ofile = open(outputfile, "w")
        for line in script:
            for check, rep in zip(checkWords, repWords):
                line = line.replace(check, rep)
            ofile.write(line)
        ofile.close()
