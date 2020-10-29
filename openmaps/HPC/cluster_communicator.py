import paramiko
from paramiko import SSHClient, SFTPClient
import os, re
import time
from copy import copy
# from input_utils import QuantumChemOutputParser
import subprocess
import numpy as np


class Partition(object):

    def __init__(self, name, maxDays):
        self.name = name
        self.maxDays = maxDays


class ClusterCommunicator(object):
    def __init__(self, hostname, username, password):
        #self.partition = self.Partition()
        self.client = SSHClient()
        #self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        successful = False
        while not successful:
            try:
                self.client.connect(hostname=hostname, username=username, password=password)
            except TimeoutError as e:
                print('Timeout.. trying again.')
                # self.client.connect(hostname = hostname, username = username, password = password)
                continue
            successful = True



    def _run_cmd(self, command):
        _, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()

    def get_partition_info(self):

        # create list of partition using sinfo -o "%R %l"
        #pattern = r"%d+"

        command = 'sinfo -o "%R %l"'
        #std_out, _ = self._run_cmd(command)
        #info = std_out.readlines()[1:]
        _, stdout, stderr = self.client.exec_command(command)
        print(stdout)
        info = stdout.readlines()[1:]
        partitions = []

        for line in info:
            if len(line.strip()) == 0:
                continue
            partition_name = line.split()[0]
            # if "gpu" in partition_name:
            #    continue
            partition_time = int(re.findall(r"\d+", line)[0])
            partitions.append(Partition(partition_name, partition_time))

        return partitions

    def sbatch(self, calc_dir, joblist_file, output_dir):
        std_out, _ = self._run_cmd(f'cd {calc_dir}; sbatch parallel_cheap_protocol.sh {joblist_file} {output_dir}')
        job_id = std_out.split(' ')[-1]
        print(std_out, _)
        print(job_id)
        job_id = int(std_out.split(' ')[-1])
        return job_id

    def sacct(self, job_id):
        std_out, _ = self._run_cmd(f'sacct -j {job_id} -b')
        std_out = std_out.split('\n')
        status = re.sub(' +', ' ', std_out[2]).split(' ')
        if len(status) <= 1:
            return 'PENDING'
        return status[1]

    def monitor(self, job_id):
        status = None
        while status not in ['COMPLETED']:
            status = self.sacct(job_id)
            print(status)
            time.sleep(5)
        return None

    def monitor_batch(self, job_ids):
        status_list = [None for job_sid in job_ids]
        while not all(status == 'COMPLETED' for status in status_list):
            status_list = [self.sacct(job_id) for job_id in job_ids]
            print(status_list)
            time.sleep(5)
        return None

    def copy_joblist(self, joblist_file, calc_dir):
        successful = False
        while not successful:
            try:
                subprocess.call(f'scp {joblist_file} ctetsass@cedar.computecanada.ca:{calc_dir}', shell=True)
            except TimeoutError as e:
                print('Timeout.. trying again.')
                # self.client.connect(hostname = hostname, username = username, password = password)
                continue
            successful = True

    def collect_results(self, calc_dir, output_dir, uuid, results_dir):
        std_out, _ = self._run_cmd(
            f'cd {calc_dir}; mkdir results; for i in output_*; do mkdir results/{uuid}_$i; cp $i/abs_0_1.npz $i/fluo_1_0.npz results/{uuid}_$i; done')
        print(std_out)

    def copy_results(self, results_dir, calc_dir, output_path):
        print('Im starting to copy...')
        successful = False
        while not successful:
            try:
                subprocess.call(f'scp -r ctetsass@cedar.computecanada.ca:{calc_dir}/results {output_path}', shell=True)
            except TimeoutError as e:
                print('Timeout.. trying again.')
                # self.client.connect(hostname = hostname, username = username, password = password)
                continue
            successful = True

    def prepare_results(self, uuid, batch_size):
        """ get all of the results of the previous batch ready to be inserted into the DB
            will return a list of dictionaries
        """
        results = []
        for i in range(batch_size):
            fluo = np.load(f'measurements/results/{uuid}_output_{i + 1}/fluo_1_0.npz')
            abs_ = np.load(f'measurements/results/{uuid}_output_{i + 1}/abs_0_1.npz')
            abs_dict = {}
            for key in abs_.files:
                abs_dict[key] = np.nan_to_num(abs_[key])
            fluo_dict = {}
            for key in fluo.files:
                fluo_dict[key] = np.nan_to_num(fluo[key])
            mol_dict = {'abs': abs_dict, 'fluo': fluo_dict}
            results.append(mol_dict)

        return results

    def get_objective(self, uuid, batch_size):
        objectives = []
        for i in range(batch_size):
            data = np.load(f'measurements/results/{uuid}_output_{i + 1}/abs_0_1.npz')
            objective = float(data['peak_w'])  # what will be our objective??
            objectives.append(objective)
        return objectives

    def cleanup(self, calc_dir):
        successful = False
        while not successful:
            try:
                std_out, _ = self._run_cmd(f'cd {calc_dir}; rm -r slurm-* output_* joblist results')
            except TimeoutError as e:
                print('Timeout.. trying again.')
                # self.client.connect(hostname = hostname, username = username, password = password)
                continue
            successful = True
        print(std_out)
