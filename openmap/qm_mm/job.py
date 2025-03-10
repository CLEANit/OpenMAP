# save job in h5 file
import os
from pathlib import Path

import h5py
import numpy as np

from openmap.util import files
from openmap.util.log import logger

__all__ = ["JobManager", "JobProfile"]


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
    @logger.catch
    def make_workdir(self):
        # os.makedirs(local_file_directory, exist_ok=True)
        Path(self.local_path).mkdir(parents=True, exist_ok=True)

    @logger.catch
    def upload_files_to_remote(self, remote):
        """
        Upload files to remote via SCP.
        """
        local_files = files.fetch_local_files(self.local_path)
        remote.bulk_upload(local_files)

    @logger.catch
    def upload_dir_to_remote(self, remote, job):
        """
        Upload directory to remote via SCP.
        """
        self.make_dir_on_remote(remote)  # make remote dir if not exist

        # for job in job_list:

        if not os.path.isdir(os.path.join(self.local_path, job)):
            print(
                f'The file {os.path.join(self.local_path, job)} does not exist')
            pass
        remote.dir_upload(os.path.join(self.local_path, job),
                          remote_path=os.path.join(self.remote_path, job))

    @logger.catch
    def download_file_from_remote(self, remote, job):
        """
        download directory  via SCP.
        """
        # for job in job_list:
        copy_dir = os.path.join(self.remote_path, job, 'vasp_output.tar.gz')
        dest_dir = os.path.join(self.local_path, job)
        remote.download_file(copy_dir, local_directory=dest_dir)

    @logger.catch
    def make_dir_on_remote(self, remote):
        """
        Create a Directory on Remote,
        if it not exit
        """
        remote.mkdir_p(os.path.join(self.remote_path))

    @logger.catch
    def run_job(self, remote, job):
        """
        Execute UNIX command on the remote host.
        """
        jobs = {}
        job_ids = []

        # for jobb in job_list:
        job_id = remote.sbatch(os.path.join(
            self.remote_path, job), job_file=job + '_vasp_job.sh')
        # job_ids.append(job_id)
        jobs = {
            'id': job_id,
            'name': job,
            'remote_path': os.path.join(self.remote_path, job),
            'local_path': os.path.join(self.local_path, job),
        }

        return jobs

    # def job_monitoring(self, remote, jobs):
    #     remote.monitor_batch(jobs)

    @logger.catch
    def write_slurm_vm(self, script, input_path, checkWords, repWords):
        """
        write python file to upload results on the virtual machine
        :param script: template
        :param input_path:
        :param checkWords:
        :param repWords:
        :return:
        """

        if not os.path.isdir(input_path):
            raise Exception(
                'The directory {} does not exist'.format(input_path))

        basename = os.path.basename(os.path.normpath(input_path))

        outputfile = os.path.join(input_path, basename + '_vm.py')

        jobname = basename
        ofile = open(outputfile, 'w')
        for line in script:
            for check, rep in zip(checkWords, repWords):
                line = line.replace(check, rep)
            ofile.write(line)
        ofile.close()

    @logger.catch
    def save_dict_to_hdf5(self, dic, filename):
        """
        'a' Read/write if exists, create otherwise
        ....
        """

        with h5py.File(filename, 'a') as h5file:
            self._recursively_save_dict_contents_to_group(h5file, '/', dic)

    @logger.catch
    def _recursively_save_dict_contents_to_group(self, h5file, path, dic):
        """
        ....
        """
        for key, item in dic.items():
            if isinstance(item, (int, float, np.ndarray, np.int64, np.float64, np.int32, np.float32, str, bytes)):
                h5file[path + key] = item
            elif isinstance(item, dict):
                self._recursively_save_dict_contents_to_group(
                    h5file, path + key + '/', item)
            else:
                raise ValueError('Cannot save %s type' % type(item))

    @logger.catch
    def load_dict_from_hdf5(self, filename):
        """
        ....
        """
        with h5py.File(filename, 'r') as h5file:
            return self._recursively_load_dict_contents_from_group(h5file, '/')

    @logger.catch
    def _recursively_load_dict_contents_from_group(self, h5file, path):
        """
        ....
        """
        ans = {}
        for key, item in h5file[path].items():
            if isinstance(item, h5py._hl.dataset.Dataset):
                ans[key] = item[()]  # item.value
            elif isinstance(item, h5py._hl.group.Group):
                ans[key] = self._recursively_load_dict_contents_from_group(
                    h5file, path + key + '/')
        return ans
