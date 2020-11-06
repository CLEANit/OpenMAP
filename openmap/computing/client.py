#!/usr/bin/env python

__version__ = '0.1'
__author__ = 'Conrard TETSASSI'
__maintainer__ = 'Conrard TETSASSI'
__email__ = 'ConrardGiresse.TetsassiFeugmo@nrc-cnrc.gc.ca'
__status__ = 'Development'

"""Client to handle connections and actions executed against a remote host."""
import os
import re
import sys
import time
from os import system

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException

from .files import fetch_local_files
from .log import logger


def progress4(filename, size, sent, peername):
    sys.stdout.write("({}:{}) {}\'s progress: {:.2f}% \r".format(peername[0], peername[1],
                                                                 filename, float(sent) / float(size) * 100))


class Partition(object):

    def __init__(self, name, maxDays):
        self.name = name
        self.maxDays = maxDays


def countdown(sleeptime):
    for remaining in range(sleeptime, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write("{:4d} seconds remaining before next refresh.".format(remaining))
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\n")


class RemoteClient:
    """Client to interact with a remote host via SSH & SCP."""

    def __init__(self, host, user, remote_path, local_path, passphrase=None, ssh_key_filepath=None):
        self.host = host
        self.user = user
        self.ssh_key_filepath = ssh_key_filepath
        self.remote_path = remote_path
        self.local_path = local_path
        self.passphrase = passphrase
        self.client = None
        self.scp = None
        self.sftp = None
        self.conn = None
        self._upload_ssh_key()

    @logger.catch
    def _get_ssh_key(self):
        """ Fetch locally stored SSH key."""
        try:
            self.ssh_key = RSAKey.from_private_key_file(self.ssh_key_filepath)
            logger.info(f'Found SSH key at self {self.ssh_key_filepath}')
        except SSHException as error:
            logger.error(error)
        return self.ssh_key

    @logger.catch
    def _upload_ssh_key(self):
        """
        Function to be run automatically whenever our client is instantiated.
        Deliver this public key to our remote host
        if   _get_ssh_key is successful
        """
        try:
            system(f'ssh-copy-id -i {self.ssh_key_filepath} {self.user}@{self.host}>/dev/null 2>&1')
            system(f'ssh-copy-id -i {self.ssh_key_filepath}.pub {self.user}@{self.host}>/dev/null 2>&1')
            logger.info(f'{self.ssh_key_filepath} uploaded to {self.host}')
        except FileNotFoundError as error:
            logger.error(error)

    @logger.catch
    def _connect(self):
        """Open connection to remote host. """
        if self.conn is None:
            try:
                self.client = SSHClient()
                self.client.load_system_host_keys()
                self.client.set_missing_host_key_policy(AutoAddPolicy())
                # self.client.connect(hostname=ip, username=user, password=password, timeout=tout,\
                #                     compress = True,look_for_keys=False, allow_agent=False)

                if self.passphrase is None:
                    self.client.connect(
                        self.host,
                        username=self.user,
                        # key_filename=self.ssh_key_filepath,
                        # look_for_keys=True  # ,
                        # password=self.passphrase  # ,
                        # timeout=5000
                    )

                else:
                    self.client.connect(
                        self.host,
                        username=self.user,
                        # key_filename=self.ssh_key_filepath,
                        look_for_keys=False,
                        password=self.passphrase  # ,
                        # timeout=5000
                    )
                self.sftp = self.client.open_sftp()
                # if not self.client.get_transport().active:
                # self.scp = SCPClient(self.client.get_transport(), progress4=progress4)
                self.scp = SCPClient(self.client.get_transport())

                logger.info(f'Connection established to {self.host}')
            except AuthenticationException as error:
                logger.error(f'Authentication failed: did you remember to create an SSH key? {error}')
                raise error
            except TimeoutError as e:
                logger.error(f'Timeout.. trying again.')
                # continue
        return self.client

    def disconnect(self):
        """Close ssh connection."""
        if self.client:
            self.client.close()
        if self.scp:
            self.scp.close()

    @logger.catch
    def dir_upload(self, dir, remote_path=None):
        """
        Upload a directory to a remote directory.
        """
        # upload = None
        # if '*' in dir:
        #   listing = glob.glob(dir)
        local_files = fetch_local_files(dir)
        if len(local_files) == 0:
            raise Exception("No file found: " + dir)

        self.conn = self._connect()
        if remote_path is None:
            remote_path = self.remote_path

        try:
            self.scp.put(
                dir,
                recursive=True,
                remote_path=remote_path
            )
            # upload = dir
        except SCPException as error:
            logger.error(error)
            raise error
        finally:
            logger.info(f' [{os.path.basename(dir)}] uploaded to {self.host}')
            # return upload

    @logger.catch
    def bulk_upload(self, files):
        """
        Upload multiple files to a remote directory.

        :param files: List of paths to local files.
        :type files: List[str]
        """
        self.conn = self._connect()
        uploads = [self._upload_single_file(file) for file in files]
        logger.info(f'All the {len(uploads)}  files  uploaded to {self.host} +++')

    def _upload_single_file(self, file):
        """Upload a single file to a remote directory."""
        upload = None
        try:
            self.scp.put(
                file,
                recursive=True,
                remote_path=self.remote_path
            )
            upload = file
        except SCPException as error:
            logger.error(error)
            raise error
        finally:
            logger.info(f'[{file}]  uploaded to  {self.host} ')
            return upload

    @logger.catch
    def bulk_download(self, files, dest):
        """
        Download  multiples files from a remote directory.
        :param files: A list with the source files in the remote server.
        :type files: List[str]
        :param dest: local destination paths to copy
        :type dest: str
        """
        self.conn = self._connect()
        download = [self.scp.get(file0, dest0) for file0, dest0 in files]
        logger.info(f' {len(download)} downloaded from {os.path.basename(self.local_path)}')

    @logger.catch
    def download_file(self, file, local_directory=None):
        """Download file from remote host."""
        self.conn = self._connect()
        if local_directory is None:
            local_directory = self.local_directory
        self.scp.get(file, local_directory, recursive=True)
        logger.info(f'[{file}] downloaded  from {self.host}')

    @logger.catch
    def execute_commands(self, commands):
        """
        Execute multiple commands in succession.

        :param commands: List of unix commands as strings.
        :type commands: List[str]
        """
        self.conn = self._connect()
        for cmd in commands:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            stdout.channel.recv_exit_status()
            response = stdout.readlines()
            for line in response:
                logger.info(f'INPUT: {cmd} | OUTPUT: {line}')

    def check_remote_dir(self, remote_directory):
        """
        check if remote dir exit (on server)"
        """
        self.conn = self._connect()
        # status = False
        try:
            self.sftp.chdir(remote_directory)  # sub-directory exists
            status = True
        except IOError:
            status = False
        return status

    def check_remote_file(self, remote_file):
        """
        check if remote file exit (on server)"
        """
        self.conn = self._connect()
        # status = False
        try:
            self.stat(remote_file)
            print('file exists')
            status = True
        except IOError:
            status = False
        return status

    @logger.catch
    def mkdir_p(self, remote_directory):
        """
        Change to this directory, recursively making new folders if needed.
        Returns True if any folders were created.
        """
        self.conn = self._connect()

        if remote_directory == '/':
            # absolute path so change directory to root
            self.sftp.chdir('/')
            return
        if remote_directory == '':
            # top-level relative directory must exist
            return
        try:
            self.sftp.chdir(remote_directory)  # sub-directory exists
        except IOError:
            dirname, basename = os.path.split(remote_directory.rstrip('/'))
            self.mkdir_p(dirname)  # make parent directories
            self.sftp.mkdir(basename)  # sub-directory missing, so created it
            self.sftp.chdir(basename)
            logger.info(f'Successfully   created  dir [{basename}]   on {self.host} ')
            return True

    @logger.catch
    def execute_command(self, command):
        """
        Execute single commands in succession.
        :param command: unix commands as strings.
        :type command: str
        """
        self.conn = self._connect()
        _, stdout, stderr = self.client.exec_command(command)
        # stdout.channel.recv_exit_status()
        # response = stdout.readlines()
        # for line in response:
        # logger.info(f'INPUT: {command} | OUTPUT: {line}')
        logger.info(f'execute_cmd: {command} ')
        return stdout.read().decode(), stderr.read().decode()

    def get_partition_info(self):
        """
        Get  partition name and max day
        :return: List of Partition method
        """

        command = 'sinfo -o "%R %l"'
        stdout, _ = self.client.exec_command(command)
        stdout.channel.recv_exit_status()
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

    @logger.catch
    def sbatch(self, job_directory, job_file='vasp_job.sh'):
        std_out, _ = self.execute_command(f'cd {job_directory}; sbatch {job_file}')
        # print(std_out, _)
        logger.info(f'{std_out}')
        job_id = std_out.split(' ')[-1]
        # print(job_id)

        return int(job_id)

    def sacct(self, job_id):
        """

               JobID      State ExitCode
        ------------ ---------- --------
        54071355        PENDING      0:0

        :param job_id:
        :return:
        """
        std_out, _ = self.execute_command(f'sacct -j {job_id} -b')
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
            time.sleep(300)
        return None

    @logger.catch
    def monitor_batch(self, jobs):
        """
        :param jobs: list of dictionary with job information
        :return:
        """
        status_list = [None for job in jobs]
        while not all(status == 'COMPLETED' for status in status_list):
            status_list = [self.sacct(job["id"]) for job in jobs]
            job_ids = [job["id"] for job in jobs]
            for id, status in zip(job_ids, status_list):
                logger.info(f' {id}:  {status}')
            #
            if all(status == 'COMPLETED' for status in status_list):
                logger.info(f'All Jobs COMPLETED')
                continue
            else:
                sleeptime = 120
                countdown(sleeptime)
        for job in jobs:
            if not self.check_remote_dir(job["remote_path"]):
                print(f'The file {job["remote_path"]} does not exist')
                continue
            self.download_file(job["remote_path"] + '/' + job["output"], local_directory=job["local_path"])
            self.clean_dir(job["remote_path"])
            logger.info(f'Job:  {job["name"]}  Cleaned on {self.host}')
        # for job in jobs:
        #    self.clean_dir(job.remote_path)
        #    logger.info(f'file: {job.name}  Cleaned on {self.host}')
        logger.info(f'Task completed')
        return None

    @logger.catch
    def start(self, user=None):
        if user is None:
            user = self.user
        std_out, _ = self.execute_command(f'squeue --start -u  {user} ')
        return std_out

    @logger.catch
    def clean_file(self, file):
        std_out, _ = self.execute_command(f'rm -f {file} ')
        logger.info(f'file: {file}  Cleaned')
        return None

    @logger.catch
    def clean_dir(self, file):
        std_out, _ = self.execute_command(f'rm -rf {file} ')
        # logger.info(f'file: {file}  Cleaned')
        return None

    @logger.catch
    def seff(self, job_id):
        """
        :param job_id:
        :return:  dictionary

        [rdb9@farnam1 ~]$ seff 21294645
        Job ID: 21294645
        Cluster: farnam
        User/Group: rdb9/lsprog
        State: COMPLETED (exit code 0)
        Cores: 1
        CPU Utilized: 00:15:55
        CPU Efficiency: 17.04% of 01:33:23 analysis-walltime
        Job Wall-clock time: 01:33:23
        Memory Utilized: 446.20 MB
        Memory Efficiency: 8.71% of 5.00 GiB
        """

        std_out, _ = self.execute_command(f'seff  {job_id} ')
        std_out = std_out.split('\n')

        output = None
        return output

    @logger.catch
    def run_on_group_allocation(self):
        # Running jobs in the group allocation
        # srun -p groupid
        # sbatch -p groupid
        return None

    # Check utilization of group allocation
    # sacct

    def kill(self, job_id):
        # Kill a job with ID $PID
        try:
            self.execute_command(f'scancel {job_id} ')
        except Exception as e:
            logger.error(f'{e}')

    def kill_all(self, user=None):
        # Kill a job with ID $PID
        if user is None:
            user = self.user
        try:
            self.execute_command(f'scancel -u {user} ')
        except Exception as e:
            logger.error(f'{e}')

    def kill_pending(self, user=None):
        # Kill all pending jobs
        if user is None:
            user = self.user
        try:
            self.execute_command(f'scancel -u {user} --state=pending')
        except Exception as e:
            logger.error(f'{e}')

    def count_job_user(self, user=None):
        # Count number of running / in queue jobs
        if user is None:
            user = self.user
        try:
            std_out, _ = self.execute_command(f'squeue -u {user} | wc -l')
            return std_out
        except Exception as e:
            logger.error(f'{e}')

    def count_pending(self):
        # Count number of  jobs pending

        try:
            std_out, _ = self.execute_command(f'squeue --state=pending | wc -l')
            return std_out
        except Exception as e:
            logger.error(f'{e}')

    def count_pending_user(self, user=None):
        # Count number of  jobs pending
        if user is None:
            user = self.user
        try:
            std_out, _ = self.execute_command(f'squeue -u {user} --state=pending | wc -l')
            return std_out
        except Exception as e:
            logger.error(f'{e}')


