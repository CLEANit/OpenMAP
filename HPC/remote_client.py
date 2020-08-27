#!/usr/bin/env python
import os
import glob
import pathlib
import sys
import getpass
import paramiko
import re

from cluster_communicator import ClusterCommunicator

# if sys.stdin.isatty():
#    p = getpass.getpass('Using getpass: ')
# else:
#    print('Using readline')
#    p = sys.stdin.readline().rstrip()

# print('Read: ', p)

# ================================================
hostname = 'cedar.computecanada.ca'  # sys.argv[1]
account = 'rrg-mkarttu-ab'
username = 'ctetsass'  # sys.argv[2]
password = 'Gastipard_Isaro'  # getpass.getpass()
# ================================================
project_name = 'Alloys'
Work_dir = '/Users/ctetsass/Calculation_NRC/OpenMAPs'
Job_dir = os.path.join(Work_dir, 'HPC_Job', project_name)


# email =  # os.environ.get("ISCF_EMAIL")
# ================================================

# cluster = ClusterCommunicator(hostname=hostname, username=username, password=password)

# class Partition(object):
#
#     def __init__(self, name, maxDays):
#         self.name = name
#         self.maxDays = maxDays
#
# def get_partition_info(hostname, username, password):
#     client = paramiko.SSHClient()
#     client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
#     client.connect(hostname=hostname, username=username, password=password)
#
#     # create list of partition using sinfo -o "%R %l"
#     pattern = r"%d+"
#
#     command = 'sinfo -o "%R %l"'
#     _, stdout, stderr = client.exec_command(command)
#     info = stdout.readlines()[1:]
#     stdout.close()
#     stderr.close()
#     client.close()
#
#     partitions = []
#
#     for line in info:
#         if len(line.strip()) == 0:
#             continue
#         partition_name = line.split()[0]
#         # if "gpu" in partition_name:
#         #    continue
#         partition_time = int(re.findall(r"\d+", line)[0])
#         partitions.append(Partition(partition_name, partition_time))
#
#     return partitions


def mkdir_p(sftp, remote_directory):
    """
    Change to this directory, recursively making new folders if needed.
    Returns True if any folders were created.
    """
    if remote_directory == '/':
        # absolute path so change directory to root
        sftp.chdir('/')
        return
    if remote_directory == '':
        # top-level relative directory must exist
        return
    try:
        sftp.chdir(remote_directory)  # sub-directory exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        mkdir_p(sftp, dirname)  # make parent directories
        sftp.mkdir(basename)  # sub-directory missing, so created it
        sftp.chdir(basename)
        return True


def copyToServer(sftp, destPath, localPath):
    try:
        sftp.put(localPath, destPath)
        sftp.close()
        transport.close()
        print(" SUCCESS !!!! Files moved to {} ".format(hostname))
        return True

    except Exception as e:
        try:
            filestat = sftp.stat(destPath)
            destPathExists = True
        except Exception as e:
            destPathExists = False

        print(destPathExists)
        if not destPathExists:
            mkdir_p(sftp, destPath)
            sftp.put(localPath, destPath)
            sftp.close()
            transport.close()
            print(" %s    FAILED    -    copying failed because directory on remote machine doesn't exist" % hostname)
            # log.write("%s    FAILED    -    copying failed    directory at remote machine doesn't exist\r\n" % hostname)
        else:
            print(" {}    FAILED    -    copying failed".format(hostname))
            # log.write("%s    FAILED    -    copying failed\r\n" % hostname)
        return False


class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        """
        Uploads the contents of the source directory to the target path.
        The target directory needs to exists.
        All subdirectories in source are created under target.
        """
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), "{}/{}".format(target, item))
            else:
                self.mkdir("{}/{}".format(target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), "{}/{}".format(target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        """
        Augments mkdir by adding an option to not fail if the folder exists
        """
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise


# command = 'sinfo -o "%R %l"'
# _, stdout, stderr = client.exec_command(command)
# info = stdout.readlines()[1:]
# infos = stdout.read().decode()
# print(info)
# print(infos)

id = 1
job_name = project_name + "_{:05d}".format(id)

#destPath = "$SCRATCH/OpenMAPs/{}".format(project_name)
destPath = os.path.join('/home/ctetsass/scratch/OpenMaps', project_name)
#destPath = '$SCRATCH/OpenMaps'


localPath = os.path.join(Job_dir, job_name, 'Alloys_00001.zip')

# client = paramiko.SSHClient()
# client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
# client.connect(hostname=hostname, username=username, password=password)
# client.close()


transport = paramiko.Transport((hostname, 22))
transport.connect(username=username, password=password)

sftp = paramiko.SFTPClient.from_transport(transport)


copyToServer(sftp, destPath, localPath)

#mkdir_p(sftp,destPath)
#Mysftp = MySFTPClient.from_transport(transport)
#Mysftp.mkdir(destPath, ignore_existing=True)
#Mysftp.put_dir(localPath, destPath)
#Mysftp.close()

# sftp = paramiko.SFTPClient.from_transport(transport)
# mkdir_p(sftp, remote_path)
# sftp.put(local_path, '.')    # At this point, you are in remote_path
# sftp.close()


# partitions = cluster.get_partition_info()

# print(partitions[-1].maxDays)

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
